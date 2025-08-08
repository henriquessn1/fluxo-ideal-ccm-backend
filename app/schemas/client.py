from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .service import ServiceStatus


class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    dns: str = Field(..., min_length=1, max_length=255)
    api_key: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    dns: Optional[str] = Field(None, min_length=1, max_length=255)
    api_key: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientWithStatus(ClientResponse):
    services: List[ServiceStatus] = []
    overall_status: str = "UNKNOWN"  # UP, DOWN, DEGRADED, UNKNOWN