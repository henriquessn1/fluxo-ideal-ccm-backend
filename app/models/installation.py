from sqlalchemy import Column, Boolean, ForeignKey, JSON, UniqueConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, SoftDeleteMixin


class Installation(BaseModel, SoftDeleteMixin):
    __tablename__ = "installations"
    
    # Foreign keys
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Authentication
    api_key = Column(String(255), nullable=False, index=True)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Configuration specific to this installation
    
    # Relationships
    module = relationship("Module", back_populates="installations")
    instance = relationship("Instance", back_populates="installations")
    thresholds = relationship("Threshold", back_populates="installation", cascade="all, delete-orphan")
    monitoring_logs = relationship("MonitoringLog", back_populates="installation", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('module_id', 'instance_id', name='_module_instance_uc'),
    )