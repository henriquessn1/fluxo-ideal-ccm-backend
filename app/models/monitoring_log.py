from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, UUIDMixin


class MonitoringLog(Base, UUIDMixin):
    __tablename__ = "monitoring_logs"
    
    # Foreign keys
    installation_id = Column(UUID(as_uuid=True), ForeignKey("installations.id", ondelete="CASCADE"), nullable=False)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False)
    
    # Response data
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Alert levels
    alert_level = Column(String(20), nullable=True, index=True)  # ok, warning, error, critical
    alert_triggered = Column(Boolean, default=False, nullable=False)
    
    # Additional metadata
    extra_data = Column(JSON, nullable=True)
    
    # Timestamp (only created_at, no updated_at for logs)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    installation = relationship("Installation", back_populates="monitoring_logs")
    endpoint = relationship("Endpoint", back_populates="monitoring_logs")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_monitoring_logs_installation_endpoint_created', 'installation_id', 'endpoint_id', 'created_at'),
        Index('ix_monitoring_logs_created_desc', created_at.desc()),
    )