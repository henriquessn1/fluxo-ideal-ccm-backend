from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_async_db
from app.models import Client, Service, HealthCheck
from app.schemas import ClientCreate, ClientUpdate, ClientResponse, ClientWithStatus, ServiceStatus

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if client with same name exists
    result = await db.execute(
        select(Client).where(Client.name == client_data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client with name '{client_data.name}' already exists"
        )
    
    client = Client(**client_data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Client)
    
    if is_active is not None:
        query = query.where(Client.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    clients = result.scalars().all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Check if new name conflicts with existing client
    if client_data.name and client_data.name != client.name:
        result = await db.execute(
            select(Client).where(Client.name == client_data.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Client with name '{client_data.name}' already exists"
            )
    
    for field, value in client_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    await db.delete(client)
    await db.commit()


@router.get("/{client_id}/status", response_model=ClientWithStatus)
async def get_client_status(
    client_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    # Get client with services
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Get all services for this client
    services_result = await db.execute(
        select(Service).where(Service.client_id == client_id)
    )
    services = services_result.scalars().all()
    
    # Get latest health check for each service
    service_statuses = []
    overall_status = "UP"
    
    for service in services:
        # Get the most recent health check for this service
        health_check_result = await db.execute(
            select(HealthCheck)
            .where(HealthCheck.service_id == service.id)
            .order_by(HealthCheck.checked_at.desc())
            .limit(1)
        )
        latest_check = health_check_result.scalar_one_or_none()
        
        service_status = ServiceStatus(
            **service.__dict__,
            status="UNKNOWN" if not latest_check else latest_check.status,
            last_check=latest_check.checked_at if latest_check else None,
            response_time=latest_check.response_time if latest_check else None,
            error_message=latest_check.error_message if latest_check else None
        )
        service_statuses.append(service_status)
        
        # Update overall status
        if latest_check:
            if latest_check.status == "DOWN":
                overall_status = "DOWN"
            elif latest_check.status == "DEGRADED" and overall_status != "DOWN":
                overall_status = "DEGRADED"
    
    # If no services or no health checks, status is UNKNOWN
    if not services or all(s.status == "UNKNOWN" for s in service_statuses):
        overall_status = "UNKNOWN"
    
    return ClientWithStatus(
        **client.__dict__,
        services=service_statuses,
        overall_status=overall_status
    )