from fastapi import APIRouter, HTTPException
from typing import Optional

from modelscope_downloader import modelscope_downloader

router = APIRouter(prefix="/models", tags=["downloads"])


@router.post("/download")
async def download_model_endpoint(request: dict):
    """开始下载模型"""
    model_id = request.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    # 检查是否已缓存
    if modelscope_downloader.is_model_cached(model_id):
        return {
            "success": True,
            "message": "模型已存在",
            "status": "completed",
            "local_path": modelscope_downloader.get_model_local_path(model_id)
        }

    # 检查是否已在下载中
    existing_task = modelscope_downloader.get_download_task(model_id)
    if existing_task and existing_task.status == "downloading":
        return {
            "success": True,
            "message": "模型正在下载中",
            "status": "downloading",
            "progress": existing_task.progress
        }

    # 开始下载
    def progress_callback(progress, current_file):
        print(f"Download {model_id}: {progress:.1f}% - {current_file}")

    task = modelscope_downloader.download_model(model_id, progress_callback)

    return {
        "success": True,
        "message": "开始下载模型",
        "status": task.status,
        "progress": task.progress
    }


@router.get("/download/status")
async def get_download_status(model_id: str):
    """获取模型下载状态"""
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    # 检查是否已缓存
    if modelscope_downloader.is_model_cached(model_id):
        return {
            "model_id": model_id,
            "status": "completed",
            "progress": 100.0,
            "local_path": modelscope_downloader.get_model_local_path(model_id)
        }

    # 获取下载任务
    task = modelscope_downloader.get_download_task(model_id)
    if task:
        return task.to_dict()

    return {
        "model_id": model_id,
        "status": "not_found",
        "progress": 0.0,
        "message": "没有找到下载任务"
    }


@router.get("/cached")
async def list_cached_models():
    """列出所有已缓存的模型"""
    cached = modelscope_downloader.list_cached_models()
    return {
        "success": True,
        "models": cached,
        "count": len(cached)
    }


@router.delete("/cached")
async def delete_cached_model(request: dict):
    """删除已缓存的模型"""
    model_id = request.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    success = modelscope_downloader.delete_model(model_id)
    if success:
        return {"success": True, "message": f"模型 {model_id} 已删除"}
    else:
        raise HTTPException(status_code=500, detail="删除模型失败")
