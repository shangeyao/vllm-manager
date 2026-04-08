from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from models import get_db, ModelInstance
from schemas import ModelInstanceResponse
from clients import vllm_process_manager
from clients.vllm import VLLMInstance

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


@router.post("/{instance_id}/start")
async def start_instance(instance_id: str, db: Session = Depends(get_db)):
    """启动已停止的实例"""
    db_instance = db.query(ModelInstance).filter(ModelInstance.id == instance_id).first()
    if not db_instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    vllm_instance = vllm_process_manager.get_instance(instance_id)
    if vllm_instance and vllm_instance.status in ["starting", "running"]:
        raise HTTPException(status_code=400, detail="实例已在运行")
    
    # 使用保存的配置启动实例
    config = db_instance.config or {}
    instance = await vllm_process_manager.start_model(
        model_name=db_instance.name,
        model_id=db_instance.model_id,
        **config
    )
    
    # 更新数据库
    db_instance.status = "running"
    db.commit()
    
    return {"success": True, "message": "实例已启动", "instance_id": instance.id}


@router.post("/{instance_id}/restart")
async def restart_instance(instance_id: str, db: Session = Depends(get_db)):
    """重启实例"""
    # 先停止
    vllm_instance = vllm_process_manager.get_instance(instance_id)
    if vllm_instance:
        await vllm_process_manager.stop_model(instance_id)
        await asyncio.sleep(2)
    
    # 再启动
    db_instance = db.query(ModelInstance).filter(ModelInstance.id == instance_id).first()
    if not db_instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    config = db_instance.config or {}
    instance = await vllm_process_manager.start_model(
        model_name=db_instance.name,
        model_id=db_instance.model_id,
        **config
    )
    
    db_instance.status = "running"
    db.commit()
    
    return {"success": True, "message": "实例已重启", "instance_id": instance.id}


@router.delete("/{instance_id}")
async def delete_instance(instance_id: str, db: Session = Depends(get_db)):
    """删除实例"""
    # 先停止
    await vllm_process_manager.stop_model(instance_id)
    
    # 删除数据库记录
    db_instance = db.query(ModelInstance).filter(ModelInstance.id == instance_id).first()
    if not db_instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    db.delete(db_instance)
    db.commit()
    
    return {"success": True, "message": "实例已删除"}


@router.get("/discover")
async def discover_processes():
    """发现系统中现有的 vLLM 进程"""
    processes = vllm_process_manager.discover_existing_processes()
    return {
        "success": True,
        "processes": processes,
        "count": len(processes)
    }


@router.post("/takeover")
async def take_over_process(port: int, model_name: str = None, db: Session = Depends(get_db)):
    """接管指定端口的 vLLM 进程"""
    try:
        instance = await vllm_process_manager.take_over_process(port, model_name)
        
        # 保存到数据库
        db_instance = ModelInstance(
            id=instance.id,
            name=instance.model_name,
            model_name=instance.model_name,
            model_id=instance.model_path,
            model_type="llm",
            status=instance.status,
            replicas=1,
            gpus=[],
            config=instance.config
        )
        db.add(db_instance)
        db.commit()
        
        return {
            "success": True,
            "message": "进程接管成功",
            "instance": instance.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/takeover/all")
async def take_over_all_processes(db: Session = Depends(get_db)):
    """接管所有发现的 vLLM 进程"""
    instances = await vllm_process_manager.take_over_all_processes()
    
    # 保存到数据库
    for instance in instances:
        db_instance = ModelInstance(
            id=instance.id,
            name=instance.model_name,
            model_name=instance.model_name,
            model_id=instance.model_path,
            model_type="llm",
            status=instance.status,
            replicas=1,
            gpus=[],
            config=instance.config
        )
        db.add(db_instance)
    db.commit()
    
    return {
        "success": True,
        "message": f"成功接管 {len(instances)} 个进程",
        "instances": [instance.to_dict() for instance in instances]
    }


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
