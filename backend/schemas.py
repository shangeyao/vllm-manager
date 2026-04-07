from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# Model Schemas
class ModelSpecInfo(BaseModel):
    model_format: str
    model_size_in_billions: Optional[float] = None
    quantizations: List[str] = ["none"]
    model_id: Optional[str] = None
    model_revision: Optional[str] = None
    model_hub: str = "modelscope"


class ModelInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: str
    status: Optional[str] = None
    size: Optional[str] = None
    language: Optional[List[str]] = None
    abilities: Optional[List[str]] = None
    format: Optional[str] = None
    quantization: Optional[str] = None
    context_length: Optional[int] = None
    cached: bool = False
    specs: Optional[List[ModelSpecInfo]] = None


class ModelInstanceCreate(BaseModel):
    name: str
    model_name: str
    model_id: Optional[str] = None
    model_type: str = "llm"
    replicas: int = 1
    gpus: List[str] = []
    config: Dict[str, Any] = {}


class ModelInstanceResponse(BaseModel):
    id: str
    name: str
    model_name: str
    model_id: Optional[str]
    model_type: str
    status: str
    version: Optional[str]
    created_at: datetime
    replicas: int
    gpus: List[str]
    config: Optional[Dict[str, Any]]
    node: Optional[str]
    
    class Config:
        from_attributes = True


# GPU Schemas
class GPUInfo(BaseModel):
    id: str
    name: str
    index: int
    utilization: float
    memory_used: float
    memory_total: float
    temperature: float
    power: float


class NodeInfo(BaseModel):
    id: str
    name: str
    ip: str
    status: str
    cpu: float
    memory_used: float
    memory_total: float
    gpus: List[GPUInfo]


# Cluster Schemas
class ClusterOverview(BaseModel):
    nodes: Dict[str, int]
    gpus: Dict[str, int]
    memory: Dict[str, float]
    avg_utilization: float


class ModelDeployment(BaseModel):
    id: str
    name: str
    status: str
    node: str
    gpus: List[str]
    tokens: str
    calls: str
    latency: str


# Stats Schemas
class StatsOverview(BaseModel):
    total_calls: str
    calls_trend: float
    total_tokens: str
    tokens_trend: float
    avg_latency: float
    p99_latency: float
    success_rate: float
    failed_calls: int
    active_users: int
    users_trend: float


class DailyTrend(BaseModel):
    date: str
    calls: int


class LatencyDistribution(BaseModel):
    time: str
    p50: float
    p95: float
    p99: float


class TokenDistribution(BaseModel):
    model: str
    input: int
    output: int


class ModelTypeDistribution(BaseModel):
    name: str
    value: int


class ErrorDistribution(BaseModel):
    type: str
    count: int
    percentage: float


class ModelStats(BaseModel):
    overview: StatsOverview
    daily_trend: List[DailyTrend]
    latency_distribution: List[LatencyDistribution]
    token_distribution: List[TokenDistribution]
    model_type_distribution: List[ModelTypeDistribution]
    error_distribution: List[ErrorDistribution]


# Request/Response Schemas
class ChatRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class EmbeddingRequest(BaseModel):
    model: str
    input: str


class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


# Dashboard Stats Schemas
class UsageStats(BaseModel):
    model_name: str
    usage: int


class TokenTrend(BaseModel):
    date: str
    value: int


class CallDistribution(BaseModel):
    name: str
    value: int


class DashboardStats(BaseModel):
    usage_stats: List[UsageStats]
    call_distribution: List[CallDistribution]
    token_trend: List[TokenTrend]


# System Management Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    status: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    name: str
    permissions: List[str] = []
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key: Optional[str] = None  # 仅在创建时返回
    user_id: str
    permissions: List[str]
    status: str
    last_used_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SystemConfigItem(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemOverview(BaseModel):
    version: str
    uptime: str
    database_status: str
    storage_used: float
    storage_total: float
    cpu_usage: float
    memory_usage: float
    active_models: int
    total_requests: int
