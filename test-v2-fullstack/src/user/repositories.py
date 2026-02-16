"""
Repositories for user module
"""

from typing import List, Optional
from uuid import UUID

# This is a simple in-memory implementation
# Replace with actual database logic (SQLAlchemy, etc.)



class UserRepository:
    """Repository for User"""
    
    def __init__(self):
        self._storage: dict[UUID, dict] = {}
    
    def find_all(self) -> List[dict]:
        """Find all User entities"""
        return list(self._storage.values())
    
    def find_by_id(self, id: UUID) -> Optional[dict]:
        """Find User by ID"""
        return self._storage.get(id)
    
    def create(self, data: dict) -> dict:
        """Create new User"""
        from uuid import uuid4
        id = uuid4()
        entity = {"id": id, **data}
        self._storage[id] = entity
        return entity
    
    def update(self, id: UUID, data: dict) -> Optional[dict]:
        """Update User"""
        if id not in self._storage:
            return None
        self._storage[id].update(data)
        return self._storage[id]
    
    def delete(self, id: UUID) -> bool:
        """Delete User"""
        if id in self._storage:
            del self._storage[id]
            return True
        return False


user_repository = UserRepository()

