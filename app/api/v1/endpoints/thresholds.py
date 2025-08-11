from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_async_db
from app.models import Threshold, Installation, Endpoint
from app.schemas import ThresholdCreate, ThresholdUpdate, ThresholdResponse

router = APIRouter()


@router.post("/", response_model=ThresholdResponse, status_code=status.HTTP_201_CREATED)
async def create_threshold(
    threshold_data: ThresholdCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if installation exists
    installation_result = await db.execute(
        select(Installation).where(Installation.id == threshold_data.installation_id)
    )
    if not installation_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Installation with id {threshold_data.installation_id} does not exist"
        )
    
    # Check if endpoint exists
    endpoint_result = await db.execute(
        select(Endpoint).where(Endpoint.id == threshold_data.endpoint_id)
    )
    if not endpoint_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Endpoint with id {threshold_data.endpoint_id} does not exist"
        )
    
    # Check if threshold already exists (unique constraint)
    existing_result = await db.execute(
        select(Threshold).where(
            Threshold.installation_id == threshold_data.installation_id,
            Threshold.endpoint_id == threshold_data.endpoint_id,
            Threshold.metric_type == threshold_data.metric_type
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Threshold already exists for metric '{threshold_data.metric_type}' on installation {threshold_data.installation_id} and endpoint {threshold_data.endpoint_id}"
        )
    
    threshold = Threshold(**threshold_data.model_dump())
    db.add(threshold)
    await db.commit()
    await db.refresh(threshold)
    return threshold


@router.get("/", response_model=List[ThresholdResponse])
async def list_thresholds(
    skip: int = 0,
    limit: int = 100,
    installation_id: UUID = None,
    endpoint_id: UUID = None,
    metric_type: str = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Threshold)
    
    if installation_id is not None:
        query = query.where(Threshold.installation_id == installation_id)
    
    if endpoint_id is not None:
        query = query.where(Threshold.endpoint_id == endpoint_id)
    
    if metric_type is not None:
        query = query.where(Threshold.metric_type == metric_type)
    
    if is_active is not None:
        query = query.where(Threshold.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    thresholds = result.scalars().all()
    return thresholds


@router.get("/{threshold_id}", response_model=ThresholdResponse)
async def get_threshold(
    threshold_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Threshold).where(Threshold.id == threshold_id)
    )
    threshold = result.scalar_one_or_none()
    
    if not threshold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threshold with id {threshold_id} not found"
        )
    
    return threshold


@router.put("/{threshold_id}", response_model=ThresholdResponse)
async def update_threshold(
    threshold_id: UUID,
    threshold_data: ThresholdUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Threshold).where(Threshold.id == threshold_id)
    )
    threshold = result.scalar_one_or_none()
    
    if not threshold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threshold with id {threshold_id} not found"
        )
    
    # Check for conflicts if metric_type is being changed
    if threshold_data.metric_type and threshold_data.metric_type != threshold.metric_type:
        existing_result = await db.execute(
            select(Threshold).where(
                Threshold.installation_id == threshold.installation_id,
                Threshold.endpoint_id == threshold.endpoint_id,
                Threshold.metric_type == threshold_data.metric_type,
                Threshold.id != threshold_id
            )
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Threshold already exists for metric '{threshold_data.metric_type}' on this installation and endpoint"
            )
    
    for field, value in threshold_data.model_dump(exclude_unset=True).items():
        setattr(threshold, field, value)
    
    await db.commit()
    await db.refresh(threshold)
    return threshold


@router.delete("/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_threshold(
    threshold_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Threshold).where(Threshold.id == threshold_id)
    )
    threshold = result.scalar_one_or_none()
    
    if not threshold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threshold with id {threshold_id} not found"
        )
    
    # Soft delete
    threshold.is_active = False
    await db.commit()