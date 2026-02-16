"""
Routes for user module
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from .models import User, UserCreate, UserUpdate

from .services import user_service


router = APIRouter()



@router.get("/user", response_model=List[User])
async def get_all_user():
    """Get all User entities"""
    return user_service.get_all()


@router.get("/user/{id}", response_model=User)
async def get_user(id: UUID):
    """Get User by ID"""
    item = user_service.get_by_id(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return item


@router.post("/user", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    """Create new User"""
    return user_service.create(data)


@router.put("/user/{id}", response_model=User)
async def update_user(id: UUID, data: UserUpdate):
    """Update User"""
    item = user_service.update(id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return item


@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: UUID):
    """Delete User"""
    if not user_service.delete(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

