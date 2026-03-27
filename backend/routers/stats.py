from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List

from models import get_db, ModelInstance, RequestLog
from schemas import (
    ModelStats, StatsOverview, DailyTrend, LatencyDistribution,
    TokenDistribution, ModelTypeDistribution, ErrorDistribution,
    DashboardStats, UsageStats, CallDistribution, TokenTrend
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_model_stats(range: str = "7d", db: Session = Depends(get_db)):
    """获取模型统计信息"""
    now = datetime.now(timezone.utc)
    if range == "24h":
        start_time = now - timedelta(hours=24)
    elif range == "7d":
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(days=30)

    logs = db.query(RequestLog).filter(RequestLog.created_at >= start_time).all()

    # 概览数据
    total_calls = len(logs)
    success_calls = len([l for l in logs if l.status == "success"])
    failed_calls = total_calls - success_calls
    success_rate = (success_calls / total_calls * 100) if total_calls > 0 else 100

    total_tokens = sum(l.input_tokens + l.output_tokens for l in logs)
    avg_latency = sum(l.latency_ms for l in logs) / len(logs) if logs else 0
    p99_latency = sorted([l.latency_ms for l in logs])[int(len(logs) * 0.99)] if logs else 0
    active_users = len(set(l.user_id for l in logs if l.user_id))

    # 每日趋势
    daily_trend = []
    for i in range(7):
        date = (now - timedelta(days=6-i)).strftime("%m-%d")
        day_start = now - timedelta(days=6-i)
        day_end = now - timedelta(days=5-i)
        day_calls = len([l for l in logs if day_start <= l.created_at < day_end])
        daily_trend.append(DailyTrend(date=date, calls=day_calls))

    # 延迟分布
    latency_distribution = []
    for hour in range(0, 24, 4):
        hour_logs = [l for l in logs if l.created_at.hour >= hour and l.created_at.hour < hour + 4]
        if hour_logs:
            latencies = [l.latency_ms for l in hour_logs]
            latencies.sort()
            latency_distribution.append(LatencyDistribution(
                time=f"{hour:02d}:00",
                p50=latencies[int(len(latencies) * 0.5)],
                p95=latencies[int(len(latencies) * 0.95)],
                p99=latencies[int(len(latencies) * 0.99)] if len(latencies) > 1 else latencies[0]
            ))

    # Token使用量分布
    token_distribution = []
    model_stats = {}
    for log in logs:
        if log.model_name not in model_stats:
            model_stats[log.model_name] = {"input": 0, "output": 0}
        model_stats[log.model_name]["input"] += log.input_tokens
        model_stats[log.model_name]["output"] += log.output_tokens

    for model_name, stats in sorted(model_stats.items(), key=lambda x: x[1]["input"] + x[1]["output"], reverse=True)[:6]:
        token_distribution.append(TokenDistribution(
            model=model_name,
            input=stats["input"],
            output=stats["output"]
        ))

    # 模型类型占比
    type_stats = {}
    for log in logs:
        model_type = "LLM"
        type_stats[model_type] = type_stats.get(model_type, 0) + 1

    model_type_distribution = [
        ModelTypeDistribution(name=t, value=c)
        for t, c in type_stats.items()
    ]

    # 错误类型分布
    error_logs = [l for l in logs if l.status == "error"]
    error_stats = {}
    for log in error_logs:
        error_type = log.error_type or "其他"
        error_stats[error_type] = error_stats.get(error_type, 0) + 1

    error_distribution = []
    for error_type, count in sorted(error_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(error_logs) * 100) if error_logs else 0
        error_distribution.append(ErrorDistribution(
            type=error_type,
            count=count,
            percentage=round(percentage, 1)
        ))

    return ModelStats(
        overview=StatsOverview(
            total_calls=f"{total_calls / 1000:.0f}K" if total_calls > 1000 else str(total_calls),
            calls_trend=12.5,
            total_tokens=f"{total_tokens / 1000000:.0f}M" if total_tokens > 1000000 else f"{total_tokens / 1000:.0f}K",
            tokens_trend=8.3,
            avg_latency=round(avg_latency, 0),
            p99_latency=round(p99_latency, 0),
            success_rate=round(success_rate, 1),
            failed_calls=failed_calls,
            active_users=active_users,
            users_trend=5.2
        ),
        daily_trend=daily_trend,
        latency_distribution=latency_distribution,
        token_distribution=token_distribution,
        model_type_distribution=model_type_distribution,
        error_distribution=error_distribution
    )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取工作台统计数据"""
    now = datetime.utcnow()
    start_time = now - timedelta(days=7)
    logs = db.query(RequestLog).filter(RequestLog.created_at >= start_time).all()

    # 按模型统计使用量
    model_usage = {}
    for log in logs:
        if log.model_name not in model_usage:
            model_usage[log.model_name] = 0
        model_usage[log.model_name] += 1

    # 使用排行
    usage_stats = [
        UsageStats(model_name=name, usage=count)
        for name, count in sorted(model_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # 调用分布
    call_distribution = [
        CallDistribution(name=name, value=count)
        for name, count in sorted(model_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # Token趋势
    token_trend = []
    for i in range(7):
        date = (now - timedelta(days=6-i)).strftime("%m-%d")
        day_start = now - timedelta(days=6-i)
        day_end = now - timedelta(days=5-i)
        day_logs = [l for l in logs if day_start <= l.created_at < day_end]
        day_tokens = sum(l.input_tokens + l.output_tokens for l in day_logs)
        token_trend.append(TokenTrend(date=date, value=day_tokens))

    return DashboardStats(
        usage_stats=usage_stats,
        call_distribution=call_distribution,
        token_trend=token_trend
    )
