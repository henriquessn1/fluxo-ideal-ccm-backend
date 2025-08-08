from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Client(Base, TimestampMixin):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    dns = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    services = relationship("Service", back_populates="client", cascade="all, delete-orphan")
    health_checks = relationship("HealthCheck", back_populates="client", cascade="all, delete-orphan")