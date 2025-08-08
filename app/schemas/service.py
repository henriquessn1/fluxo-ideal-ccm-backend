from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    endpoint: str = Field(..., min_length=1, max_length=500)
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    headers: Optional[Dict[str, str]] = None
    expected_status: int = Field(default=200, ge=100, le=599)
    timeout: int = Field(default=30, ge=1, le=300)
    description: Optional[str] = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    client_id: int


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    endpoint: Optional[str] = Field(None, min_length=1, max_length=500)
    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    headers: Optional[Dict[str, str]] = None
    expected_status: Optional[int] = Field(None, ge=100, le=599)
    timeout: Optional[int] = Field(None, ge=1, le=300)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServiceStatus(ServiceResponse):
    status: str = "UNKNOWN"  # UP, DOWN, DEGRADED, UNKNOWN
    last_check: Optional[datetime] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None