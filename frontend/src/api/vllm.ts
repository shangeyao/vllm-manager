import axios from 'axios';
import type { Model, ModelInstance, NodeInfo, ClusterOverview, ModelDeployment, UsageStats, TokenTrend, CallDistribution, ModelStats } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Models API - 从 ModelScope 获取
export const getModels = async (): Promise<Model[]> => {
  const response = await api.get('/v1/models');
  return response.data;
};

export const getModelDetails = async (modelId: string): Promise<Model> => {
  const response = await api.get(`/v1/models/${modelId}`);
  return response.data;
};

// Model Instances API - 从真实后端获取
export const getModelInstances = async (): Promise<ModelInstance[]> => {
  const response = await api.get('/v1/instances');
  return response.data.map((instance: any) => ({
    ...instance,
    modelId: instance.model_id,
    createdAt: new Date(instance.created_at).toLocaleString('zh-CN'),
  }));
};

// Cluster API - 从真实后端获取
export const getClusterOverview = async (): Promise<ClusterOverview> => {
  const response = await api.get('/v1/cluster/overview');
  return response.data;
};

export const getModelDeployments = async (): Promise<ModelDeployment[]> => {
  const response = await api.get('/v1/deployments');
  return response.data;
};

export const getUsageStats = async (): Promise<UsageStats[]> => {
  const response = await api.get('/v1/stats/usage');
  return response.data;
};

export const getCallDistribution = async (): Promise<CallDistribution[]> => {
  const response = await api.get('/v1/stats/distribution');
  return response.data;
};

export const getTokenTrend = async (): Promise<TokenTrend[]> => {
  const response = await api.get('/v1/stats/trend');
  return response.data;
};

// Dashboard Stats API
export const getDashboardStats = async (): Promise<{ usageStats: UsageStats[]; callDistribution: CallDistribution[]; tokenTrend: TokenTrend[] }> => {
  const response = await api.get('/v1/stats/dashboard');
  const data = response.data;
  return {
    usageStats: data.usage_stats || [],
    callDistribution: data.call_distribution || [],
    tokenTrend: data.token_trend || [],
  };
};

// Nodes API - 从真实后端获取
export const getNodes = async (): Promise<NodeInfo[]> => {
  const response = await api.get('/v1/cluster/nodes');
  return response.data.map((node: any) => ({
    ...node,
    memoryUsed: node.memory_used,
    memoryTotal: node.memory_total,
  }));
};

// Model Registry API
export const registerModel = async (modelData: any): Promise<void> => {
  await api.post('/v1/models', modelData);
};

export const launchModel = async (modelId: string, params: any): Promise<void> => {
  await api.post('/v1/models/launch', { model_id: modelId, ...params });
};

export const stopModel = async (modelId: string): Promise<void> => {
  await api.post('/v1/models/stop', { model_id: modelId });
};

// Model Stats API - 从真实后端获取
export const getModelStats = async (timeRange: string): Promise<ModelStats> => {
  const response = await api.get(`/v1/stats?range=${timeRange}`);
  const data = response.data;
  
  // 转换后端数据格式到前端格式
  return {
    overview: {
      totalCalls: data.overview.total_calls,
      callsTrend: data.overview.calls_trend,
      totalTokens: data.overview.total_tokens,
      tokensTrend: data.overview.tokens_trend,
      avgLatency: data.overview.avg_latency,
      p99Latency: data.overview.p99_latency,
      successRate: data.overview.success_rate,
      failedCalls: data.overview.failed_calls,
      activeUsers: data.overview.active_users,
      usersTrend: data.overview.users_trend,
    },
    dailyTrend: data.daily_trend.map((item: any) => ({
      date: item.date,
      calls: item.calls,
    })),
    latencyDistribution: data.latency_distribution.map((item: any) => ({
      time: item.time,
      p50: item.p50,
      p95: item.p95,
      p99: item.p99,
    })),
    tokenDistribution: data.token_distribution.map((item: any) => ({
      model: item.model,
      input: item.input,
      output: item.output,
    })),
    modelTypeDistribution: data.model_type_distribution.map((item: any) => ({
      name: item.name,
      value: item.value,
    })),
    errorDistribution: data.error_distribution.map((item: any) => ({
      type: item.type,
      count: item.count,
      percentage: item.percentage,
    })),
  };
};

// vLLM代理API
export const createChatCompletion = async (request: {
  model: string;
  messages: { role: string; content: string }[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}) => {
  const response = await api.post('/v1/chat/completions', request);
  return response.data;
};

export const createCompletion = async (request: {
  model: string;
  prompt: string;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}) => {
  const response = await api.post('/v1/completions', request);
  return response.data;
};

export const createEmbedding = async (request: {
  model: string;
  input: string;
}) => {
  const response = await api.post('/v1/embeddings', request);
  return response.data;
};

// Deploy Model API
export const deployModel = async (params: {
  modelName: string;
  modelId?: string;
  quantization?: string;
  tensorParallelSize?: number;
  gpuMemoryUtilization?: number;
  maxModelLen?: number;
  dtype?: string;
  gpuIndices?: number[];
  swapSpace?: number;
  enforceEager?: boolean;
  enableChunkedPrefill?: boolean;
  maxNumSeqs?: number;
  maxNumBatchedTokens?: number;
  seed?: number;
}) => {
  const response = await api.post('/v1/models/deploy', params);
  return response.data;
};

// Model Download API
export const downloadModel = async (modelId: string): Promise<{ success: boolean; status: string; progress: number; message?: string; local_path?: string }> => {
  const response = await api.post('/v1/models/download', { model_id: modelId });
  return response.data;
};

export const getDownloadStatus = async (modelId: string): Promise<{ model_id: string; status: string; progress: number; current_file?: string; error_message?: string; local_path?: string }> => {
  const response = await api.get('/v1/models/download/status', { params: { model_id: modelId } });
  return response.data;
};

export const listCachedModels = async (): Promise<{ success: boolean; models: any[]; count: number }> => {
  const response = await api.get('/v1/models/cached');
  return response.data;
};

export const deleteCachedModel = async (modelId: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete('/v1/models/cached', { data: { model_id: modelId } });
  return response.data;
};

// Refresh Model List API
export const refreshModelList = async (params?: {
  searchQuery?: string;
}): Promise<{ success: boolean; message: string; count: number; source?: string }> => {
  const response = await api.post('/v1/models/refresh', params || {});
  return response.data;
};

// Model Instance Operations API
export const startInstance = async (instanceId: string): Promise<{ success: boolean; message: string; instance_id: string }> => {
  const response = await api.post(`/v1/instances/${instanceId}/start`);
  return response.data;
};

export const stopInstance = async (instanceId: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`/v1/instances/${instanceId}/stop`);
  return response.data;
};

export const restartInstance = async (instanceId: string): Promise<{ success: boolean; message: string; instance_id: string }> => {
  const response = await api.post(`/v1/instances/${instanceId}/restart`);
  return response.data;
};

export const deleteInstance = async (instanceId: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete(`/v1/instances/${instanceId}`);
  return response.data;
};
