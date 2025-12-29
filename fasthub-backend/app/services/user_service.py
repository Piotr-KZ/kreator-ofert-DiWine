"""
User management service
Business logic for user operations
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserUpdate
from app.services.user_repository import UserRepository


class UserService:
    """Service for user management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)

    async def get_users_by_organization(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get all users in organization"""
        result = await self.db.execute(
            select(User).where(User.organization_id == organization_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_user(self, user_id: int, user_update: UserUpdate, current_user: User) -> User:
        """Update user"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check permissions
        if current_user.id != user_id and current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user"
            )

        # Check organization membership
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organization"
            )

        # Update fields
        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        if user_update.email is not None:
            # Check if email already exists
            existing = await self.user_repo.get_by_email(user_update.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
                )
            user.email = user_update.email
            user.is_verified = False  # Require re-verification

        if user_update.role is not None:
            # Only admins can change roles
            if current_user.role != UserRole.admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can change user roles",
                )
            user.role = user_update.role

        if user_update.is_active is not None:
            # Only admins can activate/deactivate users
            if current_user.role != UserRole.admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can change user status",
                )
            user.is_active = user_update.is_active

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: int, current_user: User) -> None:
        """Delete user"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Only admins can delete users
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete users"
            )

        # Check organization membership
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organization"
            )

        # Cannot delete yourself
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
            )

        await self.user_repo.delete(user)

    async def get_organization_user_count(self, organization_id: int) -> int:
        """Get count of users in organization"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.organization_id == organization_id)
        )
        return result.scalar() or 0
