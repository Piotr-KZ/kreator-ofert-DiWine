"""
Authentication package
JWT tokens, password hashing, blacklist, email verification, and FastAPI dependencies
"""

from fasthub_core.auth.service import (
    verify_password,
    get_password_hash,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_verification_token,
)
from fasthub_core.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_current_organization,
    require_organization_owner,
)
from fasthub_core.auth.blacklist import blacklist_token, is_token_blacklisted
from fasthub_core.auth.password_validation import validate_password, PasswordValidator
from fasthub_core.auth.email_verification import EmailVerificationService
from fasthub_core.auth.routes import router as auth_router

__all__ = [
    "verify_password",
    "get_password_hash",
    "validate_password_strength",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    "create_email_verification_token",
    "create_password_reset_token",
    "decode_verification_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_current_organization",
    "require_organization_owner",
    "blacklist_token",
    "is_token_blacklisted",
    "validate_password",
    "PasswordValidator",
    "EmailVerificationService",
    "auth_router",
]
