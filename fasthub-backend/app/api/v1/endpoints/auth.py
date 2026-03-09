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
        account_type=user_data.account_type,
        nip=user_data.nip,
        regon=user_data.regon,
        krs=user_data.krs,
        legal_form=user_data.legal_form,
        street=user_data.street,
        city=user_data.city,
        postal_code=user_data.postal_code,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login")
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
    If 2FA enabled, returns temp_token instead of full tokens.
    """
    auth_service = AuthService(db)

    user, access_token, refresh_token = await auth_service.login(
        email=credentials.email, password=credentials.password
    )

    # If 2FA is enabled, return temp token instead
    if getattr(user, "totp_enabled", False):
        from app.core.security import create_2fa_temp_token
        temp_token = create_2fa_temp_token(user.id)
        return {"requires_2fa": True, "temp_token": temp_token}

    # Create session record
    try:
        from fasthub_core.auth.device_parser import parse_device
        from fasthub_core.auth.session_models import UserSession
        from app.core.security import decode_refresh_token as _decode_rt
        from datetime import datetime, timedelta

        device = parse_device(request.headers.get("User-Agent", ""))
        rt_payload = _decode_rt(refresh_token)
        jti = rt_payload.get("jti", "") if rt_payload else ""

        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            device_type=device["device_type"],
            device_name=device["device_name"],
            browser=device["browser"],
            os=device["os"],
            ip_address=request.client.host if request.client else None,
            is_active=True,
            last_active_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session)
        await db.commit()
    except Exception:
        pass  # Session tracking failure should not block login

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
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    """
    Logout user

    Invalidates the current access token by adding it to blacklist.
    Client should also delete stored tokens.
    """
    import logging
    from datetime import datetime, timezone

    from app.core.security import decode_access_token
    from fasthub_core.auth.blacklist import blacklist_token

    logger = logging.getLogger(__name__)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Successfully logged out"}

        token = auth_header.replace("Bearer ", "")

        payload = decode_access_token(token)
        if not payload or not payload.get("exp"):
            return {"message": "Successfully logged out"}

        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
        now = datetime.utcnow()
        expires_in = max(int((expires_at - now).total_seconds()), 0)

        if expires_in > 0:
            await blacklist_token(token, expires_in)
            logger.info(f"User {current_user.email} logged out successfully")
        else:
            logger.warning(f"User {current_user.email} logged out but token already expired")

    except Exception as e:
        logger.error(f"Logout error: {type(e).__name__}: {str(e)}", exc_info=True)

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
    response_data = {
        "message": "If this email exists, a magic link has been sent"
    }
    
    # Only include dev_token in non-production environments
    if settings.ENVIRONMENT != "production":
        response_data["dev_token"] = token
    
    return response_data


@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify magic link and log user in

    Returns JWT access and refresh tokens.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.verify_magic_link(token)

    return TokenResponse(**tokens, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
