from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, SoftDeleteMixin


class Instance(BaseModel, SoftDeleteMixin):
    __tablename__ = "instances"
    
    # Foreign keys
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    environment = Column(String(50), nullable=True)  # production, staging, development
    version = Column(String(50), nullable=True)
    
    # Authentication
    admin_api_key = Column(String(255), nullable=True, unique=True, index=True)
    
    # Relationships
    client = relationship("Client", back_populates="instances")
    installations = relationship("Installation", back_populates="instance", cascade="all, delete-orphan")