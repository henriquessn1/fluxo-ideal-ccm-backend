from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_async_db
from app.models import Instance, Client
from app.schemas import InstanceCreate, InstanceUpdate, InstanceResponse

router = APIRouter()


@router.post("/", response_model=InstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_instance(
    instance_data: InstanceCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if client exists
    result = await db.execute(
        select(Client).where(Client.id == instance_data.client_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client with id {instance_data.client_id} does not exist"
        )
    
    instance = Instance(**instance_data.model_dump())
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


@router.get("/", response_model=List[InstanceResponse])
async def list_instances(
    skip: int = 0,
    limit: int = 100,
    client_id: UUID = None,
    is_active: bool = None,
    environment: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Instance)
    
    if client_id is not None:
        query = query.where(Instance.client_id == client_id)
    
    if is_active is not None:
        query = query.where(Instance.is_active == is_active)
    
    if environment is not None:
        query = query.where(Instance.environment == environment)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    instances = result.scalars().all()
    return instances


@router.get("/{instance_id}", response_model=InstanceResponse)
async def get_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id)
    )
    instance = result.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance with id {instance_id} not found"
        )
    
    return instance


@router.put("/{instance_id}", response_model=InstanceResponse)
async def update_instance(
    instance_id: UUID,
    instance_data: InstanceUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id)
    )
    instance = result.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance with id {instance_id} not found"
        )
    
    for field, value in instance_data.model_dump(exclude_unset=True).items():
        setattr(instance, field, value)
    
    await db.commit()
    await db.refresh(instance)
    return instance


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id)
    )
    instance = result.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance with id {instance_id} not found"
        )
    
    # Soft delete
    instance.is_active = False
    await db.commit()