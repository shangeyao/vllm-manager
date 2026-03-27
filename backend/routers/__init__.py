from .models import router as models_router
from .instances import router as instances_router
from .downloads import router as downloads_router
from .cluster import router as cluster_router
from .stats import router as stats_router
from .proxy import router as proxy_router
from .system import router as system_router

__all__ = [
    "models_router",
    "instances_router",
    "downloads_router",
    "cluster_router",
    "stats_router",
    "proxy_router",
    "system_router",
]
