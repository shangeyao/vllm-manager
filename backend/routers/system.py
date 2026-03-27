from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib
import secrets

from models import get_db, ModelInstance, RequestLog, User, Role, ApiKey, SystemConfig
from schemas import (
    UserCreate, UserUpdate, UserResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    ApiKeyCreate, ApiKeyResponse, SystemConfigItem, SystemOverview
)
from monitor import system_monitor

router = APIRouter(prefix="/system", tags=["system"])


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_api_key() -> str:
    """生成新的 API Key"""
    return "vllm_" + secrets.token_urlsafe(32)


@router.get("/overview", response_model=SystemOverview)
async def get_system_overview(db: Session = Depends(get_db)):
    """获取系统概览信息"""
    import psutil

    sys_info = system_monitor.get_system_overview()
    disk_info = sys_info.get("disk", {})

    active_models = db.query(ModelInstance).filter(ModelInstance.status == "running").count()
    total_requests = db.query(RequestLog).count()
    uptime = "7天 12小时"

    return SystemOverview(
        version="1.0.0",
        uptime=uptime,
        database_status="connected",
        storage_used=disk_info.get("used", 0),
        storage_total=disk_info.get("total", 0),
        cpu_usage=sys_info["cpu"]["percent"],
        memory_usage=sys_info["memory"]["percent"],
        active_models=active_models,
        total_requests=total_requests
    )


# 用户管理 API
@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    """获取用户列表"""
    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被使用")

    user = User(
        id=str(secrets.token_hex(16)),
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    if user_data.role:
        user.role = user_data.role
    if user_data.status:
        user.status = user_data.status

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(user)
    db.commit()
    return {"success": True, "message": "用户已删除"}


# 角色管理 API
@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(db: Session = Depends(get_db)):
    """获取角色列表"""
    roles = db.query(Role).all()
    return roles


@router.post("/roles", response_model=RoleResponse)
async def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    """创建角色"""
    existing = db.query(Role).filter(Role.name == role_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色名已存在")

    role = Role(
        id=str(secrets.token_hex(16)),
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: str, db: Session = Depends(get_db)):
    """获取角色详情"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """更新角色信息"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role_data.name:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permissions is not None:
        role.permissions = role_data.permissions

    role.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str, db: Session = Depends(get_db)):
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    db.delete(role)
    db.commit()
    return {"success": True, "message": "角色已删除"}


# API Key 管理 API
@router.get("/keys", response_model=List[ApiKeyResponse])
async def list_api_keys(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """获取 API Key 列表"""
    query = db.query(ApiKey)
    if user_id:
        query = query.filter(ApiKey.user_id == user_id)
    keys = query.all()
    return keys


@router.post("/keys", response_model=ApiKeyResponse)
async def create_api_key(key_data: ApiKeyCreate, db: Session = Depends(get_db)):
    """创建 API Key"""
    api_key = generate_api_key()
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    key_record = ApiKey(
        id=str(secrets.token_hex(16)),
        name=key_data.name,
        key_hash=key_hash,
        user_id="admin",
        permissions=key_data.permissions,
        status="active",
        expires_at=key_data.expires_at
    )
    db.add(key_record)
    db.commit()
    db.refresh(key_record)

    response_data = ApiKeyResponse(
        id=key_record.id,
        name=key_record.name,
        key=api_key,
        user_id=key_record.user_id,
        permissions=key_record.permissions,
        status=key_record.status,
        last_used_at=key_record.last_used_at,
        created_at=key_record.created_at,
        expires_at=key_record.expires_at
    )
    return response_data


@router.delete("/keys/{key_id}")
async def revoke_api_key(key_id: str, db: Session = Depends(get_db)):
    """撤销 API Key"""
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key 不存在")

    key.status = "revoked"
    db.commit()
    return {"success": True, "message": "API Key 已撤销"}


# 系统配置 API
@router.get("/config")
async def list_system_config(db: Session = Depends(get_db)):
    """获取系统配置列表"""
    configs = db.query(SystemConfig).all()
    return {
        "configs": [
            {"key": c.key, "value": c.value, "description": c.description}
            for c in configs
        ]
    }


@router.get("/config/{key}")
async def get_system_config(key: str, db: Session = Depends(get_db)):
    """获取系统配置项"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    return {"key": config.key, "value": config.value, "description": config.description}


@router.put("/config/{key}")
async def update_system_config(key: str, config_data: SystemConfigItem, db: Session = Depends(get_db)):
    """更新系统配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        config = SystemConfig(
            key=key,
            value=config_data.value,
            description=config_data.description
        )
        db.add(config)
    else:
        config.value = config_data.value
        if config_data.description:
            config.description = config_data.description

    db.commit()
    return {"success": True, "message": "配置已更新"}


@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
):
    """获取系统日志（简化版本）"""
    logs = [
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
            "level": "INFO" if i % 5 != 0 else "WARN",
            "message": f"系统运行正常 - 日志条目 {i}",
            "source": "backend"
        }
        for i in range(min(limit, 50))
    ]
    return {"logs": logs}
