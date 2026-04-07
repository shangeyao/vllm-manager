# vLLM Manager - Code Wiki

## 📚 目录

1. [项目概述](#项目概述)
2. [整体架构](#整体架构)
3. [技术栈](#技术栈)
4. [目录结构](#目录结构)
5. [后端模块详解](#后端模块详解)
   - [核心模块](#核心模块)
   - [客户端模块](#客户端模块)
   - [路由模块](#路由模块)
6. [前端模块详解](#前端模块详解)
7. [数据库设计](#数据库设计)
8. [API接口文档](#api接口文档)
9. [依赖关系](#依赖关系)
10. [项目运行方式](#项目运行方式)
11. [配置说明](#配置说明)

---

## 项目概述

**vLLM Manager** 是一个开源的大语言模型（LLM）部署和管理平台，基于 [vLLM](https://github.com/vllm-project/vllm) 和 [ModelScope](https://www.modelscope.cn/) 构建。它提供了直观的 Web 界面，让用户可以轻松地搜索、下载、部署和管理各种开源大语言模型。

### 核心功能

| 功能模块 | 描述 |
|---------|------|
| 🚀 模型仓库 | 从 ModelScope 搜索和浏览模型，支持一键下载和缓存管理 |
| ⚡ 模型部署 | 一键部署 vLLM 推理服务，可视化配置 GPU、量化等参数 |
| 📊 监控统计 | GPU 使用率、显存占用实时监控，模型调用统计 |
| 🌐 OpenAI 兼容 | 提供 OpenAI 兼容的 API 接口 |
| 💻 现代化 UI | 基于 React + Ant Design 的响应式界面 |

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Dashboard │ │ModelStore│ │Instances │ │  Stats   │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                   │
│       └────────────┴────────────┴────────────┘                   │
│                          │ Axios HTTP                            │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Routers Layer                          │   │
│  │  ┌────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌───────┐│   │
│  │  │models  │ │instances │ │cluster │ │ stats  │ │system ││   │
│  │  └───┬────┘ └────┬─────┘ └───┬────┘ └───┬────┘ └───┬───┘│   │
│  └──────┼───────────┼───────────┼───────────┼───────────┼────┘   │
│         │           │           │           │           │        │
│  ┌──────┴───────────┴───────────┴───────────┴───────────┴────┐   │
│  │                    Clients Layer                           │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────┐ │   │
│  │  │ModelScope   │ │HuggingFace  │ │   vLLM Client        │ │   │
│  │  │Client       │ │Client       │ │   + Process Manager  │ │   │
│  │  └─────────────┘ └─────────────┘ └──────────────────────┘ │   │
│  └────────────────────────────────────────────────────────────┘   │
│         │                    │                    │                │
│         ▼                    ▼                    ▼                │
│  ┌─────────────┐     ┌─────────────┐     ┌──────────────────┐     │
│  │  Database   │     │  Monitor    │     │  vLLM Instances  │     │
│  │ (SQLite/    │     │  (GPU/System│     │  (Subprocesses)  │     │
│  │  MySQL)     │     │   Metrics)  │     │                  │     │
│  └─────────────┘     └─────────────┘     └──────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   ModelScope / HuggingFace   │
              │   (Model Repository)   │
              └────────────────────────┘
```

---

## 技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 编程语言 |
| FastAPI | 0.109+ | 高性能 Web 框架 |
| SQLAlchemy | 2.0+ | ORM 数据库管理 |
| Pydantic | 2.5+ | 数据验证 |
| httpx | 0.26+ | 异步 HTTP 客户端 |
| pynvml | 11.5+ | NVIDIA GPU 监控 |
| psutil | 5.9+ | 系统监控 |
| uvicorn | 0.27+ | ASGI 服务器 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2+ | UI 框架 |
| TypeScript | 5.2+ | 类型安全 |
| Vite | 5.0+ | 构建工具 |
| Ant Design | 5.12+ | UI 组件库 |
| Axios | 1.6+ | HTTP 客户端 |
| ECharts | 5.4+ | 数据可视化 |
| Zustand | 4.4+ | 状态管理 |
| React Router | 6.20+ | 路由管理 |

---

## 目录结构

```
vllm-manager/
├── backend/                      # 后端代码
│   ├── clients/                  # 客户端模块
│   │   ├── __init__.py          # 模块导出
│   │   ├── base.py              # 抽象基类定义
│   │   ├── modelscope.py        # ModelScope 客户端
│   │   ├── huggingface.py       # HuggingFace 客户端
│   │   ├── vllm.py              # vLLM 客户端和进程管理
│   │   └── utils.py             # 工具函数
│   ├── routers/                  # API 路由模块
│   │   ├── __init__.py          # 路由导出
│   │   ├── models.py            # 模型管理路由
│   │   ├── instances.py         # 实例管理路由
│   │   ├── downloads.py         # 下载管理路由
│   │   ├── cluster.py           # 集群管理路由
│   │   ├── stats.py             # 统计信息路由
│   │   ├── proxy.py             # API 代理路由
│   │   └── system.py            # 系统管理路由
│   ├── main.py                   # FastAPI 应用入口
│   ├── config.py                 # 配置管理
│   ├── models.py                 # 数据库模型定义
│   ├── schemas.py                # Pydantic 数据模型
│   ├── monitor.py                # GPU/系统监控
│   ├── vllm_params.py            # vLLM 参数定义
│   ├── builtin_models.py         # 内置模型列表
│   ├── modelscope_downloader.py  # 模型下载器
│   ├── requirements.txt          # Python 依赖
│   └── Dockerfile                # 后端 Docker 镜像
│
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── api/                  # API 接口封装
│   │   │   ├── system.ts        # 系统 API
│   │   │   └── vllm.ts          # vLLM API
│   │   ├── components/           # React 组件
│   │   │   ├── Header.tsx       # 顶部导航
│   │   │   ├── Sidebar.tsx      # 侧边栏
│   │   │   ├── ModelChatTest.tsx # 模型测试组件
│   │   │   ├── ModelLaunchLog.tsx # 启动日志组件
│   │   │   └── VLLMParamsForm.tsx # vLLM 参数表单
│   │   ├── pages/                # 页面组件
│   │   │   ├── Dashboard.tsx    # 仪表盘
│   │   │   ├── ModelStore.tsx   # 模型仓库
│   │   │   ├── ModelRegister.tsx # 模型注册
│   │   │   ├── ModelInstances.tsx # 实例管理
│   │   │   ├── DeviceInfo.tsx   # 设备信息
│   │   │   ├── ModelStats.tsx   # 统计分析
│   │   │   └── SystemManagement.tsx # 系统管理
│   │   ├── types/                # TypeScript 类型定义
│   │   │   └── index.ts
│   │   ├── config/               # 配置文件
│   │   │   └── vllmParams.ts    # vLLM 参数配置
│   │   ├── App.tsx               # 应用入口
│   │   ├── App.css               # 全局样式
│   │   ├── main.tsx              # React 入口
│   │   └── index.css             # 基础样式
│   ├── public/                   # 静态资源
│   ├── package.json              # NPM 配置
│   ├── tsconfig.json             # TypeScript 配置
│   ├── vite.config.ts            # Vite 配置
│   └── Dockerfile                # 前端 Docker 镜像
│
├── docs/                         # 文档目录
│   ├── ARCHITECTURE.md          # 架构文档
│   ├── DEPLOYMENT.md            # 部署文档
│   └── images/                   # 文档图片
│
├── scripts/                      # 脚本目录
│   ├── build.sh                  # 构建脚本
│   └── deploy.sh                 # 部署脚本
│
├── docker-compose.yml            # Docker Compose 配置
└── README.md                     # 项目说明
```

---

## 后端模块详解

### 核心模块

#### 1. main.py - 应用入口

**职责**: FastAPI 应用初始化和生命周期管理

**关键组件**:
- `lifespan()`: 应用生命周期管理，启动时初始化数据库和监控，关闭时清理资源
- `app`: FastAPI 应用实例，配置 CORS、路由等

**代码结构**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    init_db()
    metrics_collector.register_callback(save_metrics)
    metrics_task = asyncio.create_task(metrics_collector.collect_loop(interval=10))
    yield
    # 关闭时清理
    metrics_collector.stop()
    await vllm_client.close()
```

**路由注册**:
| 路由 | 前缀 | 描述 |
|------|------|------|
| models_router | /api/v1/models | 模型管理 |
| instances_router | /api/v1/instances | 实例管理 |
| downloads_router | /api/v1/models | 下载管理 |
| cluster_router | /api/v1/cluster | 集群管理 |
| stats_router | /api/v1/stats | 统计信息 |
| system_router | /api/v1/system | 系统管理 |
| proxy_router | / | OpenAI 兼容代理 |

---

#### 2. config.py - 配置管理

**职责**: 集中管理应用配置，支持环境变量和 .env 文件

**关键类**: `Settings`

**配置项分类**:

| 类别 | 配置项 | 默认值 | 描述 |
|------|--------|--------|------|
| API | API_V1_STR | /api/v1 | API 前缀 |
| | PROJECT_NAME | vLLM Manager | 项目名称 |
| Server | HOST | 0.0.0.0 | 服务地址 |
| | PORT | 8000 | 服务端口 |
| vLLM | VLLM_BASE_URL | http://localhost:8001 | vLLM 服务地址 |
| | VLLM_PORT_RANGE_START | 8001 | 实例端口范围起始 |
| | VLLM_PORT_RANGE_END | 8100 | 实例端口范围结束 |
| Database | DB_TYPE | sqlite | 数据库类型 |
| | DATABASE_URL | None | 数据库连接 URL |
| Model Cache | MODEL_CACHE_DIR | ~/.cache/vllm-manager/models | 模型缓存目录 |

**数据库连接方法**:
```python
def get_database_url(self) -> str:
    if self.DATABASE_URL:
        return self.DATABASE_URL
    if self.DB_TYPE == "mysql":
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@..."
    elif self.DB_TYPE == "postgresql":
        return f"postgresql://..."
    else:
        return "sqlite:///./vllm_manager.db"
```

---

#### 3. models.py - 数据库模型

**职责**: 定义 SQLAlchemy ORM 模型

**数据模型**:

| 模型 | 表名 | 描述 |
|------|------|------|
| ModelInstance | model_instances | 模型实例 |
| RequestLog | request_logs | 请求日志 |
| GPUStats | gpu_stats | GPU 统计 |
| NodeInfo | nodes | 节点信息 |
| User | users | 用户 |
| Role | roles | 角色 |
| ApiKey | api_keys | API 密钥 |
| SystemConfig | system_config | 系统配置 |

**ModelInstance 详细字段**:
```python
class ModelInstance(Base):
    id = Column(String, primary_key=True)          # 实例 ID
    name = Column(String)                           # 实例名称
    model_name = Column(String)                     # 模型名称
    model_type = Column(String)                     # 模型类型
    status = Column(String, default="stopped")      # 状态
    replicas = Column(Integer, default=1)           # 副本数
    gpus = Column(JSON)                             # GPU 列表
    config = Column(JSON)                           # 配置信息
    node = Column(String)                           # 节点
```

---

#### 4. schemas.py - 数据验证模型

**职责**: 定义 Pydantic 数据模型用于请求/响应验证

**主要模型**:

| 模型 | 用途 |
|------|------|
| ModelInfo | 模型信息 |
| ModelInstanceCreate | 创建实例请求 |
| ModelInstanceResponse | 实例响应 |
| GPUInfo | GPU 信息 |
| NodeInfo | 节点信息 |
| ClusterOverview | 集群概览 |
| ModelStats | 模型统计 |
| DashboardStats | 仪表盘统计 |
| UserCreate/Response | 用户相关 |
| ApiKeyCreate/Response | API 密钥相关 |

---

#### 5. monitor.py - 系统监控

**职责**: GPU 和系统资源监控

**关键类**:

##### GPUMonitor
使用 pynvml 获取真实 GPU 信息

```python
class GPUMonitor:
    def get_gpu_count(self) -> int
    def get_gpu_info(self, index: int) -> Dict[str, Any]
    def get_all_gpus(self) -> List[Dict[str, Any]]
```

**返回的 GPU 信息**:
- id: GPU 标识
- name: GPU 名称
- index: GPU 索引
- utilization: 利用率
- memory_used/total: 显存使用/总量
- temperature: 温度
- power: 功耗

##### SystemMonitor
使用 psutil 获取系统信息

```python
class SystemMonitor:
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]
    @staticmethod
    def get_memory_info() -> Dict[str, Any]
    @staticmethod
    def get_disk_info() -> Dict[str, Any]
    @staticmethod
    def get_network_info() -> Dict[str, Any]
    @classmethod
    def get_system_overview(cls) -> Dict[str, Any]
```

##### MetricsCollector
指标收集器，定期收集并存储指标

```python
class MetricsCollector:
    def register_callback(self, callback)      # 注册回调
    async def collect_loop(self, interval=5)   # 收集循环
    def collect_metrics(self) -> Dict[str, Any]
    def stop(self)
```

---

#### 6. vllm_params.py - vLLM 参数定义

**职责**: 定义所有 vLLM 支持的参数及其验证规则

**参数数据类**:
```python
@dataclass
class VLLMParam:
    name: str                    # 参数名
    type: str                    # 类型
    default: Any                 # 默认值
    description: str             # 描述
    choices: Optional[List[str]] # 可选值
    min_value: Optional[float]   # 最小值
    max_value: Optional[float]   # 最大值
    category: str                # 分类
```

**参数分类**:

| 分类 | 参数示例 |
|------|----------|
| general | tensor_parallel_size, gpu_memory_utilization, max_model_len, dtype |
| performance | kv_cache_dtype, block_size, swap_space, max_num_seqs |
| quantization | quantization (支持 awq, gptq, fp8 等) |
| advanced | seed, enforce_eager, trust_remote_code, load_format |

**工具函数**:
```python
def build_vllm_command_args(params: Dict[str, Any]) -> List[str]
def get_param_default_value(param_name: str) -> Any
def validate_param_value(param_name: str, value: Any) -> tuple[bool, str]
```

---

#### 7. builtin_models.py - 内置模型列表

**职责**: 预定义 vLLM 支持的所有模型及其配置

**模型数据结构**:
```python
class ModelSpec(BaseModel):
    model_format: str           # pytorch, gguf, awq, gptq
    model_size_in_billions: float
    quantizations: List[str]
    model_id: str               # ModelScope model id
    model_revision: str
    model_hub: str = "modelscope"

class ModelFamily(BaseModel):
    model_name: str
    model_description: str
    model_type: str             # llm, embedding, rerank, multimodal
    model_family: str
    model_specs: List[ModelSpec]
    context_length: int
    languages: List[str]
    abilities: List[str]        # chat, generate, vision, tools
```

**支持的模型家族**:
- LLaMA 系列 (llama-2, llama-3, llama-3.1)
- Qwen 系列 (qwen2, qwen2.5, qwen2.5-coder, qwen2-vl, qwen3)
- ChatGLM 系列 (chatglm3, glm-4)
- DeepSeek 系列 (deepseek, deepseek-coder)
- Mistral/Mixtral
- Yi 系列
- Embedding 模型 (bge, e5, gte)
- 多模态模型 (llava, cogvlm, internvl)

---

#### 8. modelscope_downloader.py - 模型下载器

**职责**: 从 ModelScope 下载模型到本地缓存

**关键类**:

##### ModelDownloadTask
```python
class ModelDownloadTask:
    model_id: str
    local_path: str
    status: str          # pending, downloading, completed, failed
    progress: float
    error_message: str
    total_files: int
    downloaded_files: int
    current_file: str
```

##### ModelScopeDownloader
```python
class ModelScopeDownloader:
    def get_model_local_path(self, model_id: str) -> str
    def is_model_cached(self, model_id: str) -> bool
    def download_model(self, model_id: str, progress_callback) -> ModelDownloadTask
    def get_download_task(self, model_id: str) -> ModelDownloadTask
    def list_cached_models(self) -> list
    def delete_model(self, model_id: str) -> bool
```

**下载策略**:
1. 优先使用 ModelScope SDK 的 `snapshot_download`
2. 失败时回退到 Git LFS 克隆

---

### 客户端模块

#### 1. base.py - 抽象基类

**职责**: 定义客户端接口的统一抽象

**抽象类**:

##### ModelSourceClient
模型源客户端基类（ModelScope, HuggingFace 等）

```python
class ModelSourceClient(ABC):
    @abstractmethod
    async def search_models(...) -> List[ModelInfo]
    @abstractmethod
    async def get_model_detail(self, model_id: str) -> Optional[ModelInfo]
    @abstractmethod
    async def get_popular_models(self, limit: int) -> List[ModelInfo]
    @abstractmethod
    async def get_models_by_organization(self, organization: str) -> List[ModelInfo]
```

##### InferenceClient
推理引擎客户端基类（vLLM 等）

```python
class InferenceClient(ABC):
    @abstractmethod
    async def get_models(self) -> List[Dict]
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[Dict]
    @abstractmethod
    async def create_chat_completion(...) -> Dict
    @abstractmethod
    async def create_completion(...) -> Dict
    @abstractmethod
    async def create_embedding(...) -> Dict
    @abstractmethod
    async def stream_chat_completion(...) -> AsyncGenerator
    @abstractmethod
    async def check_health(self) -> bool
```

**数据类**:
- `ModelType`: 模型类型枚举 (LLM, EMBEDDING, MULTIMODAL 等)
- `ModelAbility`: 模型能力枚举 (CHAT, GENERATE, CODE, VISION 等)
- `ModelSpec`: 模型规格信息
- `ModelInfo`: 统一的模型信息结构

---

#### 2. modelscope.py - ModelScope 客户端

**职责**: 与 ModelScope API 交互获取模型信息

**关键实现**:
```python
class ModelScopeClient(ModelSourceClient):
    DEFAULT_ORGANIZATIONS = [
        "qwen", "LLM-Research", "ZhipuAI", "baichuan-inc",
        "deepseek-ai", "OpenBMB", "BAAI", "01-ai", ...
    ]
    
    async def search_models(self, query, model_type, tags, page, per_page) -> List[ModelInfo]
    async def get_model_detail(self, model_id: str) -> Optional[ModelInfo]
    async def get_popular_models(self, limit: int) -> List[ModelInfo]
    async def get_models_by_organization(self, organization: str) -> List[ModelInfo]
```

**模型信息推断**:
- 从标签推断模型类型
- 从名称推断模型家族
- 从标签推断模型能力
- 从名称推断上下文长度

---

#### 3. vllm.py - vLLM 客户端

**职责**: 与 vLLM OpenAI 兼容 API 交互，管理 vLLM 进程

**关键类**:

##### VLLMInstance
```python
@dataclass
class VLLMInstance:
    id: str
    model_name: str
    model_path: str
    port: int
    process: Optional[subprocess.Popen]
    status: str              # starting, running, stopping, stopped, error
    logs: List[Dict]
    start_time: datetime
    end_time: datetime
    config: Dict
    
    def add_log(self, level: str, message: str)
    def register_log_callback(self, callback: Callable)
    def to_dict(self) -> Dict
```

##### VLLMClient
HTTP 客户端，与 vLLM OpenAI 兼容 API 交互

```python
class VLLMClient(InferenceClient):
    async def get_models(self) -> List[Dict]
    async def create_chat_completion(...) -> Dict
    async def create_completion(...) -> Dict
    async def create_embedding(...) -> Dict
    async def stream_chat_completion(...) -> AsyncGenerator
    async def check_health(self) -> bool
    async def get_metrics(self) -> Optional[str]
```

##### VLLMProcessManager
进程管理器，负责启动、停止和管理 vLLM 服务实例

```python
class VLLMProcessManager:
    instances: Dict[str, VLLMInstance]
    
    async def start_model(self, model_name: str, model_id: str, **kwargs) -> VLLMInstance
    async def stop_model(self, instance_id: str) -> bool
    def get_instance(self, instance_id: str) -> Optional[VLLMInstance]
    def list_instances(self) -> List[Dict]
    def get_instance_logs(self, instance_id: str, offset, limit, level) -> List[Dict]
    async def check_instance_health(self, instance_id: str) -> bool
```

**启动流程**:
1. 查找可用端口
2. 检查模型是否已缓存
3. 构建 vLLM 启动命令
4. 在后台线程启动进程
5. 实时捕获和解析日志
6. 更新实例状态

---

### 路由模块

#### 1. models.py - 模型管理路由

**端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /models/refresh | 刷新模型列表 |
| GET | /models | 获取模型列表 |
| POST | /models/launch | 启动模型（旧接口） |
| POST | /models/deploy | 部署模型 |

**关键函数**:
```python
async def get_cached_models(model_type, search) -> List[Dict]
async def search_models_from_source(search_query, default_orgs) -> List[Dict]
async def list_models(model_type, search, db) -> List[ModelInfo]
async def deploy_model_endpoint(params: dict, db) -> Dict
```

**部署流程**:
1. 获取模型详情
2. 提取并转换 vLLM 参数
3. 调用 vllm_process_manager.start_model()
4. 创建数据库记录

---

#### 2. instances.py - 实例管理路由

**端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /instances | 获取实例列表 |
| GET | /instances/{instance_id} | 获取实例详情 |
| POST | /instances/{instance_id}/stop | 停止实例 |
| GET | /instances/{instance_id}/logs | 获取实例日志 |
| WebSocket | /instances/{instance_id}/logs | 实时日志流 |

**WebSocket 日志流**:
```python
@router.websocket("/{instance_id}/logs")
async def websocket_instance_logs(websocket: WebSocket, instance_id: str):
    await websocket.accept()
    # 发送历史日志
    await websocket.send_json({"type": "history", "logs": logs})
    # 注册回调实时推送
    instance.register_log_callback(callback)
    # 保持连接，发送心跳
```

---

#### 3. downloads.py - 下载管理路由

**端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /models/download | 开始下载模型 |
| GET | /models/download/status | 获取下载状态 |
| GET | /models/cached | 列出已缓存模型 |
| DELETE | /models/cached | 删除已缓存模型 |

---

#### 4. cluster.py - 集群管理路由

**端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /cluster/overview | 获取集群概览 |
| GET | /cluster/nodes | 获取节点信息 |
| GET | /cluster/deployments | 获取模型部署列表 |

**返回数据**:
- 集群概览: 节点数、GPU 数量、内存使用、平均利用率
- 节点信息: CPU、内存、GPU 列表
- 部署列表: 模型名称、状态、Token 使用量、调用次数

---

#### 5. stats.py - 统计信息路由

**端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /stats | 获取模型统计信息 |
| GET | /stats/dashboard | 获取仪表盘统计 |

**统计数据**:
- 总调用次数、成功率
- Token 使用量
- 平均延迟、P99 延迟
- 每日趋势
- 延迟分布
- Token 分布
- 错误类型分布

---

## 前端模块详解

### 页面组件

| 页面 | 路径 | 描述 |
|------|------|------|
| Dashboard | / | 仪表盘，展示系统概览 |
| ModelStore | /models/store | 模型仓库，搜索和浏览模型 |
| ModelRegister | /models/register | 模型注册 |
| ModelInstances | /models/instances | 实例管理 |
| DeviceInfo | /devices | 设备信息，GPU 监控 |
| ModelStats | /models/stats | 统计分析 |
| SystemManagement | /system | 系统管理 |

### 核心组件

| 组件 | 描述 |
|------|------|
| Header | 顶部导航栏 |
| Sidebar | 侧边栏菜单 |
| ModelChatTest | 模型对话测试组件 |
| ModelLaunchLog | 模型启动日志组件 |
| VLLMParamsForm | vLLM 参数配置表单 |

### API 封装

**vllm.ts**:
```typescript
// 模型相关 API
export const getModels = (params) => axios.get('/api/v1/models', { params })
export const deployModel = (params) => axios.post('/api/v1/models/deploy', params)
export const refreshModels = (params) => axios.post('/api/v1/models/refresh', params)

// 实例相关 API
export const getInstances = () => axios.get('/api/v1/instances')
export const stopInstance = (id) => axios.post(`/api/v1/instances/${id}/stop`)
export const getInstanceLogs = (id, params) => axios.get(`/api/v1/instances/${id}/logs`, { params })

// 下载相关 API
export const downloadModel = (modelId) => axios.post('/api/v1/models/download', { model_id: modelId })
export const getCachedModels = () => axios.get('/api/v1/models/cached')
```

---

## 数据库设计

### ER 图

```
┌─────────────────┐     ┌─────────────────┐
│  ModelInstance  │     │   RequestLog    │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ model_id (FK)   │
│ name            │     │ id (PK)         │
│ model_name      │     │ model_name      │
│ model_type      │     │ request_type    │
│ status          │     │ status          │
│ replicas        │     │ latency_ms      │
│ gpus (JSON)     │     │ input_tokens    │
│ config (JSON)   │     │ output_tokens   │
│ node            │     │ error_type      │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│    GPUStats     │     │    NodeInfo     │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ node_id         │     │ name            │
│ gpu_index       │     │ ip              │
│ gpu_name        │     │ status          │
│ utilization     │     │ cpu_percent     │
│ memory_used     │     │ memory_used     │
│ memory_total    │     │ memory_total    │
│ temperature     │     └─────────────────┘
│ power           │
│ timestamp       │
└─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│      User       │     │      Role       │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ username        │     │ name            │
│ email           │     │ description     │
│ password_hash   │     │ permissions(JSON)│
│ role            │     └─────────────────┘
│ status          │
│ last_login      │
└─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│     ApiKey      │     │  SystemConfig   │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ name            │     │ key             │
│ key_hash        │     │ value           │
│ user_id         │     │ description     │
│ permissions(JSON)│     └─────────────────┘
│ status          │
│ expires_at      │
└─────────────────┘
```

---

## API 接口文档

### 模型管理

#### GET /api/v1/models
获取模型列表

**Query 参数**:
- `model_type`: 模型类型过滤
- `search`: 搜索关键词

**响应**:
```json
[
  {
    "id": "qwen2.5",
    "name": "qwen2.5",
    "description": "阿里巴巴通义千问2.5系列",
    "type": "llm",
    "status": "running",
    "size": "7B",
    "language": ["zh", "en"],
    "abilities": ["chat", "generate", "tools"],
    "context_length": 32768,
    "cached": true,
    "specs": [...]
  }
]
```

#### POST /api/v1/models/deploy
部署模型

**请求体**:
```json
{
  "modelName": "qwen2.5-7b",
  "modelId": "qwen/Qwen2.5-7B-Instruct",
  "tensorParallelSize": 1,
  "gpuMemoryUtilization": 0.9,
  "maxModelLen": 8192,
  "gpuIndices": [0]
}
```

**响应**:
```json
{
  "success": true,
  "message": "模型部署中",
  "instance_id": "uuid",
  "port": 8001,
  "status": "starting"
}
```

### 实例管理

#### GET /api/v1/instances
获取实例列表

#### POST /api/v1/instances/{instance_id}/stop
停止实例

#### WebSocket /api/v1/instances/{instance_id}/logs
实时日志流

**消息格式**:
```json
{"type": "history", "logs": [...]}
{"type": "log", "data": {"level": "INFO", "message": "..."}}
{"type": "status", "data": {...}}
{"type": "ping"}
```

### 集群管理

#### GET /api/v1/cluster/overview
获取集群概览

**响应**:
```json
{
  "nodes": {"total": 1, "online": 1},
  "gpus": {"total": 4, "available": 2},
  "memory": {"total": 64.0, "used": 32.5},
  "avg_utilization": 45.2
}
```

### 统计信息

#### GET /api/v1/stats?range=7d
获取统计信息

**响应**:
```json
{
  "overview": {
    "total_calls": "15K",
    "total_tokens": "2.5M",
    "avg_latency": 150,
    "p99_latency": 450,
    "success_rate": 99.5
  },
  "daily_trend": [...],
  "latency_distribution": [...],
  "token_distribution": [...]
}
```

---

## 依赖关系

### 后端模块依赖图

```
main.py
├── config.py (settings)
├── models.py (init_db, get_db)
├── monitor.py (metrics_collector)
├── clients/
│   ├── __init__.py
│   ├── base.py (ModelSourceClient, InferenceClient)
│   ├── modelscope.py (ModelScopeClient) ──► base.py
│   ├── huggingface.py (HuggingFaceClient) ──► base.py
│   ├── vllm.py (VLLMClient, VLLMProcessManager) ──► base.py, config.py, vllm_params.py
│   └── utils.py
├── routers/
│   ├── models.py ──► clients/modelscope.py, clients/vllm.py, modelscope_downloader.py
│   ├── instances.py ──► clients/vllm.py
│   ├── downloads.py ──► modelscope_downloader.py
│   ├── cluster.py ──► monitor.py
│   ├── stats.py ──► models.py
│   ├── proxy.py ──► clients/vllm.py
│   └── system.py
├── vllm_params.py
├── builtin_models.py
├── modelscope_downloader.py ──► config.py
└── schemas.py
```

### 前端模块依赖图

```
App.tsx
├── components/
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── ModelChatTest.tsx ──► api/vllm.ts
│   ├── ModelLaunchLog.tsx ──► api/vllm.ts
│   └── VLLMParamsForm.tsx ──► config/vllmParams.ts
├── pages/
│   ├── Dashboard.tsx ──► api/vllm.ts, api/system.ts
│   ├── ModelStore.tsx ──► api/vllm.ts
│   ├── ModelInstances.tsx ──► api/vllm.ts
│   ├── DeviceInfo.tsx ──► api/system.ts
│   ├── ModelStats.tsx ──► api/vllm.ts
│   └── SystemManagement.tsx ──► api/system.ts
├── api/
│   ├── vllm.ts ──► axios
│   └── system.ts ──► axios
├── types/
│   └── index.ts
└── config/
    └── vllmParams.ts
```

---

## 项目运行方式

### 开发环境

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

### Docker 部署

```bash
# 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境部署

```bash
# 构建前端
cd frontend
npm run build

# 使用 gunicorn 启动后端
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 配置说明

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| HOST | 0.0.0.0 | 服务地址 |
| PORT | 8000 | 服务端口 |
| DB_TYPE | sqlite | 数据库类型 |
| DATABASE_URL | - | 数据库连接 URL |
| MODEL_CACHE_DIR | ~/.cache/vllm-manager/models | 模型缓存目录 |
| VLLM_PORT_RANGE_START | 8001 | vLLM 实例端口范围起始 |
| VLLM_PORT_RANGE_END | 8100 | vLLM 实例端口范围结束 |
| SECRET_KEY | - | JWT 密钥 |

### 数据库配置

#### SQLite（默认）
```bash
# 无需配置，自动创建 vllm_manager.db
```

#### MySQL
```bash
pip install pymysql

export DB_TYPE=mysql
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=vllm_user
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=vllm_manager
```

#### PostgreSQL
```bash
export DB_TYPE=postgresql
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password
export POSTGRES_DATABASE=vllm_manager
```

---

## 扩展开发指南

### 添加新的模型源

1. 在 `backend/clients/` 创建新客户端类，继承 `ModelSourceClient`
2. 实现所有抽象方法
3. 在 `backend/clients/__init__.py` 中导出

### 添加新的推理引擎

1. 在 `backend/clients/` 创建新客户端类，继承 `InferenceClient`
2. 实现所有抽象方法
3. 创建进程管理器（如需要）
4. 在 `backend/clients/__init__.py` 中导出

### 添加新的 API 端点

1. 在 `backend/routers/` 创建或修改路由文件
2. 在 `backend/main.py` 中注册路由
3. 在 `frontend/src/api/` 添加对应的 API 调用
4. 在前端页面中使用

---

## 常见问题

### Q: 如何添加新的模型到内置列表？

A: 编辑 `backend/builtin_models.py`，在 `BUILTIN_MODELS` 列表中添加新的 `ModelFamily` 对象。

### Q: 如何修改 vLLM 参数？

A: 编辑 `backend/vllm_params.py`，在 `VLLM_PARAMS` 字典中添加或修改参数定义。

### Q: 如何自定义监控指标？

A: 修改 `backend/monitor.py`，在 `MetricsCollector.collect_metrics()` 中添加新的指标收集逻辑。

### Q: 如何启用 GPU 支持？

A: 在 `docker-compose.yml` 中取消 GPU 配置的注释，并确保安装了 nvidia-docker。

---

*文档版本: 1.0.0*
*最后更新: 2025-04-07*
