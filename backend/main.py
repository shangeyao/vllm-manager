"""
vLLM Manager Backend - FastAPI Application

重构后的主入口文件，采用模块化路由组织。
所有业务逻辑已分离到 routers/ 目录下的各个模块。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

from config import settings
from models import init_db, get_db, GPUStats
from monitor import metrics_collector
from clients import vllm_client

# 导入路由
from routers import (
    models_router,
    instances_router,
    downloads_router,
    cluster_router,
    stats_router,
    proxy_router,
    system_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    init_db()

    # 启动指标收集
    async def save_metrics(metrics):
        db = next(get_db())
        try:
            for gpu in metrics.get("gpus", []):
                gpu_stat = GPUStats(
                    node_id="local",
                    gpu_index=gpu["index"],
                    gpu_name=gpu["name"],
                    utilization=gpu["utilization"],
                    memory_used=gpu["memory_used"],
                    memory_total=gpu["memory_total"],
                    temperature=gpu["temperature"],
                    power=gpu["power"]
                )
                db.add(gpu_stat)
            db.commit()
        except Exception as e:
            print(f"Error saving metrics: {e}")
        finally:
            db.close()

    metrics_collector.register_callback(save_metrics)
    metrics_task = asyncio.create_task(metrics_collector.collect_loop(interval=10))

    yield

    # 关闭时清理
    metrics_collector.stop()
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass
    await vllm_client.close()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(models_router, prefix="/api/v1")
app.include_router(instances_router, prefix="/api/v1")
app.include_router(downloads_router, prefix="/api/v1")
app.include_router(cluster_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# 代理路由（无前缀，保持 OpenAI 兼容的 API 路径）
app.include_router(proxy_router)


@app.get("/health")
async def health_check():
    """健康检查"""
    vllm_healthy = await vllm_client.check_health()
    return {
        "status": "healthy",
        "vllm": "healthy" if vllm_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
