from fastapi import APIRouter
from .endpoints import (
    clients, instances, modules, installations, 
    endpoints as endpoint_routes, thresholds, monitoring_logs,
    # Legacy endpoints (will be updated/removed)
    services, health
)

api_router = APIRouter()

# New API endpoints
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(instances.router, prefix="/instances", tags=["instances"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(installations.router, prefix="/installations", tags=["installations"])
api_router.include_router(endpoint_routes.router, prefix="/endpoints", tags=["endpoints"])
api_router.include_router(thresholds.router, prefix="/thresholds", tags=["thresholds"])
api_router.include_router(monitoring_logs.router, prefix="/monitoring-logs", tags=["monitoring-logs"])

# Legacy endpoints (deprecated - will be removed in future versions)
api_router.include_router(services.router, prefix="/services", tags=["services", "deprecated"])
api_router.include_router(health.router, prefix="/health", tags=["health"])