from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_async_db
from app.models import Client, Service, HealthCheck

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "monitoring-api"
    }


@router.get("/stats", response_model=Dict[str, Any])
async def health_stats(
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
    
    # Count total services
    services_result = await db.execute(
        select(func.count(Service.id))
    )
    total_services = services_result.scalar()
    
    # Count active services
    active_services_result = await db.execute(
        select(func.count(Service.id)).where(Service.is_active == True)
    )
    active_services = active_services_result.scalar()
    
    # Get recent health checks stats (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_checks_result = await db.execute(
        select(
            HealthCheck.status,
            func.count(HealthCheck.id).label('count')
        )
        .where(HealthCheck.checked_at >= one_hour_ago)
        .group_by(HealthCheck.status)
    )
    recent_checks = {row.status: row.count for row in recent_checks_result}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "clients": {
            "total": total_clients,
            "active": active_clients
        },
        "services": {
            "total": total_services,
            "active": active_services
        },
        "recent_health_checks": recent_checks,
        "period": "last_hour"
    }