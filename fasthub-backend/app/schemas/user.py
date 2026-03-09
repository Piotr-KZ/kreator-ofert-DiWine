"""
User schemas (DTOs)
Pydantic models for user data
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

# UserRole removed - roles are now in Member model


class UserBase(BaseModel):
    model_config = {"strict": True}
    """Base user schema"""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating user"""

    password: str


class UserUpdate(BaseModel):
    model_config = {"strict": True}
    """Schema for updating user"""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Remove leading/trailing whitespace
            v = v.strip()
            # Check for dangerous characters
            dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/']
            if any(char in v for char in dangerous_chars):
                raise ValueError('Full name contains invalid characters')
            # Check minimum length
            if len(v) < 2:
                raise ValueError('Full name must be at least 2 characters long')
        return v


class UserResponse(UserBase):
    """Schema for user response (public data)"""

    id: UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    is_superadmin: bool = False
    is_email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    google_id: Optional[str] = None
    github_id: Optional[str] = None
    microsoft_id: Optional[str] = None
    oauth_provider: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserWithMemberships(UserResponse):
    """Schema for user with their organization memberships"""

    memberships: list = []  # Will be populated with MemberResponse
