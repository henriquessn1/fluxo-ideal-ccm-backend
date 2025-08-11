from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ThresholdBase(BaseModel):
    metric_type: str = Field(..., min_length=1, max_length=50)
    warning_min: Optional[Decimal] = None
    warning_max: Optional[Decimal] = None
    error_min: Optional[Decimal] = None
    error_max: Optional[Decimal] = None
    expected_values: Optional[Dict[str, Any]] = None


class ThresholdCreate(ThresholdBase):
    installation_id: UUID
    endpoint_id: UUID


class ThresholdUpdate(BaseModel):
    metric_type: Optional[str] = Field(None, min_length=1, max_length=50)
    warning_min: Optional[Decimal] = None
    warning_max: Optional[Decimal] = None
    error_min: Optional[Decimal] = None
    error_max: Optional[Decimal] = None
    expected_values: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ThresholdResponse(ThresholdBase):
    id: UUID
    installation_id: UUID
    endpoint_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True