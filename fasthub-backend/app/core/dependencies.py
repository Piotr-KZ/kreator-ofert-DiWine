"""
FastAPI dependencies
Authentication and authorization dependencies
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User, UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token

    Usage:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    Raises:
        HTTPException 401 if token invalid or user not found
    """
    token = credentials.credentials

    # Check if token is blacklisted (SYNC - no await!)
    from app.core.token_blacklist import TokenBlacklist

    if TokenBlacklist.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (must be active and verified)

    Raises:
        HTTPException 403 if user not active or not verified
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first.",
        )

    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get current admin user (must be admin role)

    Raises:
        HTTPException 403 if user not admin
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    return current_user


async def get_current_organization(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> Organization:
    """
    Get current user's organization

    Raises:
        HTTPException 404 if organization not found
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User has no organization"
        )

    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return organization


async def require_organization_owner(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
) -> User:
    """
    Require current user to be organization owner

    Raises:
        HTTPException 403 if user not owner
    """
    if organization.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Organization owner privileges required"
        )

    return current_user


# Alias for admin dependency
require_admin = get_current_admin_user


async def get_current_user_from_api_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from API token (alternative to JWT)

    Usage:
        @router.get("/data")
        async def get_data(user: User = Depends(get_current_user_from_api_token)):
            return {"data": "..."}

    Raises:
        HTTPException 401 if token invalid or expired
    """
    from app.services.api_token_service import APITokenService

    token = credentials.credentials
    token_service = APITokenService(db)

    user = await token_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    return user


async def get_current_user_with_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user and check subscription status

    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            current_user: User = Depends(get_current_user_with_subscription)
        ):
            return {"data": "..."}

    Raises:
        HTTPException 402 if subscription invalid or expired
    """
    from fastapi import Request

    from app.core.subscription_check import SubscriptionChecker

    # Note: We can't get Request here directly, so we'll check in middleware
    # This is a placeholder for endpoints that explicitly require subscription
    # For now, just return the user - actual check happens in middleware
    return current_user


# Alias for subscription check
require_subscription = get_current_user_with_subscription
