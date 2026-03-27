"""
Hugging Face 客户端实现
"""

import requests
from typing import List, Optional, Dict, Any

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


class HuggingFaceClient(ModelSourceClient):
    """Hugging Face 模型源客户端"""

    BASE_URL = "https://huggingface.co/api"

    # 常见的 LLM 关键词
    LLM_KEYWORDS = [
        "chat",
        "instruct",
        "llama",
        "qwen",
        "glm",
        "baichuan",
        "mistral",
        "mixtral",
        "deepseek",
        "yi",
        "gemma",
        "phi",
        "qwen2",
        "qwen3",
        "llama-3",
        "llama-2",
    ]

    def __init__(self):
        super().__init__("huggingface")
        self._session = None

    def _get_session(self):
        """延迟初始化 requests session"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "vLLM-UI/1.0",
                "Accept": "application/json"
            })
        return self._session

    def _convert_to_model_info(self, raw_model: Dict[str, Any]) -> Optional[ModelInfo]:
        """将 Hugging Face 原始数据转换为统一的 ModelInfo"""
        model_id = raw_model.get("id", "")
        if not model_id:
            return None

        name = extract_model_id_from_full_id(model_id)
        tags = raw_model.get("tags", [])
        pipeline_tag = raw_model.get("pipeline_tag", "")

        # 推断模型类型
        model_type_str = infer_model_type_from_tags(tags)
        if pipeline_tag in ["text-generation", "text2text-generation"]:
            model_type_str = "llm"
        model_type = ModelType(model_type_str)

        # 创建 ModelSpec
        spec = ModelSpec(
            model_format="pytorch",
            model_size_in_billions=infer_model_size(name),
            quantizations=["none", "4-bit", "8-bit"],
            model_id=model_id,
            model_hub="huggingface",
        )

        return ModelInfo(
            model_id=model_id,
            model_name=normalize_model_name(name),
            model_description=raw_model.get("description", f"{name} model from Hugging Face"),
            model_type=model_type,
            model_family=infer_model_family(name),
            languages=infer_languages(name, tags),
            abilities=infer_abilities(name, tags, model_type_str),
            context_length=infer_context_length(name),
            specs=[spec],
            tags=tags,
            downloads=raw_model.get("downloads", 0),
            likes=raw_model.get("likes", 0),
            source="huggingface",
        )

    async def search_models(
        self,
        query: str = "",
        model_type: Optional[ModelType] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> List[ModelInfo]:
        """搜索 Hugging Face 模型"""
        url = f"{self.BASE_URL}/models"

        params = {
            "search": query,
            "limit": per_page,
            "sort": "downloads",
            "direction": "-1",
        }

        if model_type == ModelType.LLM:
            params["filter"] = "text-generation"

        try:
            response = self._get_session().get(url, params=params, timeout=30)
            response.raise_for_status()
            models = response.json()

            model_infos = []
            for model in models:
                info = self._convert_to_model_info(model)
                if info:
                    # 标签过滤
                    if tags and not any(t in info.tags for t in tags):
                        continue
                    model_infos.append(info)
            return model_infos

        except Exception as e:
            print(f"Error fetching models from Hugging Face: {e}")
            return []

    async def get_model_detail(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型详细信息"""
        url = f"{self.BASE_URL}/models/{model_id}"

        try:
            response = self._get_session().get(url, timeout=30)
            response.raise_for_status()
            return self._convert_to_model_info(response.json())

        except Exception as e:
            print(f"Error fetching model detail from Hugging Face: {e}")
            return None

    async def get_popular_models(self, limit: int = 100) -> List[ModelInfo]:
        """获取热门 LLM 模型列表"""
        models = []
        seen_ids = set()

        for keyword in self.LLM_KEYWORDS:
            try:
                results = await self.search_models(query=keyword, limit=20)
                for model in results:
                    if model.model_id not in seen_ids:
                        seen_ids.add(model.model_id)
                        models.append(model)

                if len(models) >= limit:
                    break
            except Exception as e:
                print(f"Error searching keyword '{keyword}': {e}")
                continue

        return models[:limit]

    async def get_models_by_organization(
        self, organization: str, page_size: int = 50
    ) -> List[ModelInfo]:
        """获取指定组织的模型列表"""
        # Hugging Face 可以通过 author 参数过滤
        url = f"{self.BASE_URL}/models"
        params = {
            "author": organization,
            "limit": page_size,
            "sort": "downloads",
        }

        try:
            response = self._get_session().get(url, params=params, timeout=30)
            response.raise_for_status()
            models = response.json()

            model_infos = []
            for model in models:
                info = self._convert_to_model_info(model)
                if info:
                    model_infos.append(info)
            return model_infos

        except Exception as e:
            print(f"Error fetching models from organization {organization}: {e}")
            return []


# 全局实例
hf_client = HuggingFaceClient()
