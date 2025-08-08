from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Service(Base, TimestampMixin):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), default="GET", nullable=False)
    headers = Column(JSON, nullable=True)
    expected_status = Column(Integer, default=200, nullable=False)
    timeout = Column(Integer, default=30, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="services")
    health_checks = relationship("HealthCheck", back_populates="service", cascade="all, delete-orphan")