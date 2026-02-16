"""
Models for user module
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date



class UserBase(BaseModel):
    """Base schema for User"""
    email: str
    name: str
    age: Optional[int]
    created_at: datetime


class UserCreate(UserBase):
    """Schema for creating User"""
    pass


class UserUpdate(UserBase):
    """Schema for updating User"""
    pass


class User(UserBase):
    """Schema for User with ID"""
    id: UUID
    
    class Config:
        from_attributes = True