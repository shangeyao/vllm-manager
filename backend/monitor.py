import psutil
import pynvml
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPUMonitor:
    """GPU监控器 - 使用pynvml获取真实的GPU信息"""
    
    def __init__(self):
        self.initialized = False
        self.handle = None
        try:
            pynvml.nvmlInit()
            self.initialized = True
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            logger.info("NVML initialized successfully")
        except pynvml.NVMLError as e:
            logger.warning(f"Failed to initialize NVML: {e}. GPU monitoring will be disabled.")
    
    def get_gpu_count(self) -> int:
        """获取GPU数量"""
        if not self.initialized:
            return 0
        try:
            return pynvml.nvmlDeviceGetCount()
        except:
            return 0
    
    def get_gpu_info(self, index: int) -> Optional[Dict[str, Any]]:
        """获取指定GPU的详细信息"""
        if not self.initialized:
            return None
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            
            # 获取GPU名称
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            # 获取利用率
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_util = utilization.gpu
            
            # 获取显存信息
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_used = mem_info.used / 1024 / 1024 / 1024  # GB
            mem_total = mem_info.total / 1024 / 1024 / 1024  # GB
            
            # 获取温度
            try:
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                temperature = 0
            
            # 获取功耗
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # W
            except:
                power = 0
            
            return {
                "id": f"gpu-{index}",
                "name": name,
                "index": index,
                "utilization": gpu_util,
                "memory_used": round(mem_used, 2),
                "memory_total": round(mem_total, 2),
                "temperature": temperature,
                "power": round(power, 1)
            }
        except Exception as e:
            logger.error(f"Error getting GPU {index} info: {e}")
            return None
    
    def get_all_gpus(self) -> List[Dict[str, Any]]:
        """获取所有GPU信息"""
        if not self.initialized:
            return []
        
        gpus = []
        count = self.get_gpu_count()
        for i in range(count):
            info = self.get_gpu_info(i)
            if info:
                gpus.append(info)
        return gpus
    
    def shutdown(self):
        """关闭NVML"""
        if self.initialized:
            try:
                pynvml.nvmlShutdown()
                logger.info("NVML shutdown successfully")
            except:
                pass


class SystemMonitor:
    """系统监控器 - 获取CPU、内存等系统信息"""
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """获取CPU信息"""
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
        }
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """获取内存信息"""
        mem = psutil.virtual_memory()
        return {
            "total": round(mem.total / 1024 / 1024 / 1024, 2),  # GB
            "used": round(mem.used / 1024 / 1024 / 1024, 2),    # GB
            "percent": mem.percent,
            "available": round(mem.available / 1024 / 1024 / 1024, 2)  # GB
        }
    
    @staticmethod
    def get_disk_info() -> Dict[str, Any]:
        """获取磁盘信息"""
        disk = psutil.disk_usage('/')
        return {
            "total": round(disk.total / 1024 / 1024 / 1024, 2),  # GB
            "used": round(disk.used / 1024 / 1024 / 1024, 2),    # GB
            "free": round(disk.free / 1024 / 1024 / 1024, 2),    # GB
            "percent": disk.percent
        }
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """获取网络信息"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    @classmethod
    def get_system_overview(cls) -> Dict[str, Any]:
        """获取系统概览"""
        return {
            "cpu": cls.get_cpu_info(),
            "memory": cls.get_memory_info(),
            "disk": cls.get_disk_info(),
            "network": cls.get_network_info(),
            "timestamp": datetime.utcnow().isoformat()
        }


class MetricsCollector:
    """指标收集器 - 收集和存储系统指标"""
    
    def __init__(self):
        self.gpu_monitor = GPUMonitor()
        self.system_monitor = SystemMonitor()
        self.running = False
        self.callbacks = []
    
    def register_callback(self, callback):
        """注册回调函数，当新指标可用时调用"""
        self.callbacks.append(callback)
    
    async def collect_loop(self, interval: int = 5):
        """持续收集指标的循环"""
        self.running = True
        logger.info(f"Starting metrics collection loop with interval {interval}s")
        
        while self.running:
            try:
                metrics = self.collect_metrics()
                
                # 调用所有回调
                for callback in self.callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(metrics)
                        else:
                            callback(metrics)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(interval)
    
    def collect_metrics(self) -> Dict[str, Any]:
        """收集所有指标"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": self.system_monitor.get_system_overview(),
            "gpus": self.gpu_monitor.get_all_gpus()
        }
    
    def stop(self):
        """停止收集"""
        self.running = False
        self.gpu_monitor.shutdown()


# 全局监控器实例
gpu_monitor = GPUMonitor()
system_monitor = SystemMonitor()
metrics_collector = MetricsCollector()


if __name__ == "__main__":
    # 测试监控功能
    print("GPU Info:")
    for gpu in gpu_monitor.get_all_gpus():
        print(f"  GPU {gpu['index']}: {gpu['name']}")
        print(f"    Utilization: {gpu['utilization']}%")
        print(f"    Memory: {gpu['memory_used']}/{gpu['memory_total']} GB")
        print(f"    Temperature: {gpu['temperature']}°C")
        print(f"    Power: {gpu['power']}W")
    
    print("\nSystem Info:")
    sys_info = system_monitor.get_system_overview()
    print(f"  CPU: {sys_info['cpu']['percent']}%")
    print(f"  Memory: {sys_info['memory']['used']}/{sys_info['memory']['total']} GB ({sys_info['memory']['percent']}%)")
