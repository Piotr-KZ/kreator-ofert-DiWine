"""
Authentication schemas (DTOs)
Pydantic models for auth requests and responses
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    model_config = {"strict": True}
    """Schema for user registration"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    organization_name: Optional[str] = Field(None, max_length=255)

    # Extended company fields (Brief 25 — GUS)
    account_type: Optional[str] = Field(None, pattern="^(business|individual)$")
    nip: Optional[str] = Field(None, max_length=50)
    regon: Optional[str] = Field(None, max_length=20)
    krs: Optional[str] = Field(None, max_length=20)
    legal_form: Optional[str] = Field(None, max_length=100)
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")

        return v


class UserLogin(BaseModel):
    model_config = {"strict": True}
    """Schema for user login"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    model_config = {"strict": True}
    """Schema for token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    model_config = {"strict": True}
    """Schema for token refresh request"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    model_config = {"strict": True}
    """Schema for password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    model_config = {"strict": True}
    """Schema for password reset confirmation"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")

        return v


class EmailVerificationRequest(BaseModel):
    model_config = {"strict": True}
    """Schema for email verification"""

    token: str


class ChangePassword(BaseModel):
    model_config = {"strict": True}
    """Schema for changing password (authenticated user)"""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")

        return v


class MagicLinkRequest(BaseModel):
    model_config = {"strict": True}
    """Schema for magic link request"""

    email: EmailStr
