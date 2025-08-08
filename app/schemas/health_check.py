from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HealthCheckResponse(BaseModel):
    id: int
    client_id: int
    service_id: Optional[int]
    status: str
    response_time: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    checked_at: datetime
    
    class Config:
        from_attributes = True