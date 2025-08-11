from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_async_db
from app.models import Client
from app.schemas import ClientCreate, ClientUpdate, ClientResponse, ClientWithInstances

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
    client_id: UUID,
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
    client_id: UUID,
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
    client_id: UUID,
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
    
    # Soft delete
    client.is_active = False
    await db.commit()


@router.get("/{client_id}/instances", response_model=ClientWithInstances)
async def get_client_with_instances(
    client_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    from app.models import Instance
    
    # Get client
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Get all instances for this client
    instances_result = await db.execute(
        select(Instance).where(Instance.client_id == client_id)
    )
    instances = instances_result.scalars().all()
    
    instances_data = [
        {
            "id": str(instance.id),
            "name": instance.name,
            "host": instance.host,
            "environment": instance.environment,
            "version": instance.version,
            "is_active": instance.is_active,
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat()
        }
        for instance in instances
    ]
    
    return ClientWithInstances(
        **client.__dict__,
        instances=instances_data
    )