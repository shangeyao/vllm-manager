"""
客户端抽象基类
定义模型源客户端和推理引擎客户端的统一接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, AsyncGenerator
from enum import Enum


class ModelType(str, Enum):
    """模型类型枚举"""
    LLM = "llm"
    EMBEDDING = "embedding"
    MULTIMODAL = "multimodal"
    AUDIO = "audio"
    RERANK = "rerank"
    IMAGE = "image"


class ModelAbility(str, Enum):
    """模型能力枚举"""
    CHAT = "chat"
    GENERATE = "generate"
    CODE = "code"
    VISION = "vision"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    AUDIO = "audio"


@dataclass
class ModelSpec:
    """模型规格信息"""
    model_format: str = "pytorch"
    model_size_in_billions: Optional[float] = None
    quantizations: List[str] = field(default_factory=lambda: ["none", "4-bit", "8-bit"])
    model_id: str = ""
    model_revision: Optional[str] = None
    model_hub: str = ""
    architectures: List[str] = field(default_factory=list)


@dataclass
class ModelInfo:
    """统一的模型信息结构"""
    model_id: str
    model_name: str
    model_description: str
    model_type: ModelType
    model_family: Optional[str] = None
    languages: List[str] = field(default_factory=lambda: ["en"])
    abilities: List[str] = field(default_factory=list)
    context_length: int = 8192
    specs: List[ModelSpec] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    likes: int = 0
    source: str = ""  # 模型来源: modelscope, huggingface, etc.

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "model_description": self.model_description,
            "model_type": self.model_type.value,
            "model_family": self.model_family,
            "languages": self.languages,
            "abilities": self.abilities,
            "context_length": self.context_length,
            "specs": [
                {
                    "model_format": s.model_format,
                    "model_size_in_billions": s.model_size_in_billions,
                    "quantizations": s.quantizations,
                    "model_id": s.model_id,
                    "model_revision": s.model_revision,
                    "model_hub": s.model_hub,
                    "architectures": s.architectures,
                }
                for s in self.specs
            ],
            "tags": self.tags,
            "downloads": self.downloads,
            "likes": self.likes,
            "source": self.source,
        }


class ModelSourceClient(ABC):
    """
    模型源客户端抽象基类
    用于从不同的模型仓库(ModelScope, HuggingFace等)获取模型信息
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def search_models(
        self,
        query: str = "",
        model_type: Optional[ModelType] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> List[ModelInfo]:
        """
        搜索模型

        Args:
            query: 搜索关键词
            model_type: 模型类型过滤
            tags: 标签过滤
            page: 页码
            per_page: 每页数量

        Returns:
            模型信息列表
        """
        pass

    @abstractmethod
    async def get_model_detail(self, model_id: str) -> Optional[ModelInfo]:
        """
        获取模型详细信息

        Args:
            model_id: 模型ID

        Returns:
            模型详细信息
        """
        pass

    @abstractmethod
    async def get_popular_models(self, limit: int = 100) -> List[ModelInfo]:
        """
        获取热门模型列表

        Args:
            limit: 返回数量限制

        Returns:
            热门模型列表
        """
        pass

    @abstractmethod
    async def get_models_by_organization(
        self, organization: str, page_size: int = 50
    ) -> List[ModelInfo]:
        """
        获取指定组织的模型列表

        Args:
            organization: 组织名称
            page_size: 每页数量

        Returns:
            模型列表
        """
        pass


class InferenceClient(ABC):
    """
    推理引擎客户端抽象基类
    用于与不同的推理引擎(vLLM等)交互
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key

    @abstractmethod
    async def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        pass

    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取模型详细信息"""
        pass

    @abstractmethod
    async def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """创建聊天完成请求"""
        pass

    @abstractmethod
    async def create_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """创建文本完成请求"""
        pass

    @abstractmethod
    async def create_embedding(
        self, model: str, input_text: str
    ) -> Dict[str, Any]:
        """创建嵌入向量"""
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """检查服务健康状态"""
        pass

    @abstractmethod
    async def close(self):
        """关闭客户端连接"""
        pass
