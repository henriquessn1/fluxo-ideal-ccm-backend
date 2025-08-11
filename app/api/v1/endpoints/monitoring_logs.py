from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_async_db
from app.models import MonitoringLog, Installation, Endpoint
from app.schemas import MonitoringLogCreate, MonitoringLogResponse, MonitoringLogWithDetails, MonitoringLogQuery

router = APIRouter()


@router.post("/", response_model=MonitoringLogResponse, status_code=status.HTTP_201_CREATED)
async def create_monitoring_log(
    log_data: MonitoringLogCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if installation exists
    installation_result = await db.execute(
        select(Installation).where(Installation.id == log_data.installation_id)
    )
    if not installation_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Installation with id {log_data.installation_id} does not exist"
        )
    
    # Check if endpoint exists
    endpoint_result = await db.execute(
        select(Endpoint).where(Endpoint.id == log_data.endpoint_id)
    )
    if not endpoint_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Endpoint with id {log_data.endpoint_id} does not exist"
        )
    
    monitoring_log = MonitoringLog(**log_data.model_dump())
    db.add(monitoring_log)
    await db.commit()
    await db.refresh(monitoring_log)
    return monitoring_log


@router.get("/", response_model=List[MonitoringLogResponse])
async def list_monitoring_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    installation_id: Optional[UUID] = None,
    endpoint_id: Optional[UUID] = None,
    alert_level: Optional[str] = None,
    alert_triggered: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(MonitoringLog).order_by(desc(MonitoringLog.created_at))
    
    if installation_id is not None:
        query = query.where(MonitoringLog.installation_id == installation_id)
    
    if endpoint_id is not None:
        query = query.where(MonitoringLog.endpoint_id == endpoint_id)
    
    if alert_level is not None:
        query = query.where(MonitoringLog.alert_level == alert_level)
    
    if alert_triggered is not None:
        query = query.where(MonitoringLog.alert_triggered == alert_triggered)
    
    if start_date is not None:
        query = query.where(MonitoringLog.created_at >= start_date)
    
    if end_date is not None:
        query = query.where(MonitoringLog.created_at <= end_date)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/search", response_model=List[MonitoringLogResponse])
async def search_monitoring_logs(
    query_params: MonitoringLogQuery = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    query = select(MonitoringLog).order_by(desc(MonitoringLog.created_at))
    
    if query_params.installation_id is not None:
        query = query.where(MonitoringLog.installation_id == query_params.installation_id)
    
    if query_params.endpoint_id is not None:
        query = query.where(MonitoringLog.endpoint_id == query_params.endpoint_id)
    
    if query_params.alert_level is not None:
        query = query.where(MonitoringLog.alert_level == query_params.alert_level)
    
    if query_params.alert_triggered is not None:
        query = query.where(MonitoringLog.alert_triggered == query_params.alert_triggered)
    
    if query_params.start_date is not None:
        query = query.where(MonitoringLog.created_at >= query_params.start_date)
    
    if query_params.end_date is not None:
        query = query.where(MonitoringLog.created_at <= query_params.end_date)
    
    query = query.offset(query_params.offset).limit(query_params.limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/{log_id}", response_model=MonitoringLogWithDetails)
async def get_monitoring_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    # Get monitoring log
    result = await db.execute(
        select(MonitoringLog).where(MonitoringLog.id == log_id)
    )
    monitoring_log = result.scalar_one_or_none()
    
    if not monitoring_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitoring log with id {log_id} not found"
        )
    
    # Get installation details
    installation_result = await db.execute(
        select(Installation).where(Installation.id == monitoring_log.installation_id)
    )
    installation = installation_result.scalar_one_or_none()
    
    # Get endpoint details
    endpoint_result = await db.execute(
        select(Endpoint).where(Endpoint.id == monitoring_log.endpoint_id)
    )
    endpoint = endpoint_result.scalar_one_or_none()
    
    return MonitoringLogWithDetails(
        **monitoring_log.__dict__,
        installation={
            "id": str(installation.id),
            "api_key": installation.api_key[:8] + "...",  # Masked for security
            "config": installation.config
        } if installation else None,
        endpoint={
            "id": str(endpoint.id),
            "name": endpoint.name,
            "relative_path": endpoint.relative_path,
            "method": endpoint.method,
            "type": endpoint.type
        } if endpoint else None
    )


@router.get("/stats/summary")
async def get_monitoring_stats(
    installation_id: Optional[UUID] = None,
    endpoint_id: Optional[UUID] = None,
    hours: int = Query(24, ge=1, le=168),  # Last 1-168 hours (1 week max)
    db: AsyncSession = Depends(get_async_db)
):
    from sqlalchemy import func
    from datetime import timedelta
    
    # Calculate time window
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Base query
    query = select(
        MonitoringLog.alert_level,
        func.count(MonitoringLog.id).label('count'),
        func.avg(MonitoringLog.response_time_ms).label('avg_response_time'),
        func.max(MonitoringLog.response_time_ms).label('max_response_time'),
        func.min(MonitoringLog.response_time_ms).label('min_response_time')
    ).where(
        MonitoringLog.created_at >= start_time,
        MonitoringLog.created_at <= end_time
    )
    
    if installation_id:
        query = query.where(MonitoringLog.installation_id == installation_id)
    
    if endpoint_id:
        query = query.where(MonitoringLog.endpoint_id == endpoint_id)
    
    query = query.group_by(MonitoringLog.alert_level)
    
    result = await db.execute(query)
    stats = result.all()
    
    summary = {
        "period": f"last_{hours}_hours",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "stats_by_alert_level": {}
    }
    
    for stat in stats:
        summary["stats_by_alert_level"][stat.alert_level or "unknown"] = {
            "count": stat.count,
            "avg_response_time_ms": float(stat.avg_response_time) if stat.avg_response_time else None,
            "max_response_time_ms": stat.max_response_time,
            "min_response_time_ms": stat.min_response_time
        }
    
    return summary


@router.delete("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_old_logs(
    days_to_keep: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_async_db)
):
    from datetime import timedelta
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    # Delete old logs
    result = await db.execute(
        select(func.count(MonitoringLog.id)).where(
            MonitoringLog.created_at < cutoff_date
        )
    )
    count_to_delete = result.scalar()
    
    if count_to_delete > 0:
        # Delete old logs
        from sqlalchemy import delete
        await db.execute(
            delete(MonitoringLog).where(
                MonitoringLog.created_at < cutoff_date
            )
        )
        await db.commit()
    
    return {
        "message": f"Cleanup completed",
        "logs_deleted": count_to_delete,
        "cutoff_date": cutoff_date.isoformat(),
        "days_kept": days_to_keep
    }