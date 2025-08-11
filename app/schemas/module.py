from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    relative_path: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)
    is_public: bool = True


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    relative_path: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)
    is_public: Optional[bool] = None


class ModuleResponse(ModuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True