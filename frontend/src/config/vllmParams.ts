/**
 * vLLM 参数配置
 * 包含所有 vLLM api_server 支持的参数
 */

export interface VLLMParam {
  name: string
  type: 'int' | 'float' | 'bool' | 'str' | 'select'
  default: any
  description: string
  choices?: string[]
  min?: number
  max?: number
  category: 'basic' | 'performance' | 'quantization' | 'advanced' | 'lora' | 'speculative'
}

export const VLLM_PARAMS: Record<string, VLLMParam> = {
  // ========== 基本参数 ==========
  tensorParallelSize: {
    name: 'tensorParallelSize',
    type: 'int',
    default: 1,
    description: '张量并行大小（GPU数量）',
    min: 1,
    max: 8,
    category: 'basic',
  },
  gpuMemoryUtilization: {
    name: 'gpuMemoryUtilization',
    type: 'float',
    default: 0.9,
    description: 'GPU内存利用率',
    min: 0,
    max: 1,
    category: 'basic',
  },
  maxModelLen: {
    name: 'maxModelLen',
    type: 'int',
    default: undefined,
    description: '最大模型上下文长度',
    min: 1,
    category: 'basic',
  },
  quantization: {
    name: 'quantization',
    type: 'select',
    default: undefined,
    description: '量化方式',
    choices: ['aqlm', 'awq', 'deepspeedfp', 'tpu_int8', 'fp8', 'fbgemm_fp8', 'modelopt', 'marlin', 'gguf', 'gptq_marlin_24', 'gptq_marlin', 'awq_marlin', 'gptq', 'compressed-tensors', 'bitsandbytes', 'qqq', 'hqq', 'experts_int8', 'neuron_quant', 'ipex'],
    category: 'quantization',
  },
  dtype: {
    name: 'dtype',
    type: 'select',
    default: 'auto',
    description: '数据类型',
    choices: ['auto', 'half', 'float16', 'bfloat16', 'float', 'float32'],
    category: 'basic',
  },

  // ========== 性能参数 ==========
  kvCacheDtype: {
    name: 'kvCacheDtype',
    type: 'select',
    default: 'auto',
    description: 'KV Cache 数据类型',
    choices: ['auto', 'fp8', 'fp8_e5m2', 'fp8_e4m3'],
    category: 'performance',
  },
  blockSize: {
    name: 'blockSize',
    type: 'select',
    default: 16,
    description: 'Token块大小',
    choices: ['8', '16', '32', '64', '128'],
    category: 'performance',
  },
  swapSpace: {
    name: 'swapSpace',
    type: 'float',
    default: 4,
    description: 'CPU交换空间(GB)',
    min: 0,
    category: 'performance',
  },
  cpuOffloadGb: {
    name: 'cpuOffloadGb',
    type: 'float',
    default: 0,
    description: 'CPU卸载空间(GB)',
    min: 0,
    category: 'performance',
  },
  maxNumBatchedTokens: {
    name: 'maxNumBatchedTokens',
    type: 'int',
    default: undefined,
    description: '最大批处理token数',
    min: 1,
    category: 'performance',
  },
  maxNumSeqs: {
    name: 'maxNumSeqs',
    type: 'int',
    default: 256,
    description: '最大并发序列数',
    min: 1,
    category: 'performance',
  },
  maxParallelLoadingWorkers: {
    name: 'maxParallelLoadingWorkers',
    type: 'int',
    default: undefined,
    description: '最大并行加载工作线程数',
    min: 1,
    category: 'performance',
  },
  pipelineParallelSize: {
    name: 'pipelineParallelSize',
    type: 'int',
    default: 1,
    description: '流水线并行大小',
    min: 1,
    category: 'performance',
  },
  numSchedulerSteps: {
    name: 'numSchedulerSteps',
    type: 'int',
    default: 1,
    description: '调度器步数',
    min: 1,
    category: 'performance',
  },
  schedulerDelayFactor: {
    name: 'schedulerDelayFactor',
    type: 'float',
    default: 0,
    description: '调度延迟因子',
    min: 0,
    category: 'performance',
  },
  enableChunkedPrefill: {
    name: 'enableChunkedPrefill',
    type: 'bool',
    default: true,
    description: '启用分块预填充',
    category: 'performance',
  },
  enablePrefixCaching: {
    name: 'enablePrefixCaching',
    type: 'bool',
    default: true,
    description: '启用前缀缓存',
    category: 'performance',
  },

  // ========== 高级参数 ==========
  seed: {
    name: 'seed',
    type: 'int',
    default: 0,
    description: '随机种子(0表示随机)',
    min: 0,
    category: 'advanced',
  },
  enforceEager: {
    name: 'enforceEager',
    type: 'bool',
    default: false,
    description: '强制Eager模式(禁用CUDA graph)',
    category: 'advanced',
  },
  trustRemoteCode: {
    name: 'trustRemoteCode',
    type: 'bool',
    default: true,
    description: '信任远程代码',
    category: 'advanced',
  },
  loadFormat: {
    name: 'loadFormat',
    type: 'select',
    default: 'auto',
    description: '模型加载格式',
    choices: ['auto', 'pt', 'safetensors', 'npcache', 'dummy', 'tensorizer', 'sharded_state', 'gguf', 'bitsandbytes', 'mistral', 'runai_streamer'],
    category: 'advanced',
  },
  configFormat: {
    name: 'configFormat',
    type: 'select',
    default: 'auto',
    description: '配置格式',
    choices: ['auto', 'hf', 'mistral'],
    category: 'advanced',
  },
  ropeScaling: {
    name: 'ropeScaling',
    type: 'str',
    default: undefined,
    description: 'RoPE缩放配置(JSON格式)',
    category: 'advanced',
  },
  ropeTheta: {
    name: 'ropeTheta',
    type: 'float',
    default: undefined,
    description: 'RoPE theta值',
    category: 'advanced',
  },
  tokenizerMode: {
    name: 'tokenizerMode',
    type: 'select',
    default: 'auto',
    description: '分词器模式',
    choices: ['auto', 'slow', 'mistral'],
    category: 'advanced',
  },
  guidedDecodingBackend: {
    name: 'guidedDecodingBackend',
    type: 'select',
    default: 'outlines',
    description: '引导解码后端',
    choices: ['outlines', 'lm-format-enforcer', 'xgrammar'],
    category: 'advanced',
  },
  distributedExecutorBackend: {
    name: 'distributedExecutorBackend',
    type: 'select',
    default: 'mp',
    description: '分布式执行后端',
    choices: ['ray', 'mp'],
    category: 'advanced',
  },
  device: {
    name: 'device',
    type: 'select',
    default: 'auto',
    description: '设备类型',
    choices: ['auto', 'cuda', 'neuron', 'cpu', 'openvino', 'tpu', 'xpu', 'hpu'],
    category: 'advanced',
  },
  schedulingPolicy: {
    name: 'schedulingPolicy',
    type: 'select',
    default: 'fcfs',
    description: '调度策略',
    choices: ['fcfs', 'priority'],
    category: 'advanced',
  },

  // ========== 日志参数 ==========
  disableLogStats: {
    name: 'disableLogStats',
    type: 'bool',
    default: false,
    description: '禁用统计日志',
    category: 'advanced',
  },
  disableLogRequests: {
    name: 'disableLogRequests',
    type: 'bool',
    default: false,
    description: '禁用请求日志',
    category: 'advanced',
  },
  maxLogLen: {
    name: 'maxLogLen',
    type: 'int',
    default: undefined,
    description: '最大日志长度',
    min: 1,
    category: 'advanced',
  },

  // ========== 推测解码参数 ==========
  speculativeModel: {
    name: 'speculativeModel',
    type: 'str',
    default: undefined,
    description: '推测解码模型路径',
    category: 'speculative',
  },
  numSpeculativeTokens: {
    name: 'numSpeculativeTokens',
    type: 'int',
    default: undefined,
    description: '推测token数量',
    min: 1,
    category: 'speculative',
  },

  // ========== LoRA 参数 ==========
  enableLora: {
    name: 'enableLora',
    type: 'bool',
    default: false,
    description: '启用LoRA',
    category: 'lora',
  },
  maxLoras: {
    name: 'maxLoras',
    type: 'int',
    default: 1,
    description: '最大LoRA数量',
    min: 1,
    category: 'lora',
  },
  maxLoraRank: {
    name: 'maxLoraRank',
    type: 'int',
    default: 16,
    description: '最大LoRA秩',
    min: 1,
    category: 'lora',
  },
}

// 按分类获取参数
export const getParamsByCategory = (category: string): VLLMParam[] => {
  return Object.values(VLLM_PARAMS).filter((param) => param.category === category)
}

// 获取所有参数分类
export const PARAM_CATEGORIES = [
  { key: 'basic', label: '基本配置' },
  { key: 'performance', label: '性能优化' },
  { key: 'quantization', label: '量化设置' },
  { key: 'advanced', label: '高级选项' },
  { key: 'lora', label: 'LoRA配置' },
  { key: 'speculative', label: '推测解码' },
]

// 获取参数的默认值
export const getParamDefaultValue = (paramName: string): any => {
  const param = VLLM_PARAMS[paramName]
  return param ? param.default : undefined
}
