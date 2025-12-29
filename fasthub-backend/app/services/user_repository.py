"""
User repository
Database operations for users
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User, UserRole


class UserRepository:
    """Repository for user database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_email_and_organization(
        self, email: str, organization_id: int
    ) -> Optional[User]:
        """Get user by email within specific organization"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.organization_id == organization_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        organization_id: Optional[int] = None,
        role: UserRole = UserRole.user,
        is_verified: bool = False,
    ) -> User:
        """Create new user"""
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            organization_id=organization_id,
            role=role,
            is_verified=is_verified,
            is_active=True,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update user"""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete user"""
        await self.db.delete(user)
        await self.db.flush()

    async def set_email_verified(self, user_id: int) -> Optional[User]:
        """Mark user email as verified"""
        user = await self.get_by_id(user_id)
        if user:
            user.is_verified = True
            user.email_verification_token = None
            return await self.update(user)
        return None

    async def set_password_reset_token(self, user_id: int, token: str) -> Optional[User]:
        """Set password reset token for user"""
        user = await self.get_by_id(user_id)
        if user:
            user.password_reset_token = token
            return await self.update(user)
        return None

    async def reset_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Reset user password"""
        user = await self.get_by_id(user_id)
        if user:
            user.hashed_password = get_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            return await self.update(user)
        return None

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        from datetime import datetime

        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            await self.update(user)
