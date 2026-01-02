"""
User schemas (DTOs)
Pydantic models for user data
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

# UserRole removed - roles are now in Member model


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating user"""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating user"""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (public data)"""

    id: UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithMemberships(UserResponse):
    """Schema for user with their organization memberships"""

    memberships: list = []  # Will be populated with MemberResponse
