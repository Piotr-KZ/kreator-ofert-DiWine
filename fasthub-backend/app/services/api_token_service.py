"""
API Token service
Business logic for API token operations
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_token import APIToken
from app.models.user import User


class APITokenService:
    """Service for API token management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_token(self) -> str:
        """
        Generate a secure random API token
        Returns 64-character hex string
        """
        return secrets.token_hex(32)

    def hash_token(self, token: str) -> str:
        """
        Hash token for secure storage
        Uses SHA-256
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_token(
        self, user_id: int, name: str, expires_in_days: Optional[int] = None
    ) -> tuple[APIToken, str]:
        """
        Create new API token for user
        Firebase equivalent: CreateApiTokenUseCase

        Returns:
            Tuple of (APIToken model, plaintext token)
            ⚠️ Token is only returned once - must be saved by user!
        """
        # Generate token
        plaintext_token = self.generate_token()
        token_hash = self.hash_token(plaintext_token)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create token record
        api_token = APIToken(
            user_id=user_id, token_hash=token_hash, name=name, expires_at=expires_at
        )

        self.db.add(api_token)
        await self.db.commit()
        await self.db.refresh(api_token)

        return api_token, plaintext_token

    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verify API token and return associated user
        Returns None if token invalid or expired
        """
        token_hash = self.hash_token(token)

        # Find token
        result = await self.db.execute(select(APIToken).where(APIToken.token_hash == token_hash))
        api_token = result.scalar_one_or_none()

        if not api_token:
            return None

        # Check if expired
        if api_token.is_expired:
            return None

        # Update last used timestamp
        api_token.last_used_at = datetime.utcnow()
        await self.db.commit()

        # Get user
        user_result = await self.db.execute(select(User).where(User.id == api_token.user_id))
        user = user_result.scalar_one_or_none()

        return user

    async def list_tokens(self, user_id: int) -> List[APIToken]:
        """
        List all API tokens for user
        """
        result = await self.db.execute(
            select(APIToken).where(APIToken.user_id == user_id).order_by(APIToken.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_token(self, token_id: int, user_id: int) -> bool:
        """
        Delete API token
        Firebase equivalent: DeleteApiTokenUseCase

        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(APIToken).where(APIToken.id == token_id, APIToken.user_id == user_id)
        )
        api_token = result.scalar_one_or_none()

        if not api_token:
            return False

        await self.db.delete(api_token)
        await self.db.commit()

        return True

    async def delete_expired_tokens(self) -> int:
        """
        Delete all expired tokens
        Returns count of deleted tokens
        """
        result = await self.db.execute(
            select(APIToken).where(APIToken.expires_at < datetime.utcnow())
        )
        expired_tokens = list(result.scalars().all())

        for token in expired_tokens:
            await self.db.delete(token)

        await self.db.commit()

        return len(expired_tokens)
