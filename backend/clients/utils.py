"""
客户端工具函数
提供模型信息推断的通用逻辑
"""

import re
from typing import List, Optional, Dict, Any


# 模型家族关键词映射
MODEL_FAMILY_KEYWORDS = {
    "llama": ["llama", "llama2", "llama-2", "llama3", "llama-3"],
    "qwen": ["qwen", "qwen2", "qwen-2", "qwen3", "qwen-3"],
    "chatglm": ["chatglm", "glm-4", "glm4", "glm-3", "glm3"],
    "mistral": ["mistral", "mixtral"],
    "deepseek": ["deepseek"],
    "yi": ["yi-", "yi_"],
    "gemma": ["gemma"],
    "phi": ["phi-", "phi_", "phi3"],
    "baichuan": ["baichuan"],
    "internlm": ["internlm"],
}

# 模型类型标签映射
MODEL_TYPE_TAGS = {
    "embedding": ["embedding", "embeddings", "向量", "bert", "roberta"],
    "multimodal": ["multimodal", "vision", "vl", "视觉", "多模态", "clip"],
    "audio": ["audio", "speech", "whisper", "语音", "音频", "wav2vec", "hubert"],
    "rerank": ["rerank", "reranker", "reranking", "重排"],
    "image": ["image", "diffusion", "stable-diffusion", "图像", "图片"],
}

# 语言标签映射
LANGUAGE_TAGS = {
    "zh": ["中文", "chinese", "qwen", "chatglm", "baichuan", "glm", "千问", "百川"],
    "en": ["english", "en"],
    "multilingual": ["multilingual", "多语言"],
}


def infer_model_family(name: str) -> Optional[str]:
    """从模型名称推断模型家族"""
    name_lower = name.lower()
    for family, keywords in MODEL_FAMILY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return family
    return None


def infer_model_type_from_tags(tags: List[str], architectures: List[str] = None) -> str:
    """从标签和架构推断模型类型"""
    tags_lower = [t.lower() for t in tags]
    all_text = " ".join(tags_lower)

    if architectures:
        all_text += " " + " ".join(architectures).lower()

    for model_type, keywords in MODEL_TYPE_TAGS.items():
        if any(kw in all_text for kw in keywords):
            return model_type

    return "llm"


def infer_abilities(name: str, tags: List[str], model_type: str) -> List[str]:
    """推断模型能力"""
    abilities = []
    name_lower = name.lower()
    tags_lower = [t.lower() for t in tags]

    if model_type == "llm":
        if any(kw in name_lower for kw in ["chat", "instruct", "对话"]):
            abilities.append("chat")
        if any(kw in name_lower for kw in ["code", "coder", "代码"]):
            abilities.append("code")
        if not abilities:
            abilities.append("generate")

    elif model_type == "multimodal":
        abilities.extend(["chat", "vision"])

    elif model_type == "embedding":
        abilities.append("embedding")

    elif model_type == "rerank":
        abilities.append("rerank")

    elif model_type == "audio":
        abilities.append("audio")

    return abilities


def infer_languages(name: str, tags: List[str]) -> List[str]:
    """推断支持语言"""
    languages = []
    name_lower = name.lower()

    # 检查中文模型特征
    if any(kw in name_lower for kw in LANGUAGE_TAGS["zh"]):
        languages.append("zh")

    # 检查多语言
    if any(kw in name_lower for kw in LANGUAGE_TAGS["multilingual"]):
        languages.append("multilingual")

    # 默认都有英文
    if "multilingual" not in languages:
        languages.append("en")

    return languages


def infer_model_size(name: str) -> Optional[float]:
    """推断模型大小（参数数量，单位：B）"""
    patterns = [
        r"(\d+\.?\d*)b",  # 7b, 13b, 70b
        r"(\d+\.?\d*)-b",  # 7-b, 13-b
        r"(\d+\.?\d*)b-",  # 7b-, 13b-
    ]

    name_lower = name.lower()

    for pattern in patterns:
        match = re.search(pattern, name_lower)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue

    return None


def infer_context_length(name: str, default: int = 8192) -> int:
    """推断上下文长度"""
    patterns = [
        r"(\d+)k",  # 4k, 8k, 128k
        r"(\d+)k-",  # 4k-, 8k-
    ]

    name_lower = name.lower()

    for pattern in patterns:
        match = re.search(pattern, name_lower)
        if match:
            try:
                k = int(match.group(1))
                return k * 1000
            except (ValueError, IndexError):
                continue

    return default


def normalize_model_name(name: str) -> str:
    """标准化模型名称"""
    return name.lower().replace("-", "_").replace(".", "_")


def extract_model_id_from_full_id(full_id: str) -> str:
    """从完整模型ID中提取短名称"""
    if "/" in full_id:
        return full_id.split("/")[-1]
    return full_id
