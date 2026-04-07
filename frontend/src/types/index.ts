export interface ModelSpec {
  model_format: string;
  model_size_in_billions?: number;
  quantizations: string[];
  model_id?: string;
  model_revision?: string;
  model_hub?: string;
}

export interface Model {
  id: string;
  name: string;
  description?: string;
  type: 'llm' | 'embedding' | 'rerank' | 'audio' | 'image' | 'video' | 'multimodal';
  status?: 'running' | 'stopped' | 'pending' | 'error';
  size?: string;
  language?: string[];
  abilities?: string[];
  format?: string;
  quantization?: string;
  contextLength?: number;
  cached?: boolean;
  node?: string;
  gpu?: string[];
  tokens?: string;
  calls?: string;
  latency?: string;
  createdAt?: string;
  specs?: ModelSpec[];
}

export interface ModelInstance {
  id: string;
  name: string;
  modelName: string;
  modelId?: string;
  modelType: string;
  status: 'running' | 'stopped' | 'pending' | 'error';
  version: string;
  createdAt: string;
  replicas: number;
  gpus: string[];
  config?: Record<string, any>;
  replicas_detail?: {
    id: string;
    node: string;
    gpu: string;
  }[];
}

export interface GPUInfo {
  id: string;
  name: string;
  index: number;
  utilization: number;
  memoryUsed: number;
  memoryTotal: number;
  temperature: number;
  power: number;
}

export interface NodeInfo {
  id: string;
  name: string;
  ip: string;
  status: 'online' | 'offline';
  cpu: number;
  memoryUsed: number;
  memoryTotal: number;
  gpus: GPUInfo[];
}

export interface ClusterOverview {
  nodes: {
    total: number;
    online: number;
  };
  gpus: {
    total: number;
    available: number;
  };
  memory: {
    total: number;
    used: number;
  };
  avgUtilization: number;
}

export interface ModelDeployment {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'pending';
  node: string;
  gpus: string[];
  tokens: string;
  calls: string;
  latency: string;
}

export interface UsageStats {
  modelName: string;
  usage: number;
}

export interface TokenTrend {
  date: string;
  models: {
    [key: string]: number;
  };
}

export interface CallDistribution {
  name: string;
  value: number;
}

export interface ModelStats {
  overview: {
    totalCalls: string;
    callsTrend: number;
    totalTokens: string;
    tokensTrend: number;
    avgLatency: number;
    p99Latency: number;
    successRate: number;
    failedCalls: number;
    activeUsers: number;
    usersTrend: number;
  };
  dailyTrend: {
    date: string;
    calls: number;
  }[];
  latencyDistribution: {
    time: string;
    p50: number;
    p95: number;
    p99: number;
  }[];
  tokenDistribution: {
    model: string;
    input: number;
    output: number;
  }[];
  modelTypeDistribution: {
    name: string;
    value: number;
  }[];
  errorDistribution: {
    type: string;
    count: number;
    percentage: number;
  }[];
}
