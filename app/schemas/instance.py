from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class InstanceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    host: str = Field(..., min_length=1, max_length=255)
    environment: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, max_length=50)
    admin_api_key: Optional[str] = Field(None, description="Admin API key for elevated permissions")


class InstanceCreate(InstanceBase):
    client_id: UUID


class InstanceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    environment: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, max_length=50)
    admin_api_key: Optional[str] = Field(None, description="Admin API key for elevated permissions")
    is_active: Optional[bool] = None


class InstanceResponse(InstanceBase):
    id: UUID
    client_id: UUID
    admin_api_key: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True