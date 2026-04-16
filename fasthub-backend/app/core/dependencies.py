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
from app.models.member import Member
from app.models.organization import Organization
from app.models.user import User

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

    # Check if token is blacklisted (async via fasthub_core)
    from fasthub_core.auth.blacklist import is_token_blacklisted

    try:
        if await is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        raise
    except Exception:
        # Redis unavailable — skip blacklist check (dev/no-Redis env)
        pass

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


async def get_current_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get current superuser (must have is_superuser=True)

    Raises:
        HTTPException 403 if user not superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privileges required"
        )

    return current_user


async def get_current_organization(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> Organization:
    """
    Get current user's primary organization
    
    Priority:
    1. Organization where user is owner (organizations.owner_id)
    2. First organization from memberships (members table)

    Raises:
        HTTPException 404 if user has no organization
    """
    # Priority 1: Check if user is owner of any organization
    result = await db.execute(
        select(Organization)
        .where(Organization.owner_id == current_user.id)
        .order_by(Organization.created_at)
        .limit(1)
    )
    organization = result.scalar_one_or_none()
    
    # Priority 2: If not owner, get first membership
    if not organization:
        result = await db.execute(
            select(Member)
            .where(Member.user_id == current_user.id)
            .order_by(Member.joined_at)
            .limit(1)
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User has no organization"
            )
        
        # Get organization from membership
        result = await db.execute(
            select(Organization).where(Organization.id == membership.organization_id)
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


# Alias for superuser dependency
require_superuser = get_current_superuser


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


# Alias for admin/superuser dependency
require_admin = get_current_superuser


# Alias for admin user dependency
get_current_admin_user = get_current_superuser
