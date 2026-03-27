from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from models import get_db, RequestLog
from schemas import ChatRequest, CompletionRequest, EmbeddingRequest
from clients import vllm_client

router = APIRouter(tags=["proxy"])


@router.post("/api/v1/chat/completions")
async def chat_completion(request: ChatRequest, db: Session = Depends(get_db)):
    """聊天完成 API - 代理到 vLLM"""
    start_time = datetime.utcnow()

    try:
        response = await vllm_client.create_chat_completion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )

        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        usage = response.get("usage", {})

        log = RequestLog(
            id=str(uuid.uuid4()),
            model_id=request.model,
            model_name=request.model,
            request_type="chat",
            status="success",
            latency_ms=latency,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0)
        )
        db.add(log)
        db.commit()

        return response
    except Exception as e:
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        log = RequestLog(
            id=str(uuid.uuid4()),
            model_id=request.model,
            model_name=request.model,
            request_type="chat",
            status="error",
            latency_ms=latency,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        db.add(log)
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/completions")
async def text_completion(request: CompletionRequest, db: Session = Depends(get_db)):
    """文本完成 API - 代理到 vLLM"""
    start_time = datetime.utcnow()

    try:
        response = await vllm_client.create_completion(
            model=request.model,
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )

        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        usage = response.get("usage", {})

        log = RequestLog(
            id=str(uuid.uuid4()),
            model_id=request.model,
            model_name=request.model,
            request_type="completion",
            status="success",
            latency_ms=latency,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0)
        )
        db.add(log)
        db.commit()

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/embeddings")
async def create_embedding(request: EmbeddingRequest, db: Session = Depends(get_db)):
    """嵌入向量 API - 代理到 vLLM"""
    try:
        response = await vllm_client.create_embedding(
            model=request.model,
            input_text=request.input
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
