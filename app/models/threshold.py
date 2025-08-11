from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, SoftDeleteMixin


class Threshold(BaseModel, SoftDeleteMixin):
    __tablename__ = "thresholds"
    
    # Foreign keys
    installation_id = Column(UUID(as_uuid=True), ForeignKey("installations.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metric configuration
    metric_type = Column(String(50), nullable=False)  # response_time, status_code, availability, custom
    
    # Warning levels
    warning_min = Column(Numeric, nullable=True)
    warning_max = Column(Numeric, nullable=True)
    
    # Error levels
    error_min = Column(Numeric, nullable=True)
    error_max = Column(Numeric, nullable=True)
    
    # Expected values (flexible JSON storage)
    expected_values = Column(JSON, nullable=True)  # Can store arrays, objects, etc.
    
    # Relationships
    installation = relationship("Installation", back_populates="thresholds")
    endpoint = relationship("Endpoint", back_populates="thresholds")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('installation_id', 'endpoint_id', 'metric_type', name='_installation_endpoint_metric_uc'),
    )