"""
User management service
Business logic for user operations
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.user_repository import UserRepository
from uuid import UUID


class UserService:
    """Service for user management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def _check_same_org(self, user1: User, user2: User) -> bool:
        """Check if two users share at least one organization"""
        result = await self.db.execute(
            select(Member.organization_id)
            .where(Member.user_id == user1.id)
        )
        user1_orgs = set(result.scalars().all())
        
        result = await self.db.execute(
            select(Member.organization_id)
            .where(Member.user_id == user2.id)
        )
        user2_orgs = set(result.scalars().all())
        
        return bool(user1_orgs & user2_orgs)  # Check intersection

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)

    async def get_users_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get all users in organization"""
        # Get user IDs from members table
        result = await self.db.execute(
            select(User)
            .join(Member, User.id == Member.user_id)
            .where(Member.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_user(self, user_id: int, user_update: UserUpdate, current_user: User) -> User:
        """Update user"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check permissions
        if current_user.id != user_id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user"
            )

        # Check organization membership (must share at least one org)
        if current_user.id != user_id:
            same_org = await self._check_same_org(user, current_user)
            if not same_org:
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

        if user_update.phone is not None:
            user.phone = user_update.phone
        if user_update.position is not None:
            user.position = user_update.position
        if user_update.language is not None:
            user.language = user_update.language
        if user_update.timezone is not None:
            user.timezone = user_update.timezone

        if user_update.is_active is not None:
            # Only admins can activate/deactivate users
            if not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only superusers can change user status",
                )
            user.is_active = user_update.is_active

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: UUID, current_user: User) -> None:
        """Delete user"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # SuperAdmin can delete anyone (system-wide access)
        if current_user.is_superuser:
            # SuperAdmin has full access - skip organization check
            pass
        else:
            # Regular users can only delete within their organization
            same_org = await self._check_same_org(user, current_user)
            if not same_org:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organization"
                )

        # Cannot delete yourself
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
            )

        await self.user_repo.delete(user)

    async def get_organization_user_count(self, organization_id: UUID) -> int:
        """Get count of users in organization"""
        result = await self.db.execute(
            select(func.count(Member.user_id)).where(Member.organization_id == organization_id)
        )
        return result.scalar() or 0
