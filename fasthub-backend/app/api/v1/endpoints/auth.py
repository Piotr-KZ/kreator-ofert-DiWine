"""
Authentication endpoints
API routes for auth operations
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_active_user, get_current_user
from app.core.rate_limit import RateLimits, limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePassword,
    EmailVerificationRequest,
    MagicLinkRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(
    request: Request,
    response: Response,
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register new user

    Creates new user account and organization (if provided).
    Returns access and refresh tokens.
    Email verification required before full access.
    """
    auth_service = AuthService(db)

    user, access_token, refresh_token = await auth_service.register(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        organization_name=user_data.organization_name,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Login user

    Authenticates user with email and password.
    Returns access and refresh tokens.
    """
    auth_service = AuthService(db)

    user, access_token, refresh_token = await auth_service.login(
        email=credentials.email, password=credentials.password
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token

    Uses refresh token to generate new access token.
    """
    auth_service = AuthService(db)

    access_token = await auth_service.refresh_access_token(token_data.refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information

    Returns authenticated user's profile data.
    """
    return current_user


@router.post("/verify-email", response_model=dict)
async def verify_email(
    verification_data: EmailVerificationRequest, db: AsyncSession = Depends(get_db)
):
    """
    Verify user email

    Verifies user email using verification token sent to email.
    """
    auth_service = AuthService(db)

    await auth_service.verify_email(verification_data.token)

    return {"message": "Email verified successfully"}


@router.post("/password-reset/request", response_model=dict)
@limiter.limit(RateLimits.AUTH_PASSWORD_RESET)
async def request_password_reset(
    request: Request,
    response: Response,
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset

    Sends password reset email to user if email exists.
    Always returns success to prevent email enumeration.
    """
    auth_service = AuthService(db)

    await auth_service.request_password_reset(reset_request.email)

    return {"message": "If email exists, password reset instructions have been sent"}


@router.post("/password-reset/confirm", response_model=dict)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    Confirm password reset

    Resets password using reset token from email.
    """
    auth_service = AuthService(db)

    await auth_service.reset_password(token=reset_data.token, new_password=reset_data.new_password)

    return {"message": "Password reset successfully"}


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password (authenticated user)

    Changes password for authenticated user.
    Requires current password for verification.
    """
    auth_service = AuthService(db)

    await auth_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    return {"message": "Password changed successfully"}


@router.post("/logout", response_model=dict)
def logout(request: Request, current_user: User = Depends(get_current_user)):
    """
    Logout user (SYNC version)

    Invalidates the current access token by adding it to blacklist.
    Client should also delete stored tokens.
    """
    import logging
    from datetime import datetime, timezone

    from app.core.security import decode_access_token
    from app.core.token_blacklist import TokenBlacklist

    logger = logging.getLogger(__name__)

    try:
        # Get token from request
        auth_header = request.headers.get("Authorization")
        logger.info(f"Logout: auth_header present: {bool(auth_header)}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Logout: No valid auth header, returning success anyway")
            return {"message": "Successfully logged out"}
        
        token = auth_header.replace("Bearer ", "")
        logger.info(f"Logout: token extracted, length: {len(token)}")

        # Decode token to get expiration
        payload = decode_access_token(token)
        logger.info(f"Logout: payload decoded: {bool(payload)}, exp: {payload.get('exp') if payload else None}")
        
        if not payload or not payload.get("exp"):
            logger.warning("Logout: Invalid token payload, returning success anyway")
            return {"message": "Successfully logged out"}
        
        # Convert UTC timestamp to naive UTC datetime (not local time!)
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
        logger.info(f"Logout: calling add_token with expires_at={expires_at}")
        
        # Add token to blacklist (SYNC - no await!)
        result = TokenBlacklist.add_token(token, expires_at)
        logger.info(f"Logout: add_token result: {result}")
        
        if result:
            logger.info(f"✅ User {current_user.email} logged out successfully")
        else:
            logger.warning(f"⚠️ User {current_user.email} logged out but token not blacklisted (Redis issue)")
            
    except Exception as e:
        logger.error(f"Logout error: {type(e).__name__}: {str(e)}", exc_info=True)
        # Don't fail logout even if blacklist fails

    return {"message": "Successfully logged out"}


@router.post("/magic-link/send", response_model=dict)
@limiter.limit(RateLimits.AUTH_MAGIC_LINK)
async def send_magic_link(
    request: Request,
    response: Response,
    magic_link_request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send magic link for passwordless login

    Firebase equivalent: SendLinkToLoginUseCase

    Sends email with magic link that expires in 15 minutes.
    """
    auth_service = AuthService(db)
    token = await auth_service.generate_magic_link(magic_link_request.email)

    # In development, return token for testing
    # In production, only return success message
    return {
        "message": "If this email exists, a magic link has been sent",
        "dev_token": token,  # Remove in production!
    }


@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify magic link and log user in

    Returns JWT access and refresh tokens.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.verify_magic_link(token)

    return TokenResponse(**tokens, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
