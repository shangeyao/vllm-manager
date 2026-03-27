"""
ModelScope 模型下载器
使用 modelscope 库或 git 下载模型
"""

import os
import subprocess
import threading
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import json
from config import settings


class ModelDownloadTask:
    """模型下载任务"""
    
    def __init__(self, model_id: str, local_path: str):
        self.model_id = model_id
        self.local_path = local_path
        self.status = "pending"  # pending, downloading, completed, failed
        self.progress = 0.0
        self.error_message = ""
        self.total_files = 0
        self.downloaded_files = 0
        self.current_file = ""
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "local_path": self.local_path,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "total_files": self.total_files,
            "downloaded_files": self.downloaded_files,
            "current_file": self.current_file,
        }


class ModelScopeDownloader:
    """ModelScope 模型下载器"""
    
    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.active_downloads: Dict[str, ModelDownloadTask] = {}
        self._lock = threading.Lock()
        
    def get_model_local_path(self, model_id: str) -> str:
        """获取模型本地路径"""
        # 将 model_id 中的 / 替换为 _
        safe_name = model_id.replace("/", "_")
        return str(self.cache_dir / safe_name)
    
    def is_model_cached(self, model_id: str) -> bool:
        """检查模型是否已缓存"""
        local_path = self.get_model_local_path(model_id)
        model_dir = Path(local_path)
        
        if not model_dir.exists():
            return False
        
        # 检查是否有模型文件（config.json 或 pytorch_model.bin 等）
        essential_files = [
            "config.json",
            "pytorch_model.bin",
            "model.safetensors",
            "pytorch_model.bin.index.json",
            "model.safetensors.index.json",
        ]
        
        for file in essential_files:
            if (model_dir / file).exists():
                return True
        
        return False
    
    def download_model(
        self,
        model_id: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> ModelDownloadTask:
        """
        下载模型
        
        Args:
            model_id: ModelScope 模型 ID，如 "qwen/Qwen2-7B-Instruct"
            progress_callback: 进度回调函数 (progress, current_file)
        
        Returns:
            下载任务对象
        """
        with self._lock:
            # 检查是否已有进行中的下载
            if model_id in self.active_downloads:
                return self.active_downloads[model_id]
            
            # 创建下载任务
            local_path = self.get_model_local_path(model_id)
            task = ModelDownloadTask(model_id, local_path)
            self.active_downloads[model_id] = task
        
        # 在后台线程中执行下载
        thread = threading.Thread(
            target=self._download_worker,
            args=(task, progress_callback)
        )
        thread.daemon = True
        thread.start()
        
        return task
    
    def _download_worker(
        self,
        task: ModelDownloadTask,
        progress_callback: Optional[Callable[[float, str], None]]
    ):
        """下载工作线程"""
        try:
            task.status = "downloading"
            
            # 方法1: 尝试使用 modelscope 库下载
            if self._try_modelscope_sdk_download(task, progress_callback):
                task.status = "completed"
                task.progress = 100.0
            else:
                # 方法2: 使用 git lfs 下载
                if self._try_git_lfs_download(task, progress_callback):
                    task.status = "completed"
                    task.progress = 100.0
                else:
                    task.status = "failed"
                    task.error_message = "所有下载方法都失败了"
                    
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            print(f"Error downloading model {task.model_id}: {e}")
        
        finally:
            # 通知回调
            if progress_callback:
                progress_callback(task.progress, task.current_file)
    
    def _try_modelscope_sdk_download(
        self,
        task: ModelDownloadTask,
        progress_callback: Optional[Callable[[float, str], None]]
    ) -> bool:
        """尝试使用 ModelScope SDK 下载"""
        try:
            # 尝试导入 modelscope
            from modelscope import snapshot_download
            
            def progress_handler(name, current, total):
                """处理下载进度"""
                task.current_file = name
                task.downloaded_files = current
                task.total_files = total
                
                if total > 0:
                    task.progress = (current / total) * 100
                
                if progress_callback:
                    progress_callback(task.progress, name)
            
            task.current_file = "正在使用 ModelScope SDK 下载..."
            
            # 使用 snapshot_download 下载模型
            snapshot_download(
                model_id=task.model_id,
                cache_dir=str(self.cache_dir),
                local_files_only=False,
            )
            
            return True
            
        except ImportError:
            print("ModelScope SDK not installed, trying git lfs...")
            return False
        except Exception as e:
            print(f"ModelScope SDK download failed: {e}")
            return False
    
    def _try_git_lfs_download(
        self,
        task: ModelDownloadTask,
        progress_callback: Optional[Callable[[float, str], None]]
    ) -> bool:
        """尝试使用 git lfs 下载"""
        try:
            local_path = Path(task.local_path)
            local_path.mkdir(parents=True, exist_ok=True)
            
            # ModelScope Git URL
            git_url = f"https://www.modelscope.cn/{task.model_id}.git"
            
            task.current_file = "正在使用 Git LFS 克隆..."
            if progress_callback:
                progress_callback(10, task.current_file)
            
            # 检查是否已部分克隆
            git_dir = local_path / ".git"
            if git_dir.exists():
                # 已存在，执行 git pull
                task.current_file = "正在更新模型..."
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=str(local_path),
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            else:
                # 新克隆
                task.current_file = "正在克隆仓库..."
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", git_url, str(local_path)],
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
            
            if result.returncode != 0:
                task.error_message = f"Git clone failed: {result.stderr}"
                return False
            
            if progress_callback:
                progress_callback(50, "Git clone completed")
            
            # 拉取 LFS 文件
            task.current_file = "正在下载 LFS 文件..."
            if progress_callback:
                progress_callback(60, task.current_file)
            
            result = subprocess.run(
                ["git", "lfs", "pull"],
                cwd=str(local_path),
                capture_output=True,
                text=True,
                timeout=3600,  # 1小时超时
            )
            
            if result.returncode != 0:
                task.error_message = f"Git LFS pull failed: {result.stderr}"
                return False
            
            if progress_callback:
                progress_callback(100, "Download completed")
            
            return True
            
        except subprocess.TimeoutExpired:
            task.error_message = "Download timeout"
            return False
        except Exception as e:
            task.error_message = f"Git LFS download failed: {str(e)}"
            return False
    
    def get_download_task(self, model_id: str) -> Optional[ModelDownloadTask]:
        """获取下载任务状态"""
        with self._lock:
            return self.active_downloads.get(model_id)
    
    def remove_download_task(self, model_id: str):
        """移除下载任务"""
        with self._lock:
            if model_id in self.active_downloads:
                del self.active_downloads[model_id]
    
    def list_cached_models(self) -> list:
        """列出所有已缓存的模型"""
        cached_models = []
        
        if not self.cache_dir.exists():
            return cached_models
        
        for model_dir in self.cache_dir.iterdir():
            if model_dir.is_dir():
                model_id = model_dir.name.replace("_", "/")
                if self.is_model_cached(model_id):
                    cached_models.append({
                        "model_id": model_id,
                        "local_path": str(model_dir),
                        "size": self._get_dir_size(model_dir),
                    })
        
        return cached_models
    
    def _get_dir_size(self, path: Path) -> int:
        """获取目录大小"""
        total = 0
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    
    def delete_model(self, model_id: str) -> bool:
        """删除已下载的模型"""
        try:
            local_path = Path(self.get_model_local_path(model_id))
            if local_path.exists():
                import shutil
                shutil.rmtree(local_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting model {model_id}: {e}")
            return False


# 全局下载器实例 - 使用配置的缓存目录
modelscope_downloader = ModelScopeDownloader(cache_dir=settings.MODEL_CACHE_DIR)


if __name__ == "__main__":
    # 测试下载
    downloader = ModelScopeDownloader()
    
    def progress_callback(progress, current_file):
        print(f"Progress: {progress:.1f}% - {current_file}")
    
    # 测试下载一个小模型
    task = downloader.download_model(
        "qwen/Qwen2-0.5B-Instruct",
        progress_callback=progress_callback
    )
    
    # 等待下载完成
    import time
    while task.status == "downloading":
        time.sleep(1)
        print(f"Status: {task.status}, Progress: {task.progress:.1f}%")
    
    print(f"Final status: {task.status}")
    if task.error_message:
        print(f"Error: {task.error_message}")
