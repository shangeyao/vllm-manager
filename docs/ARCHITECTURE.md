# vLLM Manager 项目架构文档

## 1. 项目概述

vLLM Manager 是一个基于 vLLM 的大语言模型部署和管理平台，提供模型仓库、模型部署、监控统计等功能。

## 2. 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **UI 组件库**: Ant Design 5
- **状态管理**: React Hooks
- **路由**: React Router
- **HTTP 客户端**: Axios

### 后端
- **框架**: FastAPI (Python 3.12)
- **数据库**: SQLite (SQLAlchemy ORM)
- **模型下载**: ModelScope SDK
- **模型服务**: vLLM (OpenAI 兼容 API)
- **监控**: 自定义监控模块

## 3. 项目结构

```
vllm_manager/
├── docs/                          # 文档目录
│   ├── ARCHITECTURE.md           # 架构文档
│   └── DEPLOYMENT.md             # 部署文档
├── frontend/                      # 前端目录
│   ├── src/
│   │   ├── api/                  # API 接口
│   │   │   ├── system.ts         # 系统管理 API
│   │   │   └── vllm.ts          # vLLM 相关 API
│   │   ├── components/           # 组件
│   │   │   ├── Header.tsx        # 顶部导航
│   │   │   ├── ModelLaunchLog.tsx # 模型启动日志
│   │   │   └── Sidebar.tsx       # 侧边栏
│   │   ├── pages/                # 页面
│   │   │   ├── Dashboard.tsx     # 仪表盘
│   │   │   ├── DeviceInfo.tsx    # 设备信息
│   │   │   ├── ModelInstances.tsx # 模型实例
│   │   │   ├── ModelRegister.tsx # 模型注册
│   │   │   ├── ModelStats.tsx    # 模型统计
│   │   │   ├── ModelStore.tsx    # 模型仓库
│   │   │   └── SystemManagement.tsx # 系统管理
│   │   ├── types/                # TypeScript 类型
│   │   │   └── index.ts
│   │   ├── App.tsx               # 根组件
│   │   └── main.tsx              # 入口文件
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                       # 后端目录
│   ├── main.py                   # FastAPI 主入口（精简版，仅注册路由）
│   ├── config.py                 # 配置管理
│   ├── models.py                 # 数据库模型
│   ├── schemas.py                # Pydantic 模型
│   ├── builtin_models.py         # 内置模型列表
│   ├── clients/                  # 统一客户端接口（重构后）
│   │   ├── __init__.py           # 客户端导出
│   │   ├── base.py               # 抽象基类定义
│   │   ├── utils.py              # 客户端工具函数
│   │   ├── modelscope.py         # ModelScope 客户端
│   │   ├── huggingface.py        # HuggingFace 客户端
│   │   └── vllm.py               # vLLM 客户端和进程管理
│   ├── modelscope_downloader.py  # 模型下载器
│   ├── vllm_params.py           # vLLM 参数定义
│   ├── monitor.py               # 系统监控
│   ├── routers/                 # 路由模块（按功能分离）
│   │   ├── __init__.py          # 路由导出
│   │   ├── models.py            # 模型管理路由
│   │   ├── instances.py         # 实例管理路由
│   │   ├── downloads.py         # 模型下载路由
│   │   ├── cluster.py           # 集群管理路由
│   │   ├── stats.py             # 统计路由
│   │   ├── proxy.py             # vLLM 代理路由
│   │   └── system.py            # 系统管理路由
│   ├── requirements.txt         # Python 依赖
│   └── model_cache/             # 模型缓存目录
├── docker/                        # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── scripts/                       # 脚本
│   ├── build.sh                 # 构建脚本
│   └── deploy.sh                # 部署脚本
├── package.json                   # 根目录 package.json
└── README.md
```

## 4. 架构设计

### 4.1 前后端分离架构

```
┌─────────────────┐     HTTP/WebSocket     ┌─────────────────┐
│   Frontend      │ ◄────────────────────► │    Backend      │
│   (React)       │                        │   (FastAPI)     │
│   Port: 3000    │                        │   Port: 8000    │
└─────────────────┘                        └────────┬────────┘
                                                    │
                       ┌────────────────────────────┼────────────────────────────┐
                       │                            │                            │
                       ▼                            ▼                            ▼
              ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
              │   ModelScope    │        │      vLLM       │        │    SQLite DB    │
              │     SDK/API     │        │  (Model Server) │        │                 │
              └─────────────────┘        └─────────────────┘        └─────────────────┘
```

### 4.2 后端模块架构（重构后）

```
main.py (FastAPI App - 精简版)
    │
    ├── 生命周期管理 (lifespan)
    │   ├── 初始化数据库
    │   ├── 启动指标收集
    │   └── 清理资源
    │
    ├── 中间件
    │   └── CORS
    │
    ├── 路由注册 (routers/)
    │   ├── models_router      # /api/v1/models/*
    │   ├── instances_router   # /api/v1/instances/*
    │   ├── downloads_router   # /api/v1/models/download/*
    │   ├── cluster_router     # /api/v1/cluster/*
    │   ├── stats_router       # /api/v1/stats/*
    │   ├── system_router      # /api/v1/system/*
    │   └── proxy_router       # /api/v1/chat/*, /api/v1/completions/*
    │
    └── 健康检查
        └── /health

routers/
    ├── models.py              # 模型管理（列表、刷新、部署）
    ├── instances.py           # 实例管理（CRUD、日志、WebSocket）
    ├── downloads.py           # 模型下载（开始、状态、缓存）
    ├── cluster.py             # 集群管理（概览、节点、部署）
    ├── stats.py               # 统计数据（模型统计、仪表盘）
    ├── proxy.py               # vLLM 代理（OpenAI 兼容 API）
    └── system.py              # 系统管理（用户、角色、配置）

clients/                       # 统一客户端接口（重构后核心模块）
    ├── base.py                # 抽象基类定义
    │   ├── ModelSourceClient  # 模型源客户端基类
    │   ├── InferenceClient    # 推理引擎客户端基类
    │   ├── ModelInfo          # 统一模型信息结构
    │   └── ModelSpec          # 模型规格信息
    ├── utils.py               # 客户端工具函数
    │   ├── infer_model_family
    │   ├── infer_model_type_from_tags
    │   ├── infer_abilities
    │   ├── infer_languages
    │   ├── infer_model_size
    │   └── infer_context_length
    ├── modelscope.py          # ModelScope 客户端实现
    ├── huggingface.py         # HuggingFace 客户端实现
    └── vllm.py                # vLLM 客户端和进程管理
```

### 4.3 统一客户端架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      clients/base.py                             │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │ ModelSourceClient   │    │  InferenceClient    │             │
│  │ (抽象基类)          │    │  (抽象基类)         │             │
│  ├─────────────────────┤    ├─────────────────────┤             │
│  │ + search_models()   │    │ + get_models()      │             │
│  │ + get_model_detail()│    │ + create_chat_completion()       │
│  │ + get_popular_models│    │ + create_completion()            │
│  │ + get_models_by_org │    │ + create_embedding()             │
│  └─────────────────────┘    │ + stream_chat_completion()       │
│                             │ + check_health()    │             │
│  ┌─────────────────────┐    └─────────────────────┘             │
│  │ ModelInfo (dataclass)                                        │
│  │ - model_id, model_name, model_type, model_family...          │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ modelscope.py   │  │ huggingface.py  │  │    vllm.py      │
│ ModelScopeClient│  │ HuggingFaceClient│  │  VLLMClient    │
│                 │  │                 │  │ VLLMProcessManager
│ 实现模型源接口   │  │ 实现模型源接口   │  │ 实现推理引擎接口 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 4.4 路由模块说明

| 模块 | 文件 | 路径前缀 | 功能 |
|------|------|----------|------|
| models | routers/models.py | /api/v1/models | 模型列表、刷新、部署 |
| instances | routers/instances.py | /api/v1/instances | 实例管理、日志、WebSocket |
| downloads | routers/downloads.py | /api/v1/models | 模型下载、缓存管理 |
| cluster | routers/cluster.py | /api/v1/cluster | 集群概览、节点信息 |
| stats | routers/stats.py | /api/v1/stats | 统计数据、仪表盘 |
| proxy | routers/proxy.py | /api/v1 | OpenAI 兼容 API 代理 |
| system | routers/system.py | /api/v1/system | 用户、角色、系统配置 |

### 4.5 客户端模块说明

| 模块 | 文件 | 类型 | 功能 |
|------|------|------|------|
| base | clients/base.py | 抽象基类 | 定义统一接口 |
| utils | clients/utils.py | 工具函数 | 模型信息推断 |
| modelscope | clients/modelscope.py | 模型源 | ModelScope 模型获取 |
| huggingface | clients/huggingface.py | 模型源 | HuggingFace 模型获取 |
| vllm | clients/vllm.py | 推理引擎 | vLLM API 和进程管理 |

## 5. 核心功能流程

### 5.1 模型部署流程

```
1. 用户选择模型 → ModelStore.tsx
2. 配置部署参数 (GPU数量、量化方式等)
3. 调用 POST /api/v1/models/deploy
4. 后端创建 VLLMInstance (vllm_process_manager)
5. 启动 vLLM 子进程
6. WebSocket 实时推送启动日志 (/ws/instances/{id}/logs)
7. 部署完成，更新实例状态
```

### 5.2 模型下载流程

```
1. 用户点击下载 → ModelStore.tsx
2. 调用 POST /api/v1/models/download
3. 后端启动下载任务 (modelscope_downloader)
4. 轮询 GET /api/v1/models/download/status
5. 显示下载进度
6. 下载完成，更新本地缓存状态
```

### 5.3 模型列表刷新流程

```
1. 用户点击"更新模型列表"
2. 调用 POST /api/v1/models/refresh
3. 后端使用 clients.modelscope 异步并发获取多个组织模型
4. 去重并转换为统一的 ModelInfo 格式
5. 更新缓存，返回模型列表
```

## 6. 数据流

### 6.1 模型数据流（重构后）

```
ModelScope API → clients.modelscope → routers/models.py → frontend/src/api/vllm.ts → React Components
                      │
                      ▼
              统一 ModelInfo 格式
```

### 6.2 实例数据流

```
vLLM Process → clients.vllm → WebSocket → ModelLaunchLog.tsx
```

## 7. 配置说明

### 7.1 后端配置 (backend/config.py)

```python
MODEL_CACHE_DIR = "~/.cache/vllm-ui/models"  # 模型缓存目录
VLLM_PORT_RANGE = 8001-8100                   # vLLM 实例端口范围
DATABASE_URL = "sqlite:///./vllm_ui.db"      # 数据库路径
```

### 7.2 前端配置 (vite.config.ts)

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws': 'ws://localhost:8000'
  }
}
```

## 8. 扩展性设计

### 8.1 添加新的模型源

1. 在 `backend/clients/` 创建新的客户端文件
2. 继承 `ModelSourceClient` 基类
3. 实现所有抽象方法
4. 在 `clients/__init__.py` 导出

示例：
```python
# clients/new_source.py
from .base import ModelSourceClient, ModelInfo, ModelType

class NewSourceClient(ModelSourceClient):
    def __init__(self):
        super().__init__("new_source")
    
    async def search_models(self, query: str = "", ...):
        # 实现搜索逻辑
        pass
    
    async def get_model_detail(self, model_id: str):
        # 实现详情获取
        pass
    
    # ... 其他方法

# clients/__init__.py
from .new_source import NewSourceClient
```

### 8.2 添加新的推理引擎

1. 在 `backend/clients/` 创建新的推理客户端
2. 继承 `InferenceClient` 基类
3. 实现所有抽象方法

### 8.3 支持新的模型类型

在 `backend/clients/base.py` 的 `ModelType` 枚举中添加新类型：

```python
class ModelType(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"
    # 添加新类型
    NEW_TYPE = "new_type"
```

### 8.4 支持新的部署参数

1. 修改 `backend/vllm_params.py` 添加参数定义
2. 修改 `backend/routers/models.py` 中的参数映射
3. 修改前端部署表单

## 9. 重构说明

### 9.1 重构前问题

- `main.py` 文件过大（约 1400 行）
- 所有路由逻辑混杂在一个文件中
- **ModelScope 代码重复**: `modelscope_client.py` 和 `modelscope_api.py` 功能高度重复
- **模型推断逻辑重复**: 每个客户端都有 `_infer_model_type`、`_infer_model_family` 等重复方法
- **缺乏统一接口**: ModelScope、HuggingFace 各自独立，没有统一抽象
- **vLLM 客户端分散**: `vllm_client.py` 和 `vllm_process_manager.py` 职责不够清晰
- 难以维护和扩展

### 9.2 重构后改进

- `main.py` 精简至约 100 行
- 按功能分离到 7 个路由模块
- **统一客户端架构**: 创建 `clients/` 模块，提供统一抽象
  - `base.py`: 定义 `ModelSourceClient` 和 `InferenceClient` 抽象基类
  - `utils.py`: 集中所有模型推断逻辑，消除重复代码
  - `modelscope.py`: 统一的 ModelScope 客户端
  - `huggingface.py`: 统一的 HuggingFace 客户端
  - `vllm.py`: 统一的 vLLM 客户端和进程管理
- **统一数据模型**: 使用 `ModelInfo` dataclass 统一模型信息格式
- 每个模块职责单一，易于维护
- 新增功能只需添加客户端或路由文件

### 9.3 文件对比

| 文件 | 重构前 | 重构后 |
|------|--------|--------|
| main.py | ~1400 行 | ~116 行 |
| routers/models.py | - | ~322 行 |
| routers/instances.py | - | ~110 行 |
| routers/downloads.py | - | ~100 行 |
| routers/cluster.py | - | ~103 行 |
| routers/stats.py | - | ~168 行 |
| routers/proxy.py | - | ~108 行 |
| routers/system.py | - | ~314 行 |
| **clients/base.py** | - | **~239 行** |
| **clients/utils.py** | - | **~166 行** |
| **clients/modelscope.py** | - | **~234 行** |
| **clients/huggingface.py** | - | **~206 行** |
| **clients/vllm.py** | - | **~517 行** |
| ~~modelscope_client.py~~ | ~~~354 行~~ | **已删除** |
| ~~modelscope_api.py~~ | ~~~335 行~~ | **已删除** |
| ~~vllm_client.py~~ | ~~~270 行~~ | **已删除** |
| ~~vllm_process_manager.py~~ | ~~~376 行~~ | **已删除** |

### 9.4 架构优势

1. **单一职责**: 每个客户端只负责一个模型源或推理引擎
2. **开闭原则**: 新增模型源只需实现基类，无需修改现有代码
3. **代码复用**: 模型推断逻辑集中在 `utils.py`，消除重复
4. **统一接口**: 所有模型源返回统一的 `ModelInfo` 格式
5. **易于测试**: 抽象基类便于 Mock 和单元测试

## 10. 安全考虑

- CORS 配置限制前端域名
- 模型下载验证文件完整性
- vLLM 进程隔离
- 数据库访问控制

## 11. 性能优化

- 模型列表缓存
- 异步并发获取模型
- 模型下载断点续传
- WebSocket 日志流式传输
- 前端虚拟滚动 (大量模型列表)
