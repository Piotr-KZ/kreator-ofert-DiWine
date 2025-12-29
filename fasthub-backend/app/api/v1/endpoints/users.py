"""
Users management endpoints
API routes for user operations
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile

    Returns authenticated user's profile data.
    """
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users in organization

    Returns list of users in the current user's organization.
    Requires admin authentication.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization"
        )

    user_service = UserService(db)
    users = await user_service.get_users_by_organization(
        current_user.organization_id, skip=skip, limit=limit
    )
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID

    Returns user details if user is in the same organization.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if user is in same organization
    if user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organization"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user

    Users can update their own profile.
    Admins can update any user in their organization.
    Only admins can change roles and status.
    """
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_update, current_user)
    await db.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user

    Only admins can delete users.
    Cannot delete yourself.
    """
    user_service = UserService(db)
    await user_service.delete_user(user_id, current_user)
    await db.commit()
    return None
