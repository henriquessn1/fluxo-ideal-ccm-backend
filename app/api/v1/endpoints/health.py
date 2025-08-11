from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_async_db
from app.models import Client, Instance, Module, Installation, Endpoint, MonitoringLog

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "monitoring-api-v2",
        "version": "2.0.0"
    }


@router.get("/stats", response_model=Dict[str, Any])
async def system_stats(
    db: AsyncSession = Depends(get_async_db)
):
    # Count total clients
    clients_result = await db.execute(
        select(func.count(Client.id))
    )
    total_clients = clients_result.scalar()
    
    # Count active clients
    active_clients_result = await db.execute(
        select(func.count(Client.id)).where(Client.is_active == True)
    )
    active_clients = active_clients_result.scalar()
    
    # Count total instances
    instances_result = await db.execute(
        select(func.count(Instance.id))
    )
    total_instances = instances_result.scalar()
    
    # Count active instances
    active_instances_result = await db.execute(
        select(func.count(Instance.id)).where(Instance.is_active == True)
    )
    active_instances = active_instances_result.scalar()
    
    # Count total modules
    modules_result = await db.execute(
        select(func.count(Module.id))
    )
    total_modules = modules_result.scalar()
    
    # Count public modules
    public_modules_result = await db.execute(
        select(func.count(Module.id)).where(Module.is_public == True)
    )
    public_modules = public_modules_result.scalar()
    
    # Count total installations
    installations_result = await db.execute(
        select(func.count(Installation.id))
    )
    total_installations = installations_result.scalar()
    
    # Count active installations
    active_installations_result = await db.execute(
        select(func.count(Installation.id)).where(Installation.is_active == True)
    )
    active_installations = active_installations_result.scalar()
    
    # Count total endpoints
    endpoints_result = await db.execute(
        select(func.count(Endpoint.id))
    )
    total_endpoints = endpoints_result.scalar()
    
    # Get recent monitoring logs stats (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_logs_result = await db.execute(
        select(
            MonitoringLog.alert_level,
            func.count(MonitoringLog.id).label('count')
        )
        .where(MonitoringLog.created_at >= one_hour_ago)
        .group_by(MonitoringLog.alert_level)
    )
    recent_logs = {(row.alert_level or 'unknown'): row.count for row in recent_logs_result}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_version": "2.0.0",
        "clients": {
            "total": total_clients,
            "active": active_clients
        },
        "instances": {
            "total": total_instances,
            "active": active_instances
        },
        "modules": {
            "total": total_modules,
            "public": public_modules
        },
        "installations": {
            "total": total_installations,
            "active": active_installations
        },
        "endpoints": {
            "total": total_endpoints
        },
        "recent_monitoring_logs": recent_logs,
        "period": "last_hour"
    }