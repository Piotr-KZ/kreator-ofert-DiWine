"""
Security utilities
Password hashing and JWT token management
"""

import uuid as uuid_module
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from fasthub_core.config import get_settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> bool:
    """
    Validate password meets requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains number

    Returns:
        True if valid, raises ValueError if not
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one number")

    return True


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token (short-lived)
    """
    settings = get_settings()
    to_encode = data.copy()
    # Convert UUID to string for JSON serialization
    if "sub" in to_encode and hasattr(to_encode["sub"], "__str__"):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # JTI — unique token identifier (dla blacklisty)
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid_module.uuid4())

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token (long-lived)
    """
    settings = get_settings()
    to_encode = data.copy()
    # Convert UUID to string for JSON serialization
    if "sub" in to_encode and hasattr(to_encode["sub"], "__str__"):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT access token

    Returns:
        Decoded token payload or None if invalid
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Verify token type
        if payload.get("type") != "access":
            return None

        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT refresh token

    Returns:
        Decoded token payload or None if invalid
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Verify token type
        if payload.get("type") != "refresh":
            return None

        return payload
    except JWTError:
        return None


def create_email_verification_token(user_id: int) -> str:
    """Create token for email verification"""
    settings = get_settings()
    data = {"sub": str(user_id), "type": "email_verification"}
    expire = datetime.utcnow() + timedelta(hours=24)
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_password_reset_token(user_id: int) -> str:
    """Create token for password reset"""
    settings = get_settings()
    data = {"sub": str(user_id), "type": "password_reset"}
    expire = datetime.utcnow() + timedelta(hours=1)
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_verification_token(token: str, token_type: str) -> Optional[int]:
    """
    Decode email verification or password reset token

    Args:
        token: JWT token
        token_type: "email_verification" or "password_reset"

    Returns:
        User ID if valid, None otherwise
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != token_type:
            return None

        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except (JWTError, ValueError):
        return None
