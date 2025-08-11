from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Endpoint(BaseModel):
    __tablename__ = "endpoints"
    
    # Foreign keys
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    relative_path = Column(String(500), nullable=False)
    method = Column(String(10), default="GET", nullable=False)  # GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
    type = Column(String(50), nullable=True)  # health, metrics, status, custom
    
    # Configuration
    expected_response_time_ms = Column(Integer, default=1000, nullable=False)
    timeout_ms = Column(Integer, default=30000, nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="endpoints")
    thresholds = relationship("Threshold", back_populates="endpoint", cascade="all, delete-orphan")
    monitoring_logs = relationship("MonitoringLog", back_populates="endpoint", cascade="all, delete-orphan")