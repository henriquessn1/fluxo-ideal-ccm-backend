from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Module(BaseModel):
    __tablename__ = "modules"
    
    # Basic information
    name = Column(String(255), nullable=False, unique=True, index=True)
    relative_path = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # api, database, cache, queue, storage, etc
    version = Column(String(50), nullable=True)
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    installations = relationship("Installation", back_populates="module", cascade="all, delete-orphan")
    endpoints = relationship("Endpoint", back_populates="module", cascade="all, delete-orphan")