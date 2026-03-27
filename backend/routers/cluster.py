from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from models import get_db, ModelInstance
from schemas import NodeInfo as NodeInfoSchema, ClusterOverview, ModelDeployment
from monitor import gpu_monitor, system_monitor

router = APIRouter(prefix="/cluster", tags=["cluster"])


@router.get("/overview")
async def get_cluster_overview():
    """获取集群概览"""
    gpus = gpu_monitor.get_all_gpus()
    sys_info = system_monitor.get_system_overview()

    total_gpus = len(gpus)
    available_gpus = sum(1 for g in gpus if g["utilization"] < 80)

    total_memory = sum(g["memory_total"] for g in gpus) if gpus else sys_info["memory"]["total"]
    used_memory = sum(g["memory_used"] for g in gpus) if gpus else sys_info["memory"]["used"]

    avg_utilization = sum(g["utilization"] for g in gpus) / len(gpus) if gpus else 0

    return ClusterOverview(
        nodes={"total": 1, "online": 1},
        gpus={"total": total_gpus, "available": available_gpus},
        memory={"total": total_memory, "used": used_memory},
        avg_utilization=round(avg_utilization, 1)
    )


@router.get("/nodes", response_model=List[NodeInfoSchema])
async def get_nodes():
    """获取节点信息"""
    gpus = gpu_monitor.get_all_gpus()
    sys_info = system_monitor.get_system_overview()

    if not gpus:
        return [NodeInfoSchema(
            id="local",
            name="local-node",
            ip="127.0.0.1",
            status="online",
            cpu=sys_info["cpu"]["percent"],
            memory_used=sys_info["memory"]["used"],
            memory_total=sys_info["memory"]["total"],
            gpus=[]
        )]

    gpu_infos = []
    for gpu in gpus:
        gpu_infos.append(NodeInfoSchema.GPUInfo(
            id=gpu["id"],
            name=gpu["name"],
            index=gpu["index"],
            utilization=gpu["utilization"],
            memory_used=gpu["memory_used"],
            memory_total=gpu["memory_total"],
            temperature=gpu["temperature"],
            power=gpu["power"]
        ))

    return [NodeInfoSchema(
        id="local",
        name="gpu-node-01",
        ip="127.0.0.1",
        status="online",
        cpu=sys_info["cpu"]["percent"],
        memory_used=sys_info["memory"]["used"],
        memory_total=sys_info["memory"]["total"],
        gpus=gpu_infos
    )]


@router.get("/deployments")
async def get_deployments(db: Session = Depends(get_db)):
    """获取模型部署列表"""
    from models import RequestLog

    instances = db.query(ModelInstance).filter(ModelInstance.status == "running").all()

    deployments = []
    for inst in instances:
        logs = db.query(RequestLog).filter(RequestLog.model_id == inst.id).all()
        total_calls = len(logs)
        total_tokens = sum(log.input_tokens + log.output_tokens for log in logs)
        avg_latency = sum(log.latency_ms for log in logs) / len(logs) if logs else 0

        deployments.append(ModelDeployment(
            id=inst.id,
            name=inst.model_name,
            status=inst.status,
            node=inst.node or "local",
            gpus=inst.gpus or [],
            tokens=f"{total_tokens / 1000000:.1f}M" if total_tokens > 1000000 else f"{total_tokens / 1000:.1f}K",
            calls=f"{total_calls / 1000:.1f}K" if total_calls > 1000 else str(total_calls),
            latency=f"{avg_latency:.0f}ms"
        ))

    return deployments
