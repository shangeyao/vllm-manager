"""
ModelScope 客户端实现
统一使用 ModelScope SDK 获取模型信息
"""

import asyncio
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from .base import ModelSourceClient, ModelInfo, ModelSpec, ModelType
from .utils import (
    infer_model_family,
    infer_model_type_from_tags,
    infer_abilities,
    infer_languages,
    infer_model_size,
    infer_context_length,
    normalize_model_name,
    extract_model_id_from_full_id,
)


class ModelScopeClient(ModelSourceClient):
    """ModelScope 模型源客户端"""

    # 默认热门组织列表
    DEFAULT_ORGANIZATIONS = [
        "qwen",  # 通义千问
        "LLM-Research",  # Meta Llama 等
        "ZhipuAI",  # 智谱 AI
        "baichuan-inc",  # 百川
        "deepseek-ai",  # DeepSeek
        "OpenBMB",  # 面壁智能
        "BAAI",  # 智源研究院
        "01-ai",  # 零一万物
        "internlm",  # 书生浦语
        "OpenGVLab",  # 上海 AI Lab
        "modelscope",  # ModelScope 官方
        "AI-ModelScope",  # AI ModelScope
    ]

    def __init__(self):
        super().__init__("modelscope")
        self._api = None
        self._executor = ThreadPoolExecutor(max_workers=5)
        self._session = None

    def _get_api(self):
        """延迟初始化 HubApi"""
        if self._api is None:
            try:
                from modelscope.hub.api import HubApi
                self._api = HubApi()
            except ImportError:
                raise ImportError(
                    "modelscope SDK not installed. "
                    "Install it with: pip install modelscope"
                )
        return self._api

    def _get_session(self):
        """延迟初始化 requests session (用于 HTTP API)"""
        if self._session is None:
            import requests
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "vLLM-UI/1.0",
                "Accept": "application/json"
            })
        return self._session

    def _convert_to_model_info(self, raw_model: Dict[str, Any]) -> Optional[ModelInfo]:
        """将原始模型数据转换为统一的 ModelInfo"""
        # ModelScope API 返回的字段可能是 'Name' 或 'ModelId'
        model_id = raw_model.get("Name") or raw_model.get("ModelId", "")
        if not model_id:
            return None

        name = extract_model_id_from_full_id(model_id)
        tags = raw_model.get("Tags", [])
        architectures = raw_model.get("Architectures", [])

        # 推断模型类型
        model_type_str = infer_model_type_from_tags(tags, architectures)
        model_type = ModelType(model_type_str)

        # 获取描述
        description = raw_model.get("Description", "")
        chinese_name = raw_model.get("ChineseName", "")
        if not description and chinese_name:
            description = chinese_name
        if not description:
            description = f"{name} model from ModelScope"

        # 创建 ModelSpec
        spec = ModelSpec(
            model_format="pytorch",
            model_size_in_billions=infer_model_size(name),
            quantizations=["none", "4-bit", "8-bit"],
            model_id=model_id,
            model_hub="modelscope",
            architectures=architectures,
        )

        return ModelInfo(
            model_id=model_id,
            model_name=normalize_model_name(name),
            model_description=description,
            model_type=model_type,
            model_family=infer_model_family(name),
            languages=infer_languages(name, tags),
            abilities=infer_abilities(name, tags, model_type_str),
            context_length=infer_context_length(name),
            specs=[spec],
            tags=tags,
            downloads=raw_model.get("Downloads", 0),
            likes=raw_model.get("Likes", 0),
            source="modelscope",
        )

    async def get_models_by_organization(
        self, organization: str, page_size: int = 50
    ) -> List[ModelInfo]:
        """获取指定组织的模型列表"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor,
                lambda: self._get_api().list_models(
                    owner_or_group=organization, page_size=page_size
                ),
            )

            models = result.get("Models", [])
            model_infos = []
            for model in models:
                info = self._convert_to_model_info(model)
                if info:
                    model_infos.append(info)
            return model_infos

        except Exception as e:
            print(f"Error fetching models from {organization}: {e}")
            return []

    async def get_popular_models(self, limit: int = 100) -> List[ModelInfo]:
        """获取热门模型列表"""
        # 并发获取所有组织的模型
        tasks = [
            self.get_models_by_organization(org, page_size=50)
            for org in self.DEFAULT_ORGANIZATIONS
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_models = []
        seen_ids = set()

        for org, models in zip(self.DEFAULT_ORGANIZATIONS, results):
            if isinstance(models, Exception):
                print(f"Error fetching from {org}: {models}")
                continue

            for model in models:
                if model.model_id not in seen_ids:
                    seen_ids.add(model.model_id)
                    all_models.append(model)

        return all_models[:limit]

    async def search_models(
        self,
        query: str = "",
        model_type: Optional[ModelType] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> List[ModelInfo]:
        """搜索模型 - 使用 HTTP API"""
        url = "https://www.modelscope.cn/api/v1/models"

        params = {
            "Search": query,
            "Page": page,
            "PageSize": per_page,
        }

        if model_type:
            params["Type"] = model_type.value

        try:
            import requests
            response = self._get_session().get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("Success"):
                models = data.get("Data", {}).get("Models", [])
                model_infos = []
                for model in models:
                    info = self._convert_to_model_info(model)
                    if info:
                        # 标签过滤
                        if tags and not any(t in info.tags for t in tags):
                            continue
                        model_infos.append(info)
                return model_infos
            return []

        except Exception as e:
            print(f"Error searching models from ModelScope: {e}")
            return []

    async def get_model_detail(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型详细信息"""
        url = f"https://www.modelscope.cn/api/v1/models/{model_id}"

        try:
            import requests
            response = self._get_session().get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("Success"):
                return self._convert_to_model_info(data.get("Data", {}))
            return None

        except Exception as e:
            print(f"Error fetching model detail from ModelScope: {e}")
            return None


# 全局实例
modelscope_client = ModelScopeClient()
