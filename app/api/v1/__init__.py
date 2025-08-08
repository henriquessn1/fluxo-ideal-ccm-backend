from fastapi import APIRouter
from .endpoints import clients, services, health

api_router = APIRouter()

api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(health.router, prefix="/health", tags=["health"])