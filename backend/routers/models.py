from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models import get_db, ModelInstance
from schemas import ModelInfo, ModelInstanceCreate, ModelInstanceResponse, ModelSpecInfo
from clients import modelscope_client, vllm_process_manager
from modelscope_downloader import modelscope_downloader
from builtin_models import get_builtin_models

router = APIRouter(prefix="/models", tags=["models"])

# 缓存模型列表
_model_cache: List[Dict[str, Any]] = []
_model_cache_time: Optional[datetime] = None
_model_cache_loaded: bool = False


def load_builtin_models() -> List[Dict[str, Any]]:
    """加载内置模型列表"""
    builtin_models = get_builtin_models()
    return [m.model_dump() for m in builtin_models]


def model_info_to_dict(model_info) -> Dict[str, Any]:
    """将 ModelInfo 对象转换为字典"""
    return {
        "model_name": model_info.model_name,
        "model_description": model_info.model_description,
        "model_type": model_info.model_type.value if hasattr(model_info.model_type, 'value') else model_info.model_type,
        "model_family": model_info.model_family,
        "languages": model_info.languages,
        "abilities": model_info.abilities,
        "context_length": model_info.context_length,
        "model_specs": [
            {
                "model_format": spec.model_format,
                "model_size_in_billions": spec.model_size_in_billions,
                "quantizations": spec.quantizations,
                "model_id": spec.model_id,
                "model_revision": spec.model_revision,
                "model_hub": spec.model_hub,
            }
            for spec in model_info.specs
        ],
        "tags": model_info.tags,
        "downloads": model_info.downloads,
        "likes": model_info.likes,
    }


async def get_cached_models(
    model_type: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """获取模型列表（带缓存）"""
    global _model_cache, _model_cache_time, _model_cache_loaded

    if not _model_cache_loaded or not _model_cache:
        _model_cache = load_builtin_models()
        _model_cache_time = datetime.now()
        _model_cache_loaded = True

    models = _model_cache

    if model_type and model_type != "all":
        models = [m for m in models if m.get("model_type") == model_type]

    if search:
        search_lower = search.lower()
        models = [m for m in models if search_lower in m.get("model_name", "").lower()]

    return models


async def search_models_from_source(
    search_query: Optional[str] = None,
    default_orgs: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """从 ModelScope 搜索模型"""
    try:
        if not search_query and default_orgs:
            all_models = []
            for org in default_orgs:
                org_models = await modelscope_client.get_models_by_organization(org, page_size=100)
                if org_models:
                    all_models.extend(org_models)

            if not all_models:
                return []

            seen_ids = set()
            unique_models = []
            for m in all_models:
                if m.model_id and m.model_id not in seen_ids:
                    seen_ids.add(m.model_id)
                    unique_models.append(model_info_to_dict(m))

            return unique_models

        if not search_query:
            models = await modelscope_client.get_popular_models()
            if not models:
                return []
            return [model_info_to_dict(m) for m in models]

        search_lower = search_query.lower()
        default_organizations = ['qwen', 'moonshot', 'ZhipuAI', 'minimax', 'deepseek-ai']

        is_default_org = any(org.lower() == search_lower for org in default_organizations)
        models = []

        if is_default_org or search_lower in [org.lower() for org in default_organizations]:
            for org in default_organizations:
                if search_lower in org.lower() or org.lower() in search_lower:
                    org_models = await modelscope_client.get_models_by_organization(org, page_size=100)
                    if org_models:
                        models.extend(org_models)
                    break

        if not models:
            all_models = await modelscope_client.get_popular_models()
            if all_models:
                models = [m for m in all_models if search_lower in m.model_id.lower()]

        if not models:
            return []

        converted = [model_info_to_dict(m) for m in models]

        if search_query:
            converted = [m for m in converted if
                        search_lower in m.get("model_name", "").lower() or
                        search_lower in m.get("model_id", "").lower()]

        return converted

    except Exception as e:
        print(f"Error searching models: {e}")
        return []


@router.post("/refresh")
async def refresh_models(params: dict = None):
    """刷新模型列表"""
    global _model_cache, _model_cache_time, _model_cache_loaded

    params = params or {}
    search_query = params.get("searchQuery", "").strip()
    default_organizations = ['qwen', 'moonshot', 'ZhipuAI', 'minimax', 'deepseek-ai']

    try:
        if search_query:
            models = await search_models_from_source(search_query=search_query)
            source = "modelscope_search"
        else:
            models = await search_models_from_source(
                search_query=None,
                default_orgs=default_organizations
            )
            source = "modelscope_default_orgs"

        if not models:
            models = load_builtin_models()
            source = "builtin"

        _model_cache = models
        _model_cache_time = datetime.now()
        _model_cache_loaded = True

        return {
            "success": True,
            "message": f"成功更新模型列表，共 {len(models)} 个模型 (来源: {source})",
            "count": len(models),
            "source": source
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新模型列表失败: {str(e)}")


@router.get("", response_model=List[ModelInfo])
async def list_models(
    model_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取模型列表"""
    ms_models = await get_cached_models(model_type=model_type, search=search)

    local_instances = db.query(ModelInstance).all()
    instance_map = {inst.model_name: inst for inst in local_instances}

    cached_models = modelscope_downloader.list_cached_models()
    cached_ids = {m["model_id"] for m in cached_models}

    models = []
    for model_data in ms_models:
        model_name = model_data.get("model_name", "")
        instance = instance_map.get(model_name)
        specs_data = model_data.get("model_specs", [])

        specs = []
        for s in specs_data:
            specs.append(ModelSpecInfo(
                model_format=s.get("model_format", "pytorch"),
                model_size_in_billions=s.get("model_size_in_billions"),
                quantizations=s.get("quantizations", ["none"]),
                model_id=s.get("model_id", ""),
                model_revision=s.get("model_revision"),
                model_hub=s.get("model_hub", "modelscope")
            ))

        is_cached = any(s.model_id in cached_ids for s in specs if s.model_id)

        model_info = ModelInfo(
            id=model_name,
            name=model_name,
            description=model_data.get("model_description", ""),
            type=model_data.get("model_type", "llm"),
            status=instance.status if instance else None,
            size=f"{specs[0].model_size_in_billions}B" if specs and specs[0].model_size_in_billions else None,
            language=model_data.get("languages", ["en"]),
            abilities=model_data.get("abilities", []),
            format=specs[0].model_format if specs else "pytorch",
            quantization=specs[0].quantizations[0] if specs and specs[0].quantizations else None,
            context_length=model_data.get("context_length", 8192),
            cached=is_cached,
            specs=specs
        )
        models.append(model_info)

    return models


@router.post("/launch")
async def launch_model(
    model_data: ModelInstanceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """启动模型实例（旧接口，保留兼容）"""
    try:
        instance = ModelInstance(
            id=str(uuid.uuid4()),
            name=model_data.name,
            model_name=model_data.model_name,
            model_type=model_data.model_type,
            status="starting",
            replicas=model_data.replicas,
            gpus=model_data.gpus,
            config=model_data.config
        )
        db.add(instance)
        db.commit()

        # 使用新的 vllm_process_manager
        await vllm_process_manager.start_model(
            model_name=model_data.model_name,
            model_id=model_data.config.get("model_id"),
            tensor_parallel_size=model_data.config.get("tensor_parallel_size", 1),
            gpu_memory_utilization=model_data.config.get("gpu_memory_utilization", 0.9)
        )

        return {"success": True, "message": "模型启动中", "instance_id": instance.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy")
async def deploy_model_endpoint(params: dict, db: Session = Depends(get_db)):
    """部署模型"""
    try:
        model_name = params.get("modelName")
        model_id = params.get("modelId")

        if not model_name:
            raise HTTPException(status_code=400, detail="模型名称不能为空")

        # 获取模型详情
        model_detail = await modelscope_client.get_model_detail(model_id or model_name)
        model_type = model_detail.model_type.value if model_detail else "llm"

        # 提取 vLLM 参数
        vllm_params = {k: v for k, v in params.items() if k not in ["modelName", "modelId"]}

        # 参数名转换
        param_mapping = {
            "tensorParallelSize": "tensor_parallel_size",
            "gpuMemoryUtilization": "gpu_memory_utilization",
            "maxModelLen": "max_model_len",
            "kvCacheDtype": "kv_cache_dtype",
            "blockSize": "block_size",
            "swapSpace": "swap_space",
            "cpuOffloadGb": "cpu_offload_gb",
            "maxNumBatchedTokens": "max_num_batched_tokens",
            "maxNumSeqs": "max_num_seqs",
            "enableChunkedPrefill": "enable_chunked_prefill",
            "enablePrefixCaching": "enable_prefix_caching",
            "enforceEager": "enforce_eager",
            "trustRemoteCode": "trust_remote_code",
            "gpuIndices": "gpu_indices",
        }

        converted_params = {}
        for key, value in vllm_params.items():
            new_key = param_mapping.get(key, key)
            if isinstance(value, str) and value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            converted_params[new_key] = value

        instance = await vllm_process_manager.start_model(
            model_name=model_name,
            model_id=model_id,
            **converted_params
        )

        db_instance = ModelInstance(
            id=instance.id,
            name=f"{model_name}-instance",
            model_name=model_name,
            model_type=model_type if isinstance(model_type, str) else model_type.value,
            status=instance.status,
            replicas=1,
            gpus=params.get("gpuIndices", []),
            config={"model_id": model_id, "port": instance.port, **converted_params}
        )
        db.add(db_instance)
        db.commit()

        return {
            "success": True,
            "message": "模型部署中",
            "instance_id": instance.id,
            "port": instance.port,
            "status": instance.status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
