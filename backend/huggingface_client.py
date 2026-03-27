"""
Hugging Face API 客户端
用于从 Hugging Face 获取模型列表
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HFModel:
    """Hugging Face 模型信息"""
    model_id: str
    name: str
    description: str
    model_type: str
    tags: List[str]
    downloads: int
    likes: int


class HuggingFaceClient:
    """Hugging Face API 客户端"""
    
    BASE_URL = "https://huggingface.co/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "vLLM-UI/1.0",
            "Accept": "application/json"
        })
    
    def search_models(
        self,
        query: str = "",
        limit: int = 50,
        sort: str = "downloads",
        direction: str = "-1"
    ) -> List[Dict[str, Any]]:
        """
        搜索 Hugging Face 模型
        
        Args:
            query: 搜索关键词
            limit: 返回数量限制
            sort: 排序方式
            direction: 排序方向
        
        Returns:
            模型列表
        """
        url = f"{self.BASE_URL}/models"
        
        params = {
            "search": query,
            "limit": limit,
            "sort": sort,
            "direction": direction,
            "filter": "text-generation",  # 只获取文本生成模型
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching models from Hugging Face: {e}")
            return []
    
    def get_popular_llm_models(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取热门 LLM 模型列表
        
        Args:
            limit: 返回数量限制
        
        Returns:
            热门 LLM 模型列表
        """
        # 搜索 LLM 相关模型
        models = []
        seen_ids = set()
        
        # 常见的 LLM 关键词
        keywords = [
            "chat", "instruct", "llama", "qwen", "glm", "baichuan",
            "mistral", "mixtral", "deepseek", "yi", "gemma", "phi",
            "qwen2", "qwen3", "llama-3", "llama-2"
        ]
        
        for keyword in keywords:
            try:
                results = self.search_models(query=keyword, limit=20)
                for model in results:
                    model_id = model.get("id", "")
                    if model_id and model_id not in seen_ids:
                        seen_ids.add(model_id)
                        models.append(model)
                
                if len(models) >= limit:
                    break
            except Exception as e:
                print(f"Error searching keyword '{keyword}': {e}")
                continue
        
        return models[:limit]
    
    def convert_to_builtin_format(self, hf_models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将 Hugging Face 模型格式转换为内置模型格式
        
        Args:
            hf_models: Hugging Face 返回的模型列表
        
        Returns:
            转换后的模型列表
        """
        converted = []
        
        for model in hf_models:
            model_id = model.get("id", "")
            name = model_id.split("/")[-1] if "/" in model_id else model_id
            
            # 获取标签
            tags = model.get("tags", [])
            
            # 推断模型类型
            model_type = self._infer_model_type_from_tags(tags, name)
            
            # 推断能力
            abilities = self._infer_abilities(name, tags)
            
            # 推断语言
            languages = self._infer_languages(name, tags)
            
            # 推断上下文长度
            context_length = self._infer_context_length(name)
            
            # 推断模型大小
            model_size = self._infer_model_size(name)
            
            converted_model = {
                "model_name": name.lower().replace("-", "_").replace(".", "_"),
                "model_description": model.get("description", f"{name} model from Hugging Face"),
                "model_type": model_type,
                "model_family": self._infer_model_family(name),
                "languages": languages,
                "abilities": abilities,
                "context_length": context_length,
                "model_specs": [{
                    "model_format": "pytorch",
                    "model_size_in_billions": model_size,
                    "quantizations": ["none", "4-bit", "8-bit"],
                    "model_id": model_id,
                    "model_hub": "huggingface"
                }]
            }
            
            converted.append(converted_model)
        
        return converted
    
    def _infer_model_type_from_tags(self, tags: List[str], name: str) -> str:
        """从标签推断模型类型"""
        tags_lower = [t.lower() for t in tags]
        name_lower = name.lower()
        
        if any(t in tags_lower for t in ["embedding", "embeddings"]):
            return "embedding"
        if any(t in tags_lower for t in ["multimodal", "vision", "vl"]):
            return "multimodal"
        if any(t in tags_lower for t in ["audio", "speech", "whisper"]):
            return "audio"
        if any(t in tags_lower for t in ["image", "diffusion", "stable-diffusion"]):
            return "image"
        
        return "llm"
    
    def _infer_abilities(self, name: str, tags: List[str]) -> List[str]:
        """推断模型能力"""
        abilities = []
        name_lower = name.lower()
        tags_lower = [t.lower() for t in tags]
        
        if "chat" in name_lower or "instruct" in name_lower:
            abilities.append("chat")
        if "code" in name_lower or "coder" in name_lower:
            abilities.append("code")
        if "vision" in name_lower or "vl" in name_lower:
            abilities.append("vision")
        
        if not abilities:
            abilities.append("generate")
        
        return abilities
    
    def _infer_languages(self, name: str, tags: List[str]) -> List[str]:
        """推断支持语言"""
        languages = []
        name_lower = name.lower()
        
        # 中文模型特征
        if any(kw in name_lower for kw in ["chinese", "qwen", "chatglm", "baichuan"]):
            languages.append("zh")
        
        # 默认都有英文
        languages.append("en")
        
        return languages
    
    def _infer_model_family(self, name: str) -> Optional[str]:
        """推断模型家族"""
        name_lower = name.lower()
        
        families = {
            "llama": ["llama", "llama2", "llama-2", "llama3", "llama-3"],
            "qwen": ["qwen", "qwen2", "qwen-2", "qwen3", "qwen-3"],
            "chatglm": ["chatglm", "glm-4", "glm4"],
            "mistral": ["mistral", "mixtral"],
            "deepseek": ["deepseek"],
            "yi": ["yi-", "yi_"],
            "gemma": ["gemma"],
            "phi": ["phi-", "phi_", "phi3"],
            "baichuan": ["baichuan"],
        }
        
        for family, keywords in families.items():
            if any(kw in name_lower for kw in keywords):
                return family
        
        return None
    
    def _infer_model_size(self, name: str) -> Optional[float]:
        """推断模型大小（参数数量）"""
        import re
        
        # 匹配常见的模型大小格式
        patterns = [
            r'(\d+\.?\d*)b',  # 7b, 13b, 70b
            r'(\d+\.?\d*)-b',  # 7-b, 13-b
        ]
        
        name_lower = name.lower()
        
        for pattern in patterns:
            match = re.search(pattern, name_lower)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        
        return None
    
    def _infer_context_length(self, name: str) -> Optional[int]:
        """推断上下文长度"""
        import re
        
        # 匹配上下文长度
        patterns = [
            r'(\d+)k',  # 4k, 8k, 128k
        ]
        
        name_lower = name.lower()
        
        for pattern in patterns:
            match = re.search(pattern, name_lower)
            if match:
                try:
                    k = int(match.group(1))
                    return k * 1000
                except:
                    continue
        
        # 默认值
        return 8192


# 全局客户端实例
hf_client = HuggingFaceClient()


if __name__ == "__main__":
    # 测试
    client = HuggingFaceClient()
    models = client.search_models(query="qwen", limit=5)
    print(f"Found {len(models)} models")
    for m in models[:3]:
        print(f"- {m.get('id')}")
