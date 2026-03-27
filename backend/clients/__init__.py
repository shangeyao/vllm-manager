"""
统一客户端接口模块
提供模型源客户端和推理引擎客户端的统一抽象
"""

from .base import ModelSourceClient, InferenceClient, ModelInfo, ModelSpec
from .modelscope import ModelScopeClient, modelscope_client
from .huggingface import HuggingFaceClient
from .vllm import VLLMClient, VLLMProcessManager, vllm_client, vllm_process_manager

__all__ = [
    # 基类
    "ModelSourceClient",
    "InferenceClient",
    "ModelInfo",
    "ModelSpec",
    # 实现类
    "ModelScopeClient",
    "HuggingFaceClient",
    "VLLMClient",
    "VLLMProcessManager",
    # 实例
    "modelscope_client",
    "vllm_client",
    "vllm_process_manager",
]
