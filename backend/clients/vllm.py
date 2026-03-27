"""
vLLM 客户端实现
提供与 vLLM OpenAI 兼容 API 的交互
"""

import os
import asyncio
import subprocess
import threading
import socket
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, field

import httpx

from clients.base import InferenceClient
from config import settings
from vllm_params import build_vllm_command_args


@dataclass
class VLLMInstance:
    """vLLM 实例信息"""
    id: str
    model_name: str
    model_path: str
    port: int
    process: Optional[subprocess.Popen] = None
    status: str = "starting"  # starting, running, stopping, stopped, error
    status_message: str = ""
    logs: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    _log_callbacks: List[Callable] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add_log(self, level: str, message: str, timestamp: Optional[datetime] = None):
        """添加日志并通知回调"""
        with self._lock:
            log_entry = {
                "timestamp": (timestamp or datetime.now()).isoformat(),
                "level": level,
                "message": message
            }
            self.logs.append(log_entry)
            if len(self.logs) > 10000:
                self.logs = self.logs[-5000:]

        for callback in self._log_callbacks:
            try:
                callback(log_entry)
            except Exception as e:
                print(f"Log callback error: {e}")

    def register_log_callback(self, callback: Callable):
        """注册日志回调"""
        with self._lock:
            if callback not in self._log_callbacks:
                self._log_callbacks.append(callback)

    def unregister_log_callback(self, callback: Callable):
        """注销日志回调"""
        with self._lock:
            if callback in self._log_callbacks:
                self._log_callbacks.remove(callback)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "model_name": self.model_name,
            "model_path": self.model_path,
            "port": self.port,
            "status": self.status,
            "status_message": self.status_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "config": self.config,
            "log_count": len(self.logs)
        }


class VLLMClient(InferenceClient):
    """vLLM HTTP 客户端 - 与 vLLM OpenAI 兼容 API 交互"""

    def __init__(self, base_url: str = None, api_key: str = None):
        base_url = base_url or settings.VLLM_BASE_URL
        api_key = api_key or settings.VLLM_API_KEY
        super().__init__(base_url, api_key)
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """延迟初始化 httpx 客户端"""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=60.0
            )
        return self._client

    async def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        try:
            client = self._get_client()
            response = await client.get("/v1/models")
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Failed to get models: {e}")
            return []

    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取模型详细信息"""
        try:
            client = self._get_client()
            response = await client.get(f"/v1/models/{model_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get model info: {e}")
            return None

    async def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """创建聊天完成请求"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            client = self._get_client()
            response = await client.post("/v1/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Chat completion failed: {e}")
            raise

    async def create_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """创建文本完成请求"""
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": stream
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            client = self._get_client()
            response = await client.post("/v1/completions", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Completion failed: {e}")
            raise

    async def create_embedding(self, model: str, input_text: str) -> Dict[str, Any]:
        """创建嵌入向量"""
        payload = {
            "model": model,
            "input": input_text
        }

        try:
            client = self._get_client()
            response = await client.post("/v1/embeddings", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Embedding failed: {e}")
            raise

    async def stream_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            client = self._get_client()
            async with client.stream("POST", "/v1/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        yield data
        except Exception as e:
            print(f"Stream chat completion failed: {e}")
            raise

    async def check_health(self) -> bool:
        """检查 vLLM 服务健康状态"""
        try:
            client = self._get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except:
            return False

    async def get_metrics(self) -> Optional[str]:
        """获取 Prometheus 指标"""
        try:
            client = self._get_client()
            response = await client.get("/metrics")
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Failed to get metrics: {e}")
            return None

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None


class VLLMProcessManager:
    """vLLM 进程管理器 - 负责启动、停止和管理 vLLM 服务实例"""

    def __init__(self):
        self.instances: Dict[str, VLLMInstance] = {}
        self._port_lock = threading.Lock()
        self._used_ports: set = set()
        self._lock = threading.Lock()

    def _find_available_port(self) -> int:
        """查找可用端口"""
        with self._port_lock:
            for port in range(settings.VLLM_PORT_RANGE_START, settings.VLLM_PORT_RANGE_END):
                if port not in self._used_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.bind(("localhost", port))
                        sock.close()
                        self._used_ports.add(port)
                        return port
                    except socket.error:
                        continue
        raise RuntimeError("No available ports in range")

    def _release_port(self, port: int):
        """释放端口"""
        with self._port_lock:
            self._used_ports.discard(port)

    def _build_vllm_command(
        self, model_path: str, port: int, **kwargs
    ) -> List[str]:
        """构建 vLLM 启动命令"""
        python_cmd = "python3" if os.system("which python3 > /dev/null 2>&1") == 0 else "python"

        cmd = [
            python_cmd, "-m", "vllm.entrypoints.openai.api_server",
            "--model", model_path,
            "--port", str(port),
            "--download-dir", settings.MODEL_CACHE_DIR,
        ]

        vllm_args = build_vllm_command_args(kwargs)
        cmd.extend(vllm_args)

        return cmd

    def _parse_log_line(self, instance: VLLMInstance, line: str):
        """解析日志行并更新状态"""
        level = "INFO"
        upper_line = line.upper()
        if "ERROR" in upper_line or "EXCEPTION" in upper_line or "FAILED" in upper_line:
            level = "ERROR"
        elif "WARNING" in upper_line or "WARN" in upper_line:
            level = "WARN"
        elif "DEBUG" in upper_line:
            level = "DEBUG"

        instance.add_log(level, line)

        if "Uvicorn running on" in line or "Application startup complete" in line:
            instance.status = "running"
            instance.status_message = "Server is ready"
            instance.add_log("SUCCESS", "vLLM server is ready!")
        elif "Loading model weights" in line:
            instance.status_message = "Loading model weights..."
        elif "Loading tokenizer" in line:
            instance.status_message = "Loading tokenizer..."
        elif "Initializing the engine" in line:
            instance.status_message = "Initializing engine..."

    def _run_vllm_process(self, instance: VLLMInstance, cmd: List[str]):
        """运行 vLLM 进程并捕获输出"""
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["VLLM_LOGGING_LEVEL"] = "INFO"

            instance.add_log("INFO", "Starting vLLM process...")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )

            instance.process = process
            instance.status = "starting"

            for line in iter(process.stdout.readline, ""):
                line = line.strip()
                if line:
                    self._parse_log_line(instance, line)

            process.wait()

            if process.returncode == 0:
                instance.status = "stopped"
                instance.add_log("INFO", "vLLM process stopped normally")
            else:
                instance.status = "error"
                instance.add_log("ERROR", f"vLLM process exited with code {process.returncode}")

        except Exception as e:
            instance.status = "error"
            instance.add_log("ERROR", f"Failed to start vLLM: {str(e)}")
        finally:
            instance.end_time = datetime.now()
            self._release_port(instance.port)

    async def start_model(
        self,
        model_name: str,
        model_id: Optional[str] = None,
        **kwargs
    ) -> VLLMInstance:
        """启动 vLLM 模型实例"""
        import uuid

        instance_id = str(uuid.uuid4())
        actual_model_id = model_id or model_name

        # 检查模型是否已下载
        from modelscope_downloader import modelscope_downloader
        if modelscope_downloader.is_model_cached(actual_model_id):
            model_path = modelscope_downloader.get_model_local_path(actual_model_id)
        else:
            model_path = actual_model_id

        port = self._find_available_port()

        instance = VLLMInstance(
            id=instance_id,
            model_name=model_name,
            model_path=model_path,
            port=port,
            start_time=datetime.now(),
            config=kwargs
        )

        with self._lock:
            self.instances[instance_id] = instance

        cmd = self._build_vllm_command(
            model_path=model_path,
            port=port,
            **kwargs
        )

        instance.add_log("INFO", f"Starting vLLM server with command: {' '.join(cmd)}")
        instance.add_log("INFO", f"Model path: {model_path}")
        instance.add_log("INFO", f"Port: {port}")

        threading.Thread(
            target=self._run_vllm_process,
            args=(instance, cmd),
            daemon=True
        ).start()

        return instance

    async def stop_model(self, instance_id: str) -> bool:
        """停止模型实例"""
        with self._lock:
            instance = self.instances.get(instance_id)

        if not instance:
            return False

        if instance.process and instance.process.poll() is None:
            instance.status = "stopping"
            instance.add_log("INFO", "Stopping vLLM process...")

            try:
                instance.process.terminate()

                for _ in range(10):
                    if instance.process.poll() is not None:
                        break
                    await asyncio.sleep(1)

                if instance.process.poll() is None:
                    instance.process.kill()
                    instance.add_log("WARN", "Process killed forcefully")

                instance.status = "stopped"
                instance.add_log("INFO", "vLLM process stopped")
                return True

            except Exception as e:
                instance.add_log("ERROR", f"Error stopping process: {e}")
                return False

        return True

    def get_instance(self, instance_id: str) -> Optional[VLLMInstance]:
        """获取实例信息"""
        with self._lock:
            return self.instances.get(instance_id)

    def list_instances(self) -> List[Dict[str, Any]]:
        """列出所有实例"""
        with self._lock:
            return [inst.to_dict() for inst in self.instances.values()]

    def get_instance_logs(
        self,
        instance_id: str,
        offset: int = 0,
        limit: int = 100,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取实例日志"""
        instance = self.get_instance(instance_id)
        if not instance:
            return []

        logs = instance.logs
        if level:
            logs = [log for log in logs if log["level"] == level]

        return logs[offset:offset + limit]

    async def check_instance_health(self, instance_id: str) -> bool:
        """检查实例健康状态"""
        instance = self.get_instance(instance_id)
        if not instance or instance.status != "running":
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:{instance.port}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

    def cleanup_stopped_instances(self):
        """清理已停止的实例"""
        with self._lock:
            to_remove = [
                id for id, inst in self.instances.items()
                if inst.status in ["stopped", "error"] and inst.end_time
                and (datetime.now() - inst.end_time).total_seconds() > 3600
            ]
            for id in to_remove:
                del self.instances[id]


# 全局实例
vllm_client = VLLMClient()
vllm_process_manager = VLLMProcessManager()
