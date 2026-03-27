from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from models import get_db, ModelInstance
from schemas import ModelInstanceResponse
from clients import vllm_process_manager

router = APIRouter(prefix="/instances", tags=["instances"])


@router.get("", response_model=List[ModelInstanceResponse])
async def list_instances(db: Session = Depends(get_db)):
    """获取模型实例列表"""
    instances = db.query(ModelInstance).all()
    return instances


@router.get("/{instance_id}")
async def get_instance(instance_id: str, db: Session = Depends(get_db)):
    """获取实例详情"""
    vllm_instance = vllm_process_manager.get_instance(instance_id)
    if vllm_instance:
        return vllm_instance.to_dict()

    db_instance = db.query(ModelInstance).filter(ModelInstance.id == instance_id).first()
    if not db_instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    return db_instance


@router.post("/{instance_id}/stop")
async def stop_instance(instance_id: str, db: Session = Depends(get_db)):
    """停止实例"""
    success = await vllm_process_manager.stop_model(instance_id)
    if not success:
        raise HTTPException(status_code=404, detail="实例不存在或已停止")

    db_instance = db.query(ModelInstance).filter(ModelInstance.id == instance_id).first()
    if db_instance:
        db_instance.status = "stopped"
        db.commit()

    return {"success": True, "message": "实例已停止"}


@router.get("/{instance_id}/logs")
async def get_instance_logs(
    instance_id: str,
    offset: int = 0,
    limit: int = 100,
    level: Optional[str] = None
):
    """获取实例日志"""
    logs = vllm_process_manager.get_instance_logs(instance_id, offset, limit, level)
    instance = vllm_process_manager.get_instance(instance_id)
    total_logs = len(instance.logs) if instance else 0

    return {
        "instance_id": instance_id,
        "logs": logs,
        "offset": offset,
        "limit": limit,
        "total": total_logs
    }


@router.websocket("/{instance_id}/logs")
async def websocket_instance_logs(websocket: WebSocket, instance_id: str):
    """WebSocket 实时日志流"""
    await websocket.accept()

    instance = vllm_process_manager.get_instance(instance_id)
    if not instance:
        await websocket.send_json({"error": "Instance not found"})
        await websocket.close()
        return

    # 发送历史日志
    logs = instance.logs[-100:]
    await websocket.send_json({"type": "history", "logs": logs})

    # 注册日志回调
    async def log_callback(log_entry):
        try:
            await websocket.send_json({"type": "log", "data": log_entry})
        except:
            pass

    def sync_callback(log_entry):
        asyncio.create_task(log_callback(log_entry))

    instance.register_log_callback(sync_callback)

    try:
        await websocket.send_json({"type": "status", "data": instance.to_dict()})

        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        instance.unregister_log_callback(sync_callback)
