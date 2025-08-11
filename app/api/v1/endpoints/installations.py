from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_async_db
from app.models import Installation, Module, Instance
from app.schemas import InstallationCreate, InstallationUpdate, InstallationResponse, InstallationWithDetails

router = APIRouter()


@router.post("/", response_model=InstallationResponse, status_code=status.HTTP_201_CREATED)
async def create_installation(
    installation_data: InstallationCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if module exists
    module_result = await db.execute(
        select(Module).where(Module.id == installation_data.module_id)
    )
    if not module_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with id {installation_data.module_id} does not exist"
        )
    
    # Check if instance exists
    instance_result = await db.execute(
        select(Instance).where(Instance.id == installation_data.instance_id)
    )
    if not instance_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instance with id {installation_data.instance_id} does not exist"
        )
    
    # Check if installation already exists (unique constraint)
    existing_result = await db.execute(
        select(Installation).where(
            Installation.module_id == installation_data.module_id,
            Installation.instance_id == installation_data.instance_id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Installation already exists for module {installation_data.module_id} on instance {installation_data.instance_id}"
        )
    
    installation = Installation(**installation_data.model_dump())
    db.add(installation)
    await db.commit()
    await db.refresh(installation)
    return installation


@router.get("/", response_model=List[InstallationResponse])
async def list_installations(
    skip: int = 0,
    limit: int = 100,
    module_id: UUID = None,
    instance_id: UUID = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Installation)
    
    if module_id is not None:
        query = query.where(Installation.module_id == module_id)
    
    if instance_id is not None:
        query = query.where(Installation.instance_id == instance_id)
    
    if is_active is not None:
        query = query.where(Installation.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    installations = result.scalars().all()
    return installations


@router.get("/{installation_id}", response_model=InstallationWithDetails)
async def get_installation(
    installation_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    # Get installation with relationships
    result = await db.execute(
        select(Installation).where(Installation.id == installation_id)
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Installation with id {installation_id} not found"
        )
    
    # Get module details
    module_result = await db.execute(
        select(Module).where(Module.id == installation.module_id)
    )
    module = module_result.scalar_one_or_none()
    
    # Get instance details
    instance_result = await db.execute(
        select(Instance).where(Instance.id == installation.instance_id)
    )
    instance = instance_result.scalar_one_or_none()
    
    return InstallationWithDetails(
        **installation.__dict__,
        module={
            "id": str(module.id),
            "name": module.name,
            "category": module.category,
            "version": module.version
        } if module else None,
        instance={
            "id": str(instance.id),
            "name": instance.name,
            "host": instance.host,
            "environment": instance.environment
        } if instance else None
    )


@router.put("/{installation_id}", response_model=InstallationResponse)
async def update_installation(
    installation_id: UUID,
    installation_data: InstallationUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Installation).where(Installation.id == installation_id)
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Installation with id {installation_id} not found"
        )
    
    for field, value in installation_data.model_dump(exclude_unset=True).items():
        setattr(installation, field, value)
    
    await db.commit()
    await db.refresh(installation)
    return installation


@router.delete("/{installation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_installation(
    installation_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Installation).where(Installation.id == installation_id)
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Installation with id {installation_id} not found"
        )
    
    # Soft delete
    installation.is_active = False
    await db.commit()


@router.post("/{installation_id}/regenerate-api-key", response_model=InstallationResponse)
async def regenerate_api_key(
    installation_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    import secrets
    
    result = await db.execute(
        select(Installation).where(Installation.id == installation_id)
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Installation with id {installation_id} not found"
        )
    
    # Generate new API key
    new_api_key = f"inst_{secrets.token_urlsafe(32)}"
    installation.api_key = new_api_key
    
    await db.commit()
    await db.refresh(installation)
    return installation