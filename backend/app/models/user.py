"""
User models for authentication.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class AdminUser(Base):
    """Admin user model for simple JWT auth."""
    
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}')>"


class AppUser(Base):
    """Staff and student user model."""
    
    __tablename__ = "app_users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # staff | student
    department = Column(String(120), nullable=True)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AppUser(id={self.id}, email='{self.email}', role='{self.role}')>"
