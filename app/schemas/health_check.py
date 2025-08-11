from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class HealthCheckResponse(BaseModel):
    id: UUID
    client_id: UUID
    service_id: Optional[UUID]
    status: str
    response_time: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    checked_at: datetime
    
    class Config:
        from_attributes = True