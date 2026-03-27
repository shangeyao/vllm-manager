from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "vLLM Manager Backend"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # vLLM Settings
    VLLM_BASE_URL: str = "http://localhost:8001"  # vLLM OpenAI compatible server URL (default)
    VLLM_API_KEY: Optional[str] = None
    VLLM_PORT_RANGE_START: int = 8001  # vLLM 实例端口范围起始
    VLLM_PORT_RANGE_END: int = 8100    # vLLM 实例端口范围结束
    
    # Model Cache Settings
    MODEL_CACHE_DIR: str = os.path.expanduser("~/.cache/vllm-manager/models")  # 模型下载缓存目录
    
    # Database Settings
    DB_TYPE: str = "sqlite"  # sqlite, mysql, postgresql
    DATABASE_URL: Optional[str] = None  # 完整的数据库URL，如果设置则优先使用
    
    # MySQL Settings
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "vllm_manager"
    MYSQL_CHARSET: str = "utf8mb4"
    MYSQL_POOL_SIZE: int = 10
    MYSQL_MAX_OVERFLOW: int = 20
    MYSQL_POOL_TIMEOUT: int = 30
    MYSQL_POOL_RECYCLE: int = 3600
    
    # PostgreSQL Settings (预留)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DATABASE: str = "vllm_manager"
    
    # Monitoring
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.DB_TYPE == "mysql":
            return (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
                f"?charset={self.MYSQL_CHARSET}"
            )
        elif self.DB_TYPE == "postgresql":
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"
            )
        else:  # sqlite
            return "sqlite:///./vllm_manager.db"
    
    def get_db_connect_args(self) -> dict:
        """获取数据库连接参数"""
        if self.DB_TYPE == "sqlite":
            return {"check_same_thread": False}
        return {}
    
    def get_db_pool_args(self) -> dict:
        """获取数据库连接池参数"""
        if self.DB_TYPE == "mysql":
            return {
                "pool_size": self.MYSQL_POOL_SIZE,
                "max_overflow": self.MYSQL_MAX_OVERFLOW,
                "pool_timeout": self.MYSQL_POOL_TIMEOUT,
                "pool_recycle": self.MYSQL_POOL_RECYCLE,
            }
        elif self.DB_TYPE == "postgresql":
            return {
                "pool_size": 10,
                "max_overflow": 20,
            }
        return {}


settings = Settings()
