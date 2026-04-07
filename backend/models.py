from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()

# 创建数据库引擎
database_url = settings.get_database_url()
connect_args = settings.get_db_connect_args()
pool_args = settings.get_db_pool_args()

engine = create_engine(
    database_url,
    connect_args=connect_args,
    **pool_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ModelInstance(Base):
    __tablename__ = "model_instances"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    model_id = Column(String)
    model_type = Column(String, nullable=False)
    status = Column(String, default="stopped")
    version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    replicas = Column(Integer, default=1)
    gpus = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    node = Column(String)


class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(String, primary_key=True)
    model_id = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    request_type = Column(String, nullable=False)  # chat, completion, embedding
    status = Column(String, nullable=False)  # success, error
    latency_ms = Column(Float)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    error_type = Column(String)
    error_message = Column(String)
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    request_metadata = Column(JSON, default=dict)


class GPUStats(Base):
    __tablename__ = "gpu_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    gpu_index = Column(Integer, nullable=False)
    gpu_name = Column(String)
    utilization = Column(Float)
    memory_used = Column(Float)
    memory_total = Column(Float)
    temperature = Column(Float)
    power = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class NodeInfo(Base):
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    ip = Column(String)
    status = Column(String, default="offline")
    cpu_percent = Column(Float)
    memory_used = Column(Float)
    memory_total = Column(Float)
    last_seen = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, user, viewer
    status = Column(String, default="active")  # active, disabled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    permissions = Column(JSON, default=list)
    status = Column(String, default="active")  # active, revoked
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(String)
    description = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
