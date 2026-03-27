"""
内置模型列表 - 类似xinference的model family
预定义了vLLM支持的所有模型及其配置
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ModelSpec(BaseModel):
    """模型规格配置"""
    model_format: str  # pytorch, gguf, awq, gptq, etc.
    model_size_in_billions: Optional[float] = None
    quantizations: List[str] = ["none"]
    model_id: Optional[str] = None  # ModelScope model id
    model_revision: Optional[str] = None
    model_hub: str = "modelscope"


class ModelFamily(BaseModel):
    """模型家族定义"""
    model_name: str
    model_description: str
    model_type: str  # llm, embedding, rerank, audio, image, video, multimodal
    model_family: Optional[str] = None
    model_specs: List[ModelSpec]
    prompt_style: Optional[str] = None
    context_length: Optional[int] = None
    languages: List[str] = []
    abilities: List[str] = []  # chat, generate, vision, tools, embedding, rerank, etc.
    is_builtin: bool = True


# 内置模型列表 - 主流开源模型
BUILTIN_MODELS: List[ModelFamily] = [
    # LLaMA 系列
    ModelFamily(
        model_name="llama-2",
        model_description="Meta开发的LLaMA 2系列大语言模型",
        model_type="llm",
        model_family="llama",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Llama-2-7b-chat-ms",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Llama-2-13b-chat-ms",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=70,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Llama-2-70b-chat-ms",
            ),
        ],
    ),
    
    # LLaMA 3 系列
    ModelFamily(
        model_name="llama-3",
        model_description="Meta开发的最新LLaMA 3系列大语言模型",
        model_type="llm",
        model_family="llama",
        context_length=8192,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Meta-Llama-3-8B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=70,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Meta-Llama-3-70B-Instruct",
            ),
        ],
    ),
    
    # LLaMA 3.1 系列
    ModelFamily(
        model_name="llama-3.1",
        model_description="Meta开发的LLaMA 3.1系列，支持128K上下文",
        model_type="llm",
        model_family="llama",
        context_length=128000,
        languages=["en", "zh", "de", "fr", "it", "pt", "hi", "th", "es"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Meta-Llama-3.1-8B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=70,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Meta-Llama-3.1-70B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=405,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Meta-Llama-3.1-405B-Instruct",
            ),
        ],
    ),
    
    # Qwen 系列
    ModelFamily(
        model_name="qwen2",
        model_description="阿里巴巴通义千问2系列大语言模型",
        model_type="llm",
        model_family="qwen",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.5,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-0.5B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.5,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-1.5B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-7B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=72,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-72B-Instruct",
            ),
        ],
    ),
    
    # Qwen 2.5 系列
    ModelFamily(
        model_name="qwen2.5",
        model_description="阿里巴巴通义千问2.5系列，全面升级",
        model_type="llm",
        model_family="qwen",
        context_length=32768,
        languages=["zh", "en", "ja", "ko", "de", "fr", "it", "pt", "es", "id", "th", "vi", "ar"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.5,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-0.5B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.5,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-1.5B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-3B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-7B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=14,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-14B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=32,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-32B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=72,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen2.5-72B-Instruct",
            ),
        ],
    ),
    
    # Qwen 2.5 Coder 系列
    ModelFamily(
        model_name="qwen2.5-coder",
        model_description="阿里巴巴通义千问2.5代码专用模型",
        model_type="llm",
        model_family="qwen",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.5,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2.5-Coder-1.5B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2.5-Coder-7B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=14,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2.5-Coder-14B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=32,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2.5-Coder-32B-Instruct",
            ),
        ],
    ),
    
    # Qwen 2 VL 系列 (多模态)
    ModelFamily(
        model_name="qwen2-vl",
        model_description="阿里巴巴通义千问2视觉语言多模态模型",
        model_type="multimodal",
        model_family="qwen",
        context_length=32768,
        languages=["zh", "en", "ja", "ko", "de", "fr", "it", "pt", "es"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-VL-2B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-VL-7B-Instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=72,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen2-VL-72B-Instruct",
            ),
        ],
    ),

    # Qwen3 系列
    ModelFamily(
        model_name="qwen3",
        model_description="通义千问3系列大语言模型，支持思考模式",
        model_type="llm",
        model_family="qwen",
        context_length=128000,
        languages=["zh", "en", "multilingual"],
        abilities=["chat", "generate", "tools", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.6,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-0.6B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-1.7B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=4,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-4B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-8B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=14,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-14B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=32,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-32B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=30,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="qwen/Qwen3-30B-A3B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=235,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="qwen/Qwen3-235B-A22B",
            ),
        ],
    ),

    # ChatGLM 系列
    ModelFamily(
        model_name="chatglm3",
        model_description="智谱AI ChatGLM3系列大语言模型",
        model_type="llm",
        model_family="chatglm",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="ZhipuAI/chatglm3-6b",
            ),
        ],
    ),
    
    # GLM-4 系列
    ModelFamily(
        model_name="glm-4",
        model_description="智谱AI GLM-4系列最新大语言模型",
        model_type="llm",
        model_family="chatglm",
        context_length=131072,
        languages=["zh", "en"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=9,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="ZhipuAI/glm-4-9b-chat",
            ),
        ],
    ),
    
    # Mistral 系列
    ModelFamily(
        model_name="mistral",
        model_description="Mistral AI开发的高性能大语言模型",
        model_type="llm",
        model_family="mistral",
        context_length=32768,
        languages=["en", "fr", "de", "es", "it", "pt"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Mistral-7B-Instruct-v0.3",
            ),
        ],
    ),
    
    # Mixtral 系列
    ModelFamily(
        model_name="mixtral",
        model_description="Mistral AI开发的MoE架构大语言模型",
        model_type="llm",
        model_family="mistral",
        context_length=32768,
        languages=["en", "fr", "de", "es", "it", "pt"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Mixtral-8x7B-Instruct-v0.1",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=22,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Mixtral-8x22B-Instruct-v0.1",
            ),
        ],
    ),
    
    # DeepSeek 系列
    ModelFamily(
        model_name="deepseek",
        model_description="DeepSeek开发的高性能大语言模型",
        model_type="llm",
        model_family="deepseek",
        context_length=65536,
        languages=["zh", "en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6.7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="deepseek-ai/deepseek-llm-7b-chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=67,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="deepseek-ai/deepseek-llm-67b-chat",
            ),
        ],
    ),
    
    # DeepSeek Coder 系列
    ModelFamily(
        model_name="deepseek-coder",
        model_description="DeepSeek开发的代码专用模型",
        model_type="llm",
        model_family="deepseek",
        context_length=16384,
        languages=["zh", "en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="deepseek-ai/deepseek-coder-1.3b-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6.7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="deepseek-ai/deepseek-coder-6.7b-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=33,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="deepseek-ai/deepseek-coder-33b-instruct",
            ),
        ],
    ),
    
    # Yi 系列
    ModelFamily(
        model_name="yi",
        model_description="零一万物开发的Yi系列大语言模型",
        model_type="llm",
        model_family="yi",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="01ai/Yi-6B-Chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=34,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="01ai/Yi-34B-Chat",
            ),
        ],
    ),
    
    # Yi-VL 系列 (多模态)
    ModelFamily(
        model_name="yi-vl",
        model_description="零一万物开发的Yi视觉语言多模态模型",
        model_type="multimodal",
        model_family="yi",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="01ai/Yi-VL-6B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=34,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="01ai/Yi-VL-34B",
            ),
        ],
    ),
    
    # Embedding 模型
    ModelFamily(
        model_name="bge-large-zh",
        model_description="BAAI开发的的中文Embedding模型",
        model_type="embedding",
        model_family="bge",
        context_length=512,
        languages=["zh"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="BAAI/bge-large-zh-v1.5",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="bge-large-en",
        model_description="BAAI开发的英文Embedding模型",
        model_type="embedding",
        model_family="bge",
        context_length=512,
        languages=["en"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="BAAI/bge-large-en-v1.5",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="bge-m3",
        model_description="BAAI开发的多语言长文本Embedding模型",
        model_type="embedding",
        model_family="bge",
        context_length=8192,
        languages=["zh", "en", "ja", "ko", "de", "fr", "es", "pt", "it"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.5,
                quantizations=["none"],
                model_id="BAAI/bge-m3",
            ),
        ],
    ),
    
    # Rerank 模型
    ModelFamily(
        model_name="bge-reranker",
        model_description="BAAI开发的Rerank模型",
        model_type="rerank",
        model_family="bge",
        context_length=512,
        languages=["zh", "en"],
        abilities=["rerank"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="BAAI/bge-reranker-v2-m3",
            ),
        ],
    ),
    
    # 音频模型
    ModelFamily(
        model_name="whisper",
        model_description="OpenAI开发的语音识别模型",
        model_type="audio",
        model_family="whisper",
        context_length=1500,
        languages=["multilingual"],
        abilities=["audio"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.039,
                quantizations=["none"],
                model_id="modelscope/whisper-tiny",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.074,
                quantizations=["none"],
                model_id="modelscope/whisper-base",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.244,
                quantizations=["none"],
                model_id="modelscope/whisper-small",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.769,
                quantizations=["none"],
                model_id="modelscope/whisper-medium",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.55,
                quantizations=["none"],
                model_id="modelscope/whisper-large-v3",
            ),
        ],
    ),
    
    # Baichuan 百川系列
    ModelFamily(
        model_name="baichuan2",
        model_description="百川智能开发的Baichuan 2系列大语言模型",
        model_type="llm",
        model_family="baichuan",
        context_length=4096,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="baichuan-inc/Baichuan2-7B-Chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="baichuan-inc/Baichuan2-13B-Chat",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="baichuan2-192k",
        model_description="百川智能Baichuan 2长上下文版本，支持192K上下文",
        model_type="llm",
        model_family="baichuan",
        context_length=192000,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="baichuan-inc/Baichuan2-7B-Base",
            ),
        ],
    ),
    
    # InternLM 书生·浦语系列
    ModelFamily(
        model_name="internlm2",
        model_description="上海AI Lab开发的书生·浦语2系列大语言模型",
        model_type="llm",
        model_family="internlm",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="internlm/internlm2-chat-7b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=20,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="internlm/internlm2-chat-20b",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="internlm2.5",
        model_description="上海AI Lab开发的书生·浦语2.5系列，支持百万字长文本",
        model_type="llm",
        model_family="internlm",
        context_length=1000000,
        languages=["zh", "en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="internlm/internlm2_5-7b-chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=20,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="internlm/internlm2_5-20b-chat",
            ),
        ],
    ),
    
    # CodeLlama 系列
    ModelFamily(
        model_name="codellama",
        model_description="Meta开发的代码专用大语言模型",
        model_type="llm",
        model_family="llama",
        context_length=16384,
        languages=["en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-7b-Instruct-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-13b-Instruct-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=34,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-34b-Instruct-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=70,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-70b-Instruct-hf",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="codellama-python",
        model_description="Meta开发的Python代码专用模型",
        model_type="llm",
        model_family="llama",
        context_length=16384,
        languages=["en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-7b-Python-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-13b-Python-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=34,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/CodeLlama-34b-Python-hf",
            ),
        ],
    ),
    
    # Vicuna 系列
    ModelFamily(
        model_name="vicuna",
        model_description="LMSYS开发的Vicuna系列对话模型",
        model_type="llm",
        model_family="llama",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/vicuna-7b-v1.5",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/vicuna-13b-v1.5",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=33,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/vicuna-33b-v1.3",
            ),
        ],
    ),
    
    # Falcon 系列
    ModelFamily(
        model_name="falcon",
        model_description="TII开发的Falcon系列大语言模型",
        model_type="llm",
        model_family="falcon",
        context_length=2048,
        languages=["en", "de", "es", "fr"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/falcon-7b-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=40,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/falcon-40b-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=180,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/falcon-180B-chat",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="falcon2",
        model_description="TII开发的Falcon 2系列最新模型",
        model_type="llm",
        model_family="falcon",
        context_length=8192,
        languages=["en", "de", "es", "fr", "it", "pt", "pl", "nl", "ro", "cs", "sv"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=11,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/falcon-11B",
            ),
        ],
    ),
    
    # Gemma 系列
    ModelFamily(
        model_name="gemma",
        model_description="Google开发的轻量级开源模型",
        model_type="llm",
        model_family="gemma",
        context_length=8192,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/gemma-2b-it",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/gemma-7b-it",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="gemma2",
        model_description="Google开发的Gemma 2系列，性能大幅提升",
        model_type="llm",
        model_family="gemma",
        context_length=8192,
        languages=["en", "it", "de", "fr", "es", "pt", "pl", "nl", "ro", "cs", "sv", "da", "hu", "bg", "fi", "sk", "hr", "sl", "lt", "lv", "et", "mt", "ga", "cy"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/gemma-2-2b-it",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=9,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/gemma-2-9b-it",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=27,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/gemma-2-27b-it",
            ),
        ],
    ),
    
    # Phi 系列
    ModelFamily(
        model_name="phi3",
        model_description="Microsoft开发的小参数高性能模型",
        model_type="llm",
        model_family="phi",
        context_length=128000,
        languages=["en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3.8,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Phi-3-mini-4k-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3.8,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Phi-3-mini-128k-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Phi-3-small-8k-instruct",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=14,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Phi-3-medium-4k-instruct",
            ),
        ],
    ),
    
    # Command-R 系列
    ModelFamily(
        model_name="command-r",
        model_description="Cohere开发的Command R系列模型，支持RAG和工具使用",
        model_type="llm",
        model_family="cohere",
        context_length=128000,
        languages=["en", "fr", "es", "it", "de", "pt", "ja", "ko", "zh", "ar"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=35,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/c4ai-command-r-v01",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="command-r-plus",
        model_description="Cohere开发的Command R+系列，更强的推理能力",
        model_type="llm",
        model_family="cohere",
        context_length=128000,
        languages=["en", "fr", "es", "it", "de", "pt", "ja", "ko", "zh", "ar"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=104,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/c4ai-command-r-plus",
            ),
        ],
    ),
    
    # StableLM 系列
    ModelFamily(
        model_name="stablelm",
        model_description="Stability AI开发的StableLM系列模型",
        model_type="llm",
        model_family="stablelm",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/stablelm-3b-4e1t",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/stablelm-2-12b-chat",
            ),
        ],
    ),
    
    # Zephyr 系列
    ModelFamily(
        model_name="zephyr",
        model_description="HuggingFace开发的Zephyr系列对齐模型",
        model_type="llm",
        model_family="mistral",
        context_length=32768,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/zephyr-7b-beta",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/zephyr-7b-gemma-v0.1",
            ),
        ],
    ),
    
    # Orca 系列
    ModelFamily(
        model_name="orca2",
        model_description="Microsoft开发的Orca 2推理优化模型",
        model_type="llm",
        model_family="llama",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Orca-2-7b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Orca-2-13b",
            ),
        ],
    ),
    
    # StarCoder 系列
    ModelFamily(
        model_name="starcoder2",
        model_description="BigCode开发的StarCoder 2代码模型",
        model_type="llm",
        model_family="starcoder",
        context_length=16384,
        languages=["en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/starcoder2-3b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/starcoder2-7b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=15,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/starcoder2-15b",
            ),
        ],
    ),
    
    # SOLAR 系列
    ModelFamily(
        model_name="solar",
        model_description="Upstage开发的SOLAR系列模型",
        model_type="llm",
        model_family="solar",
        context_length=4096,
        languages=["en", "ko"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=10.7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/SOLAR-10.7B-Instruct-v1.0",
            ),
        ],
    ),
    
    # DBRX 系列
    ModelFamily(
        model_name="dbrx",
        model_description="Databricks开发的DBRX MoE架构模型",
        model_type="llm",
        model_family="dbrx",
        context_length=32768,
        languages=["en"],
        abilities=["chat", "generate", "code"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=132,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/dbrx-instruct",
            ),
        ],
    ),
    
    # Jamba 系列
    ModelFamily(
        model_name="jamba",
        model_description="AI21 Labs开发的Jamba SSM-Transformer混合架构模型",
        model_type="llm",
        model_family="jamba",
        context_length=256000,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=52,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/Jamba-v0.1",
            ),
        ],
    ),
    
    # Nemotron 系列
    ModelFamily(
        model_name="nemotron",
        model_description="NVIDIA开发的Nemotron系列模型",
        model_type="llm",
        model_family="nemotron",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=4,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/Nemotron-4-340B-Instruct",
            ),
        ],
    ),
    
    # MiniCPM 系列
    ModelFamily(
        model_name="minicpm",
        model_description="面壁智能开发的MiniCPM系列小参数模型",
        model_type="llm",
        model_family="minicpm",
        context_length=4096,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2.8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="OpenBMB/MiniCPM-2B-sft-bf16",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="minicpm3",
        model_description="面壁智能开发的MiniCPM 3.0系列，4B参数媲美GPT-3.5",
        model_type="llm",
        model_family="minicpm",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate", "tools"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=4,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="OpenBMB/MiniCPM3-4B",
            ),
        ],
    ),
    
    # TeleChat 系列
    ModelFamily(
        model_name="telechat",
        model_description="中国电信开发的TeleChat系列大语言模型",
        model_type="llm",
        model_family="telechat",
        context_length=8192,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="TeleAI/TeleChat-7B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=12,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="TeleAI/TeleChat-12B",
            ),
        ],
    ),
    
    # BlueLM 系列
    ModelFamily(
        model_name="bluelm",
        model_description="vivo开发的BlueLM蓝心大模型",
        model_type="llm",
        model_family="bluelm",
        context_length=4096,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="vivo-ai/BlueLM-7B-Chat",
            ),
        ],
    ),
    
    # XVERSE 系列
    ModelFamily(
        model_name="xverse",
        model_description="元象科技开发的XVERSE系列大语言模型",
        model_type="llm",
        model_family="xverse",
        context_length=32768,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="xverse/XVERSE-7B-Chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="xverse/XVERSE-13B-Chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=65,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="xverse/XVERSE-65B-Chat",
            ),
        ],
    ),
    
    # OpenChat 系列
    ModelFamily(
        model_name="openchat",
        model_description="OpenChat团队开发的通用对话模型",
        model_type="llm",
        model_family="llama",
        context_length=8192,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/openchat-3.5",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/openchat-3.5-0106",
            ),
        ],
    ),
    
    # Neural-Chat 系列
    ModelFamily(
        model_name="neural-chat",
        model_description="Intel开发的Neural Chat对话模型",
        model_type="llm",
        model_family="llama",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/neural-chat-7b-v3-1",
            ),
        ],
    ),
    
    # Aquila 系列
    ModelFamily(
        model_name="aquila",
        model_description="智源研究院开发的Aquila系列大语言模型",
        model_type="llm",
        model_family="aquila",
        context_length=2048,
        languages=["zh", "en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="BAAI/AquilaChat2-7B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=34,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="BAAI/AquilaChat2-34B",
            ),
        ],
    ),
    
    # mT5/XLM 系列多语言模型
    ModelFamily(
        model_name="mpt",
        model_description="MosaicML开发的MPT系列模型",
        model_type="llm",
        model_family="mpt",
        context_length=8192,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/mpt-7b-chat",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=30,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/mpt-30b-chat",
            ),
        ],
    ),
    
    # GPT-Neo/GPT-J 系列
    ModelFamily(
        model_name="gpt-neox",
        model_description="EleutherAI开发的GPT-NeoX系列模型",
        model_type="llm",
        model_family="gpt-neox",
        context_length=2048,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=20,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/gpt-neox-20b",
            ),
        ],
    ),
    
    # Pythia 系列
    ModelFamily(
        model_name="pythia",
        model_description="EleutherAI开发的Pythia系列模型",
        model_type="llm",
        model_family="pythia",
        context_length=2048,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2.8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/pythia-2.8b-deduped",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6.9,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/pythia-6.9b-deduped",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=12,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/pythia-12b-deduped",
            ),
        ],
    ),
    
    # RedPajama 系列
    ModelFamily(
        model_name="redpajama",
        model_description="Together AI开发的RedPajama系列模型",
        model_type="llm",
        model_family="gpt-neox",
        context_length=2048,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/RedPajama-INCITE-Chat-3B-v1",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/RedPajama-INCITE-7B-Chat",
            ),
        ],
    ),
    
    # OPT 系列
    ModelFamily(
        model_name="opt",
        model_description="Meta开发的OPT开放预训练模型",
        model_type="llm",
        model_family="opt",
        context_length=2048,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=6.7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/opt-6.7b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/opt-13b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=30,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/opt-30b",
            ),
        ],
    ),
    
    # BLOOM 系列
    ModelFamily(
        model_name="bloom",
        model_description="BigScience开发的BLOOM多语言模型",
        model_type="llm",
        model_family="bloom",
        context_length=2048,
        languages=["en", "zh", "fr", "es", "ar", "pt", "it", "de", "hi", "ru", "ja"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/bloom-3b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/bloom-7b1",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=176,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/bloom",
            ),
        ],
    ),
    
    # BLOOMZ 系列
    ModelFamily(
        model_name="bloomz",
        model_description="BigScience开发的BLOOMZ指令微调模型",
        model_type="llm",
        model_family="bloom",
        context_length=2048,
        languages=["en", "zh", "fr", "es", "ar", "pt", "it", "de", "hi", "ru", "ja"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/bloomz-3b",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/bloomz-7b1",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=176,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/bloomz",
            ),
        ],
    ),
    
    # T5/Flan-T5 系列
    ModelFamily(
        model_name="flan-t5",
        model_description="Google开发的Flan-T5指令微调模型",
        model_type="llm",
        model_family="t5",
        context_length=512,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.25,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/flan-t5-small",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.77,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/flan-t5-base",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=3,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/flan-t5-large",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=11,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/flan-t5-xl",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=45,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/flan-t5-xxl",
            ),
        ],
    ),
    
    # UL2 系列
    ModelFamily(
        model_name="ul2",
        model_description="Google开发的UL2统一语言学习模型",
        model_type="llm",
        model_family="t5",
        context_length=512,
        languages=["en"],
        abilities=["chat", "generate"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=20,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/ul2",
            ),
        ],
    ),
    
    # RoBERTa 系列 (Embedding)
    ModelFamily(
        model_name="roberta",
        model_description="Facebook开发的RoBERTa预训练模型",
        model_type="embedding",
        model_family="roberta",
        context_length=512,
        languages=["en"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.355,
                quantizations=["none"],
                model_id="modelscope/roberta-base",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.5,
                quantizations=["none"],
                model_id="modelscope/roberta-large",
            ),
        ],
    ),
    
    # E5 系列 (Embedding)
    ModelFamily(
        model_name="e5",
        model_description="Microsoft开发的E5文本Embedding模型",
        model_type="embedding",
        model_family="e5",
        context_length=512,
        languages=["en", "zh", "de", "es", "fr", "it", "pt", "nl", "pl", "ru", "ja", "ko"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.1,
                quantizations=["none"],
                model_id="modelscope/e5-small-v2",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/e5-base-v2",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.1,
                quantizations=["none"],
                model_id="modelscope/e5-large-v2",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.5,
                quantizations=["none"],
                model_id="modelscope/multilingual-e5-base",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.1,
                quantizations=["none"],
                model_id="modelscope/multilingual-e5-large",
            ),
        ],
    ),
    
    # GTE 系列 (Embedding)
    ModelFamily(
        model_name="gte",
        model_description="阿里巴巴开发的GTE通用文本Embedding模型",
        model_type="embedding",
        model_family="gte",
        context_length=8192,
        languages=["zh", "en"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.1,
                quantizations=["none"],
                model_id="Alibaba-NLP/gte-small-zh",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="Alibaba-NLP/gte-base-zh",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="Alibaba-NLP/gte-large-zh",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="Alibaba-NLP/gte-base-en-v1.5",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.4,
                quantizations=["none"],
                model_id="Alibaba-NLP/gte-large-en-v1.5",
            ),
        ],
    ),
    
    # Jina Embedding 系列
    ModelFamily(
        model_name="jina-embeddings",
        model_description="Jina AI开发的Embedding模型",
        model_type="embedding",
        model_family="jina",
        context_length=8192,
        languages=["en"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.4,
                quantizations=["none"],
                model_id="modelscope/jina-embeddings-v2-base-en",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=1.1,
                quantizations=["none"],
                model_id="modelscope/jina-embeddings-v2-large-en",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/jina-embeddings-v2-small-en",
            ),
        ],
    ),
    
    # Jina Reranker 系列
    ModelFamily(
        model_name="jina-reranker",
        model_description="Jina AI开发的Rerank模型",
        model_type="rerank",
        model_family="jina",
        context_length=8192,
        languages=["en"],
        abilities=["rerank"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/jina-reranker-v2-base-multilingual",
            ),
        ],
    ),
    
    # Cohere Embedding 系列
    ModelFamily(
        model_name="cohere-embed",
        model_description="Cohere开发的Embedding模型",
        model_type="embedding",
        model_family="cohere",
        context_length=512,
        languages=["en", "de", "es", "fr", "it", "pt", "ja", "ko", "zh", "ar"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/c4ai-embed-v3-multilingual",
            ),
        ],
    ),
    
    # Sentence-Transformer 系列
    ModelFamily(
        model_name="all-minilm",
        model_description="Sentence Transformers开发的MiniLM Embedding模型",
        model_type="embedding",
        model_family="sentence-transformers",
        context_length=512,
        languages=["en"],
        abilities=["embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.02,
                quantizations=["none"],
                model_id="modelscope/all-MiniLM-L6-v2",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.03,
                quantizations=["none"],
                model_id="modelscope/all-MiniLM-L12-v2",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.04,
                quantizations=["none"],
                model_id="modelscope/all-mpnet-base-v2",
            ),
        ],
    ),
    
    # CLIP 系列 (多模态)
    ModelFamily(
        model_name="clip",
        model_description="OpenAI开发的CLIP视觉-语言模型",
        model_type="multimodal",
        model_family="clip",
        context_length=77,
        languages=["en"],
        abilities=["vision", "embedding"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.15,
                quantizations=["none"],
                model_id="modelscope/clip-vit-base-patch32",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/clip-vit-large-patch14",
            ),
        ],
    ),
    
    # LLaVA 系列 (多模态)
    ModelFamily(
        model_name="llava",
        model_description="LLaVA团队开发的视觉语言多模态模型",
        model_type="multimodal",
        model_family="llava",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/llava-1.5-7b-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="modelscope/llava-1.5-13b-hf",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="llava-next",
        model_description="LLaVA-NeXT下一代视觉语言模型",
        model_type="multimodal",
        model_family="llava",
        context_length=4096,
        languages=["en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=7,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/llava-v1.6-vicuna-7b-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=13,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/llava-v1.6-vicuna-13b-hf",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=34,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="modelscope/llava-v1.6-34b-hf",
            ),
        ],
    ),
    
    # CogVLM 系列 (多模态)
    ModelFamily(
        model_name="cogvlm",
        model_description="智谱AI开发的CogVLM视觉语言模型",
        model_type="multimodal",
        model_family="cogvlm",
        context_length=2048,
        languages=["zh", "en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=17,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="ZhipuAI/cogvlm-chat-hf",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="cogvlm2",
        model_description="智谱AI开发的CogVLM 2.0视觉语言模型",
        model_type="multimodal",
        model_family="cogvlm",
        context_length=8192,
        languages=["zh", "en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=19,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="ZhipuAI/cogvlm2-llama3-chat-19B",
            ),
        ],
    ),
    
    # InternVL 系列 (多模态)
    ModelFamily(
        model_name="internvl",
        model_description="上海AI Lab开发的InternVL视觉语言模型",
        model_type="multimodal",
        model_family="internlm",
        context_length=8192,
        languages=["zh", "en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2.2,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="OpenGVLab/InternVL2-1B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=4,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="OpenGVLab/InternVL2-4B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="OpenGVLab/InternVL2-8B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=26,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="OpenGVLab/InternVL2-26B",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=40,
                quantizations=["none", "4-bit", "8-bit", "fp8"],
                model_id="OpenGVLab/InternVL2-40B",
            ),
        ],
    ),
    
    # MiniCPM-V 系列 (多模态)
    ModelFamily(
        model_name="minicpm-v",
        model_description="面壁智能开发的MiniCPM-V视觉语言模型",
        model_type="multimodal",
        model_family="minicpm",
        context_length=4096,
        languages=["zh", "en"],
        abilities=["chat", "vision"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=2.8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="OpenBMB/MiniCPM-V-2",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=8,
                quantizations=["none", "4-bit", "8-bit"],
                model_id="OpenBMB/MiniCPM-V-2_6",
            ),
        ],
    ),
    
    # Speech/Audio 模型
    ModelFamily(
        model_name="wav2vec2",
        model_description="Facebook开发的Wav2Vec 2.0语音识别模型",
        model_type="audio",
        model_family="wav2vec",
        context_length=1500,
        languages=["multilingual"],
        abilities=["audio"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/wav2vec2-base-960h",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/wav2vec2-large-960h",
            ),
        ],
    ),
    
    ModelFamily(
        model_name="hubert",
        model_description="Facebook开发的HuBERT语音表示模型",
        model_type="audio",
        model_family="hubert",
        context_length=1500,
        languages=["multilingual"],
        abilities=["audio"],
        model_specs=[
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/hubert-base-ls960",
            ),
            ModelSpec(
                model_format="pytorch",
                model_size_in_billions=0.3,
                quantizations=["none"],
                model_id="modelscope/hubert-large-ls960-ft",
            ),
        ],
    ),
]


def get_builtin_models(
    model_type: Optional[str] = None,
    model_name: Optional[str] = None,
    abilities: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
) -> List[ModelFamily]:
    """获取内置模型列表，支持过滤"""
    models = BUILTIN_MODELS
    
    if model_type and model_type != "all":
        models = [m for m in models if m.model_type == model_type]
    
    if model_name:
        models = [m for m in models if model_name.lower() in m.model_name.lower()]
    
    if abilities:
        models = [m for m in models if any(a in m.abilities for a in abilities)]
    
    if languages:
        models = [m for m in models if any(l in m.languages for l in languages)]
    
    return models


def get_model_by_name(model_name: str) -> Optional[ModelFamily]:
    """根据模型名称获取模型定义"""
    for model in BUILTIN_MODELS:
        if model.model_name == model_name:
            return model
    return None


def list_model_types() -> List[Dict[str, str]]:
    """列出所有模型类型"""
    types = {}
    for model in BUILTIN_MODELS:
        types[model.model_type] = {
            "llm": "大语言模型",
            "embedding": "向量模型",
            "rerank": "重排模型",
            "audio": "音频模型",
            "image": "图像模型",
            "video": "视频模型",
            "multimodal": "多模态模型",
        }.get(model.model_type, model.model_type)
    
    return [{"key": k, "label": v} for k, v in types.items()]


def list_model_families() -> List[str]:
    """列出所有模型家族"""
    families = set()
    for model in BUILTIN_MODELS:
        if model.model_family:
            families.add(model.model_family)
    return sorted(list(families))
