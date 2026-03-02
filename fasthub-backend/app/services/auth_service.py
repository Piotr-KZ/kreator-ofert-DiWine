"""
Authentication service
Business logic for authentication operations
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_refresh_token,
    decode_verification_token,
    verify_password,
)
from app.models.member import Member, MemberRole
from app.models.user import User
from app.services.email_service import EmailService
from app.services.organization_repository import OrganizationRepository
from app.services.user_repository import UserRepository
from uuid import UUID


class AuthService:
    """Service for authentication operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.email_service = EmailService()
    
    async def _get_user_primary_org_id(self, user_id: UUID) -> Optional[UUID]:
        """Get user's primary organization ID (first membership)"""
        result = await self.db.execute(
            select(Member.organization_id)
            .where(Member.user_id == user_id)
            .order_by(Member.joined_at)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def register(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        organization_name: Optional[str] = None,
    ) -> Tuple[User, str, str]:
        """
        Register new user with organization

        Returns:
            Tuple of (user, access_token, refresh_token)

        Raises:
            HTTPException if email already exists
        """
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Create organization if provided
        organization_id = None
        if organization_name:
            # Create organization (user will be owner)
            # We'll set owner_id after creating user
            pass

        # Create user
        user = await self.user_repo.create(
            email=email,
            password=password,
            full_name=full_name,
            is_verified=True,  # Auto-verify for boilerplate (change to False in production)
        )

        # Create organization if needed
        if organization_name:
            organization = await self.org_repo.create(name=organization_name, owner_id=user.id)
            # Create member record (owner gets admin role in legacy system)
            member = Member(
                user_id=user.id,
                organization_id=organization.id,
                role=MemberRole.ADMIN
            )
            self.db.add(member)
            await self.db.flush()
            organization_id = organization.id

            # RBAC: create system roles for the new organization and assign Owner
            try:
                from fasthub_core.rbac.service import RBACService
                from fasthub_core.rbac.models import Role
                rbac = RBACService(self.db)
                await rbac.seed_organization_roles(organization.id)
                # Assign Owner role to the creator
                owner_role_result = await self.db.execute(
                    select(Role).where(
                        Role.organization_id == organization.id,
                        Role.name == "Owner",
                        Role.is_system == True,
                    )
                )
                owner_role = owner_role_result.scalar_one_or_none()
                if owner_role:
                    await rbac.assign_role(
                        user_id=user.id,
                        role_id=owner_role.id,
                        organization_id=organization.id,
                    )
            except Exception:
                pass  # RBAC seed failure should not block registration

        # Generate email verification token
        verification_token = create_email_verification_token(user.id)
        user.email_verification_token = verification_token
        await self.user_repo.update(user)

        # Send verification email
        await self.email_service.send_verification_email(
            to_email=user.email,
            verification_token=verification_token,
            frontend_url=settings.FRONTEND_URL,
        )

        # Get user's primary organization for JWT
        primary_org_id = await self._get_user_primary_org_id(user.id)
        
        # Generate tokens
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org": str(primary_org_id) if primary_org_id else None,
            }
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return user, access_token, refresh_token

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user (returns user only, no tokens)
        Used for testing and internal validation

        Returns:
            User if credentials valid, None otherwise
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    async def login(self, email: str, password: str) -> Tuple[User, str, str]:
        """
        Login user

        Returns:
            Tuple of (user, access_token, refresh_token)

        Raises:
            HTTPException if credentials invalid
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

        # Update last login
        await self.user_repo.update_last_login(user.id)

        # Get user's primary organization for JWT
        primary_org_id = await self._get_user_primary_org_id(user.id)
        
        # Generate tokens
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org": str(primary_org_id) if primary_org_id else None,
            }
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return user, access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh access token using refresh token

        Returns:
            New access token

        Raises:
            HTTPException if refresh token invalid
        """
        # Decode refresh token
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
            )

        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        from uuid import UUID

        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
            )

        # Get user's primary organization for JWT
        primary_org_id = await self._get_user_primary_org_id(user.id)
        
        # Generate new access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org": str(primary_org_id) if primary_org_id else None,
            }
        )

        return access_token

    async def verify_email(self, token: str) -> User:
        """
        Verify user email

        Returns:
            User with verified email

        Raises:
            HTTPException if token invalid
        """
        # Decode token
        user_id = decode_verification_token(token, "email_verification")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # Verify email
        user = await self.user_repo.set_email_verified(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

    async def request_password_reset(self, email: str) -> None:
        """
        Request password reset

        Sends password reset email if user exists
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Don't reveal if email exists
            return

        # Generate reset token
        reset_token = create_password_reset_token(user.id)
        await self.user_repo.set_password_reset_token(user.id, reset_token)

        # Send password reset email
        await self.email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            frontend_url=settings.FRONTEND_URL,
        )

    async def reset_password(self, token: str, new_password: str) -> User:
        """
        Reset password using reset token

        Returns:
            User with new password

        Raises:
            HTTPException if token invalid
        """
        # Decode token
        user_id = decode_verification_token(token, "password_reset")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token"
            )

        # Reset password
        user = await self.user_repo.reset_password(user_id, new_password)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> User:
        """
        Change user password (authenticated user)

        Returns:
            User with new password

        Raises:
            HTTPException if current password incorrect
        """
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
            )

        # Update password
        user = await self.user_repo.reset_password(user_id, new_password)
        return user

    async def generate_magic_link(self, email: str) -> str:
        """
        Generate magic link token for passwordless login (alias for send_magic_link)
        Firebase equivalent: SendLinkToLoginUseCase

        Returns:
            Magic link token (for testing/development)
        """
        # Find user
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if email exists - return empty token
            # This prevents email enumeration attacks
            return ""

        # Generate magic link token
        magic_token = secrets.token_urlsafe(32)
        magic_expires = datetime.utcnow() + timedelta(minutes=15)  # 15 min expiry

        # Save token to user
        user.magic_link_token = magic_token
        user.magic_link_expires = magic_expires
        await self.db.commit()

        # Send email with magic link
        await self.email_service.send_magic_link_email(
            to_email=user.email,
            magic_token=magic_token,
            frontend_url=settings.FRONTEND_URL,
        )

        return magic_token

    async def verify_magic_link(self, token: str) -> Optional[User]:
        """
        Verify magic link token and return user

        Returns:
            User if token valid, None otherwise
        """
        # Find user by magic link token
        result = await self.db.execute(select(User).where(User.magic_link_token == token))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Check if token expired
        if not user.magic_link_expires or user.magic_link_expires < datetime.utcnow():
            return None

        # Clear magic link token (one-time use)
        user.magic_link_token = None
        user.magic_link_expires = None

        # Mark email as verified
        user.is_verified = True

        await self.db.commit()

        return user
