import httpx
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Client, Service, HealthCheck
from app.core.config import settings


class HealthChecker:
    def __init__(self):
        self.timeout = settings.HEALTH_CHECK_TIMEOUT
    
    async def check_service(self, service: Service, api_key: str) -> Dict[str, Any]:
        """Check a single service health"""
        start_time = datetime.utcnow()
        
        try:
            headers = service.headers or {}
            headers['X-API-Key'] = api_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=service.method,
                    url=f"{service.endpoint}",
                    headers=headers
                )
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == service.expected_status:
                    status = "UP"
                elif 200 <= response.status_code < 400:
                    status = "DEGRADED"
                else:
                    status = "DOWN"
                
                return {
                    "status": status,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error_message": None
                }
                
        except httpx.TimeoutException:
            return {
                "status": "DOWN",
                "response_time": self.timeout * 1000,
                "status_code": None,
                "error_message": "Service timeout"
            }
        except httpx.RequestError as e:
            return {
                "status": "DOWN",
                "response_time": None,
                "status_code": None,
                "error_message": str(e)
            }
        except Exception as e:
            return {
                "status": "DOWN",
                "response_time": None,
                "status_code": None,
                "error_message": f"Unexpected error: {str(e)}"
            }
    
    async def check_client_services(self, db: AsyncSession, client_id: int):
        """Check all services for a client"""
        # Get client
        client_result = await db.execute(
            select(Client).where(Client.id == client_id, Client.is_active == True)
        )
        client = client_result.scalar_one_or_none()
        
        if not client:
            return
        
        # Get active services for this client
        services_result = await db.execute(
            select(Service).where(
                Service.client_id == client_id,
                Service.is_active == True
            )
        )
        services = services_result.scalars().all()
        
        # Check each service
        for service in services:
            result = await self.check_service(service, client.api_key)
            
            # Save health check result
            health_check = HealthCheck(
                client_id=client_id,
                service_id=service.id,
                status=result["status"],
                response_time=result["response_time"],
                status_code=result["status_code"],
                error_message=result["error_message"]
            )
            db.add(health_check)
        
        await db.commit()
    
    async def check_all_clients(self, db: AsyncSession):
        """Check all active clients and their services"""
        # Get all active clients
        result = await db.execute(
            select(Client).where(Client.is_active == True)
        )
        clients = result.scalars().all()
        
        # Check each client's services concurrently
        tasks = [
            self.check_client_services(db, client.id)
            for client in clients
        ]
        
        if tasks:
            await asyncio.gather(*tasks)
    
    def check_service_sync(self, service: Service, api_key: str) -> Dict[str, Any]:
        """Synchronous version for Celery tasks"""
        start_time = datetime.utcnow()
        
        try:
            headers = service.headers or {}
            headers['X-API-Key'] = api_key
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=service.method,
                    url=f"{service.endpoint}",
                    headers=headers
                )
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == service.expected_status:
                    status = "UP"
                elif 200 <= response.status_code < 400:
                    status = "DEGRADED"
                else:
                    status = "DOWN"
                
                return {
                    "status": status,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error_message": None
                }
                
        except httpx.TimeoutException:
            return {
                "status": "DOWN",
                "response_time": self.timeout * 1000,
                "status_code": None,
                "error_message": "Service timeout"
            }
        except httpx.RequestError as e:
            return {
                "status": "DOWN",
                "response_time": None,
                "status_code": None,
                "error_message": str(e)
            }
        except Exception as e:
            return {
                "status": "DOWN",
                "response_time": None,
                "status_code": None,
                "error_message": f"Unexpected error: {str(e)}"
            }
    
    def check_client_services_sync(self, db: Session, client_id: int):
        """Synchronous version for Celery tasks"""
        # Get client
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.is_active == True
        ).first()
        
        if not client:
            return
        
        # Get active services for this client
        services = db.query(Service).filter(
            Service.client_id == client_id,
            Service.is_active == True
        ).all()
        
        # Check each service
        for service in services:
            result = self.check_service_sync(service, client.api_key)
            
            # Save health check result
            health_check = HealthCheck(
                client_id=client_id,
                service_id=service.id,
                status=result["status"],
                response_time=result["response_time"],
                status_code=result["status_code"],
                error_message=result["error_message"]
            )
            db.add(health_check)
        
        db.commit()