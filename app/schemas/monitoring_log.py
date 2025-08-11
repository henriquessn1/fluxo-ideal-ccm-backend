from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class MonitoringLogBase(BaseModel):
    response_time_ms: Optional[int] = None
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    alert_level: Optional[str] = Field(None, max_length=20)
    alert_triggered: bool = False
    extra_data: Optional[Dict[str, Any]] = None


class MonitoringLogCreate(MonitoringLogBase):
    installation_id: UUID
    endpoint_id: UUID


class MonitoringLogResponse(MonitoringLogBase):
    id: UUID
    installation_id: UUID
    endpoint_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class MonitoringLogWithDetails(MonitoringLogResponse):
    installation: Optional[Dict[str, Any]] = None
    endpoint: Optional[Dict[str, Any]] = None


class MonitoringLogQuery(BaseModel):
    installation_id: Optional[UUID] = None
    endpoint_id: Optional[UUID] = None
    alert_level: Optional[str] = None
    alert_triggered: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)