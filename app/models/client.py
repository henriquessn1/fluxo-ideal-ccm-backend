from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel, SoftDeleteMixin


class Client(BaseModel, SoftDeleteMixin):
    __tablename__ = "clients"
    
    # Basic information
    name = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    timezone = Column(String(50), default="America/Sao_Paulo", nullable=False)
    
    # Relationships
    instances = relationship("Instance", back_populates="client", cascade="all, delete-orphan")