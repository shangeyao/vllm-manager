"""
vLLM 参数定义
包含所有 vLLM api_server 支持的参数
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class VLLMParam:
    """vLLM 参数定义"""
    name: str
    type: str
    default: Any
    description: str
    choices: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    category: str = "general"  # general, performance, quantization, advanced


# vLLM 完整参数列表
VLLM_PARAMS = {
    # ========== 基本参数 ==========
    "tensor_parallel_size": VLLMParam(
        name="tensor_parallel_size",
        type="int",
        default=1,
        description="张量并行大小（GPU数量）",
        min_value=1,
        max_value=8,
        category="general"
    ),
    "gpu_memory_utilization": VLLMParam(
        name="gpu_memory_utilization",
        type="float",
        default=0.9,
        description="GPU内存利用率",
        min_value=0.0,
        max_value=1.0,
        category="general"
    ),
    "max_model_len": VLLMParam(
        name="max_model_len",
        type="int",
        default=None,
        description="最大模型上下文长度",
        min_value=1,
        category="general"
    ),
    "quantization": VLLMParam(
        name="quantization",
        type="str",
        default=None,
        description="量化方式",
        choices=["aqlm", "awq", "deepspeedfp", "tpu_int8", "fp8", "fbgemm_fp8", 
                "modelopt", "marlin", "gguf", "gptq_marlin_24", "gptq_marlin", 
                "awq_marlin", "gptq", "compressed-tensors", "bitsandbytes", 
                "qqq", "hqq", "experts_int8", "neuron_quant", "ipex"],
        category="quantization"
    ),
    "dtype": VLLMParam(
        name="dtype",
        type="str",
        default="auto",
        description="数据类型",
        choices=["auto", "half", "float16", "bfloat16", "float", "float32"],
        category="general"
    ),
    
    # ========== 性能参数 ==========
    "kv_cache_dtype": VLLMParam(
        name="kv_cache_dtype",
        type="str",
        default="auto",
        description="KV Cache 数据类型",
        choices=["auto", "fp8", "fp8_e5m2", "fp8_e4m3"],
        category="performance"
    ),
    "block_size": VLLMParam(
        name="block_size",
        type="int",
        default=16,
        description="Token块大小",
        choices=[8, 16, 32, 64, 128],
        category="performance"
    ),
    "swap_space": VLLMParam(
        name="swap_space",
        type="float",
        default=4.0,
        description="CPU交换空间(GB)",
        min_value=0,
        category="performance"
    ),
    "cpu_offload_gb": VLLMParam(
        name="cpu_offload_gb",
        type="float",
        default=0,
        description="CPU卸载空间(GB)",
        min_value=0,
        category="performance"
    ),
    "max_num_batched_tokens": VLLMParam(
        name="max_num_batched_tokens",
        type="int",
        default=None,
        description="最大批处理token数",
        min_value=1,
        category="performance"
    ),
    "max_num_seqs": VLLMParam(
        name="max_num_seqs",
        type="int",
        default=256,
        description="最大并发序列数",
        min_value=1,
        category="performance"
    ),
    "max_parallel_loading_workers": VLLMParam(
        name="max_parallel_loading_workers",
        type="int",
        default=None,
        description="最大并行加载工作线程数",
        min_value=1,
        category="performance"
    ),
    "pipeline_parallel_size": VLLMParam(
        name="pipeline_parallel_size",
        type="int",
        default=1,
        description="流水线并行大小",
        min_value=1,
        category="performance"
    ),
    "num_scheduler_steps": VLLMParam(
        name="num_scheduler_steps",
        type="int",
        default=1,
        description="调度器步数",
        min_value=1,
        category="performance"
    ),
    "scheduler_delay_factor": VLLMParam(
        name="scheduler_delay_factor",
        type="float",
        default=0.0,
        description="调度延迟因子",
        min_value=0.0,
        category="performance"
    ),
    "enable_chunked_prefill": VLLMParam(
        name="enable_chunked_prefill",
        type="bool",
        default=True,
        description="启用分块预填充",
        category="performance"
    ),
    "enable_prefix_caching": VLLMParam(
        name="enable_prefix_caching",
        type="bool",
        default=True,
        description="启用前缀缓存",
        category="performance"
    ),
    
    # ========== 高级参数 ==========
    "seed": VLLMParam(
        name="seed",
        type="int",
        default=0,
        description="随机种子(0表示随机)",
        min_value=0,
        category="advanced"
    ),
    "enforce_eager": VLLMParam(
        name="enforce_eager",
        type="bool",
        default=False,
        description="强制Eager模式(禁用CUDA graph)",
        category="advanced"
    ),
    "trust_remote_code": VLLMParam(
        name="trust_remote_code",
        type="bool",
        default=True,
        description="信任远程代码",
        category="advanced"
    ),
    "load_format": VLLMParam(
        name="load_format",
        type="str",
        default="auto",
        description="模型加载格式",
        choices=["auto", "pt", "safetensors", "npcache", "dummy", "tensorizer", 
                "sharded_state", "gguf", "bitsandbytes", "mistral", "runai_streamer"],
        category="advanced"
    ),
    "config_format": VLLMParam(
        name="config_format",
        type="str",
        default="auto",
        description="配置格式",
        choices=["auto", "hf", "mistral"],
        category="advanced"
    ),
    "rope_scaling": VLLMParam(
        name="rope_scaling",
        type="str",
        default=None,
        description="RoPE缩放配置(JSON格式)",
        category="advanced"
    ),
    "rope_theta": VLLMParam(
        name="rope_theta",
        type="float",
        default=None,
        description="RoPE theta值",
        category="advanced"
    ),
    "tokenizer_mode": VLLMParam(
        name="tokenizer_mode",
        type="str",
        default="auto",
        description="分词器模式",
        choices=["auto", "slow", "mistral"],
        category="advanced"
    ),
    "guided_decoding_backend": VLLMParam(
        name="guided_decoding_backend",
        type="str",
        default="outlines",
        description="引导解码后端",
        choices=["outlines", "lm-format-enforcer", "xgrammar"],
        category="advanced"
    ),
    "distributed_executor_backend": VLLMParam(
        name="distributed_executor_backend",
        type="str",
        default="mp",
        description="分布式执行后端",
        choices=["ray", "mp"],
        category="advanced"
    ),
    "device": VLLMParam(
        name="device",
        type="str",
        default="auto",
        description="设备类型",
        choices=["auto", "cuda", "neuron", "cpu", "openvino", "tpu", "xpu", "hpu"],
        category="advanced"
    ),
    "preemption_mode": VLLMParam(
        name="preemption_mode",
        type="str",
        default=None,
        description="抢占模式",
        category="advanced"
    ),
    "scheduling_policy": VLLMParam(
        name="scheduling_policy",
        type="str",
        default="fcfs",
        description="调度策略",
        choices=["fcfs", "priority"],
        category="advanced"
    ),
    
    # ========== 日志参数 ==========
    "disable_log_stats": VLLMParam(
        name="disable_log_stats",
        type="bool",
        default=False,
        description="禁用统计日志",
        category="advanced"
    ),
    "disable_log_requests": VLLMParam(
        name="disable_log_requests",
        type="bool",
        default=False,
        description="禁用请求日志",
        category="advanced"
    ),
    "max_log_len": VLLMParam(
        name="max_log_len",
        type="int",
        default=None,
        description="最大日志长度",
        min_value=1,
        category="advanced"
    ),
    
    # ========== 推测解码参数 ==========
    "speculative_model": VLLMParam(
        name="speculative_model",
        type="str",
        default=None,
        description="推测解码模型路径",
        category="advanced"
    ),
    "num_speculative_tokens": VLLMParam(
        name="num_speculative_tokens",
        type="int",
        default=None,
        description="推测token数量",
        min_value=1,
        category="advanced"
    ),
    
    # ========== LoRA 参数 ==========
    "enable_lora": VLLMParam(
        name="enable_lora",
        type="bool",
        default=False,
        description="启用LoRA",
        category="advanced"
    ),
    "max_loras": VLLMParam(
        name="max_loras",
        type="int",
        default=1,
        description="最大LoRA数量",
        min_value=1,
        category="advanced"
    ),
    "max_lora_rank": VLLMParam(
        name="max_lora_rank",
        type="int",
        default=16,
        description="最大LoRA秩",
        min_value=1,
        category="advanced"
    ),
}


def get_vllm_param_categories() -> Dict[str, List[str]]:
    """获取参数分类"""
    categories = {
        "general": [],
        "performance": [],
        "quantization": [],
        "advanced": []
    }
    
    for name, param in VLLM_PARAMS.items():
        categories[param.category].append(name)
    
    return categories


def build_vllm_command_args(params: Dict[str, Any]) -> List[str]:
    """
    构建 vLLM 命令行参数
    
    Args:
        params: 参数字典
    
    Returns:
        命令行参数列表
    """
    args = []
    
    for name, value in params.items():
        if value is None:
            continue
        
        param_def = VLLM_PARAMS.get(name)
        if not param_def:
            continue
        
        # 处理布尔值
        if param_def.type == "bool":
            if value:
                args.append(f"--{name.replace('_', '-')}")
            else:
                # 对于某些参数，需要显式禁用
                if name in ["enable_chunked_prefill", "enable_prefix_caching", "trust_remote_code"]:
                    args.append(f"--no-{name.replace('_', '-')}")
        else:
            args.append(f"--{name.replace('_', '-')}")
            args.append(str(value))
    
    return args


def get_param_default_value(param_name: str) -> Any:
    """获取参数默认值"""
    param = VLLM_PARAMS.get(param_name)
    return param.default if param else None


def validate_param_value(param_name: str, value: Any) -> tuple[bool, str]:
    """
    验证参数值
    
    Returns:
        (是否有效, 错误信息)
    """
    param = VLLM_PARAMS.get(param_name)
    if not param:
        return False, f"未知参数: {param_name}"
    
    if value is None:
        return True, ""
    
    # 类型验证
    if param.type == "int":
        if not isinstance(value, int):
            return False, f"{param_name} 必须是整数"
    elif param.type == "float":
        if not isinstance(value, (int, float)):
            return False, f"{param_name} 必须是数字"
    elif param.type == "bool":
        if not isinstance(value, bool):
            return False, f"{param_name} 必须是布尔值"
    elif param.type == "str":
        if not isinstance(value, str):
            return False, f"{param_name} 必须是字符串"
    
    # 范围验证
    if param.min_value is not None and value < param.min_value:
        return False, f"{param_name} 不能小于 {param.min_value}"
    
    if param.max_value is not None and value > param.max_value:
        return False, f"{param_name} 不能大于 {param.max_value}"
    
    # 选项验证
    if param.choices is not None and value not in param.choices:
        return False, f"{param_name} 必须是以下值之一: {param.choices}"
    
    return True, ""
