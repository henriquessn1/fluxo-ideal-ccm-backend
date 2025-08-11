from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_async_db
from app.models import Endpoint, Module
from app.schemas import EndpointCreate, EndpointUpdate, EndpointResponse

router = APIRouter()


@router.post("/", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    endpoint_data: EndpointCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if module exists
    result = await db.execute(
        select(Module).where(Module.id == endpoint_data.module_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with id {endpoint_data.module_id} does not exist"
        )
    
    endpoint = Endpoint(**endpoint_data.model_dump())
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)
    return endpoint


@router.get("/", response_model=List[EndpointResponse])
async def list_endpoints(
    skip: int = 0,
    limit: int = 100,
    module_id: UUID = None,
    type: str = None,
    method: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Endpoint)
    
    if module_id is not None:
        query = query.where(Endpoint.module_id == module_id)
    
    if type is not None:
        query = query.where(Endpoint.type == type)
    
    if method is not None:
        query = query.where(Endpoint.method == method)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    endpoints = result.scalars().all()
    return endpoints


@router.get("/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(
    endpoint_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Endpoint).where(Endpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint with id {endpoint_id} not found"
        )
    
    return endpoint


@router.put("/{endpoint_id}", response_model=EndpointResponse)
async def update_endpoint(
    endpoint_id: UUID,
    endpoint_data: EndpointUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Endpoint).where(Endpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint with id {endpoint_id} not found"
        )
    
    for field, value in endpoint_data.model_dump(exclude_unset=True).items():
        setattr(endpoint, field, value)
    
    await db.commit()
    await db.refresh(endpoint)
    return endpoint


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(
    endpoint_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Endpoint).where(Endpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint with id {endpoint_id} not found"
        )
    
    await db.delete(endpoint)
    await db.commit()