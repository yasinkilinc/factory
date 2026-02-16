"""
Services for user module
"""

from typing import List, Optional
from uuid import UUID
from .repositories import user_repository

from .models import User, UserCreate, UserUpdate




class UserService:
    """Service for User"""
    
    def __init__(self):
        self.repository = user_repository
    
    def get_all(self) -> List[User]:
        """Get all User entities"""
        items = self.repository.find_all()
        return [User(**item) for item in items]
    
    def get_by_id(self, id: UUID) -> Optional[User]:
        """Get User by ID"""
        item = self.repository.find_by_id(id)
        return User(**item) if item else None
    
    def create(self, data: UserCreate) -> User:
        """Create new User"""
        item = self.repository.create(data.model_dump())
        return User(**item)
    
    def update(self, id: UUID, data: UserUpdate) -> Optional[User]:
        """Update User"""
        item = self.repository.update(id, data.model_dump(exclude_unset=True))
        return User(**item) if item else None
    
    def delete(self, id: UUID) -> bool:
        """Delete User"""
        return self.repository.delete(id)


user_service = UserService()

