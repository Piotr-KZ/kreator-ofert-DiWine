"""
User schemas (DTOs)
Pydantic models for user data
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating user"""

    password: str
    organization_id: Optional[UUID] = None
    role: UserRole = UserRole.user


class UserUpdate(BaseModel):
    """Schema for updating user"""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (public data)"""

    id: UUID
    role: UserRole
    is_active: bool
    is_verified: bool
    organization_id: Optional[UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithOrganization(UserResponse):
    """Schema for user with organization data"""

    organization_name: Optional[str] = None
    organization_slug: Optional[str] = None
