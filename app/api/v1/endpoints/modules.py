from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_async_db
from app.models import Module
from app.schemas import ModuleCreate, ModuleUpdate, ModuleResponse

router = APIRouter()


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # Check if module with same name exists
    result = await db.execute(
        select(Module).where(Module.name == module_data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with name '{module_data.name}' already exists"
        )
    
    module = Module(**module_data.model_dump())
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@router.get("/", response_model=List[ModuleResponse])
async def list_modules(
    skip: int = 0,
    limit: int = 100,
    is_public: bool = None,
    category: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Module)
    
    if is_public is not None:
        query = query.where(Module.is_public == is_public)
    
    if category is not None:
        query = query.where(Module.category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    modules = result.scalars().all()
    return modules


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    return module


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: UUID,
    module_data: ModuleUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    # Check if new name conflicts with existing module
    if module_data.name and module_data.name != module.name:
        result = await db.execute(
            select(Module).where(Module.name == module_data.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Module with name '{module_data.name}' already exists"
            )
    
    for field, value in module_data.model_dump(exclude_unset=True).items():
        setattr(module, field, value)
    
    await db.commit()
    await db.refresh(module)
    return module


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    await db.delete(module)
    await db.commit()