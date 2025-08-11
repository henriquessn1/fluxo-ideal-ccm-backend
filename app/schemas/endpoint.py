from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class EndpointBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    relative_path: str = Field(..., min_length=1, max_length=500)
    method: str = Field("GET", max_length=10)
    type: Optional[str] = Field(None, max_length=50)
    expected_response_time_ms: int = Field(1000, ge=1)
    timeout_ms: int = Field(30000, ge=1000)


class EndpointCreate(EndpointBase):
    module_id: UUID


class EndpointUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    relative_path: Optional[str] = Field(None, min_length=1, max_length=500)
    method: Optional[str] = Field(None, max_length=10)
    type: Optional[str] = Field(None, max_length=50)
    expected_response_time_ms: Optional[int] = Field(None, ge=1)
    timeout_ms: Optional[int] = Field(None, ge=1000)


class EndpointResponse(EndpointBase):
    id: UUID
    module_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True