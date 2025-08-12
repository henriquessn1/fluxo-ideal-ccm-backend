from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class InstallationBase(BaseModel):
    api_key: str = Field(..., description="API key for authentication")
    config: Optional[Dict[str, Any]] = None


class InstallationCreate(InstallationBase):
    module_id: UUID
    instance_id: UUID


class InstallationUpdate(BaseModel):
    api_key: Optional[str] = Field(None, description="API key for authentication")
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class InstallationResponse(InstallationBase):
    id: UUID
    module_id: UUID
    instance_id: UUID
    api_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InstallationWithDetails(InstallationResponse):
    module: Optional[Dict[str, Any]] = None
    instance: Optional[Dict[str, Any]] = None