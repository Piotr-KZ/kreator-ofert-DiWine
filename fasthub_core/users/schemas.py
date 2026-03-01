"""
User, Organization, Member, and Auth schemas (DTOs)
Pydantic models for request/response data
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from fasthub_core.users.models import MemberRole


# ============================================================================
# User Schemas
# ============================================================================

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
            v = v.strip()
            dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/']
            if any(char in v for char in dangerous_chars):
                raise ValueError('Full name contains invalid characters')
            if len(v) < 2:
                raise ValueError('Full name must be at least 2 characters long')
        return v


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

    memberships: list = []


# ============================================================================
# Organization Schemas
# ============================================================================

class OrganizationBase(BaseModel):
    model_config = {"strict": True}
    """Base organization schema"""

    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)


class OrganizationCreate(OrganizationBase):
    """Schema for creating organization"""

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Organization name contains invalid characters')
        if len(v) < 2:
            raise ValueError('Organization name must be at least 2 characters long')
        return v


class OrganizationUpdate(BaseModel):
    model_config = {"strict": True}
    """Schema for updating organization"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    nip: Optional[str] = Field(None, max_length=50)
    billing_street: Optional[str] = Field(None, max_length=255)
    billing_city: Optional[str] = Field(None, max_length=100)
    billing_postal_code: Optional[str] = Field(None, max_length=20)
    billing_country: Optional[str] = Field(None, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/']
            if any(char in v for char in dangerous_chars):
                raise ValueError('Organization name contains invalid characters')
            if len(v) < 2:
                raise ValueError('Organization name must be at least 2 characters long')
        return v

    @field_validator("nip")
    @classmethod
    def validate_nip(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        nip_clean = v.replace(" ", "").replace("-", "")
        if not re.match(r"^\d{10}$", nip_clean):
            raise ValueError("NIP must contain exactly 10 digits")
        return nip_clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        phone_clean = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not re.match(r"^(\+?\d{9,15})$", phone_clean):
            raise ValueError("Phone number must contain 9-15 digits (optionally starting with +)")
        return phone_clean

    @field_validator("billing_postal_code")
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        postal_clean = v.replace(" ", "")
        if not re.match(r"^\d{2}-?\d{3}$", postal_clean):
            raise ValueError("Postal code must be in format XX-XXX or XXXXX (5 digits)")
        if len(postal_clean) == 5:
            postal_clean = f"{postal_clean[:2]}-{postal_clean[2:]}"
        return postal_clean


class OrganizationComplete(BaseModel):
    model_config = {"strict": True}
    """Schema for completing organization onboarding"""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(business|individual)$")
    nip: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    billing_street: str = Field(..., min_length=1, max_length=255)
    billing_city: str = Field(..., min_length=1, max_length=100)
    billing_postal_code: str = Field(..., min_length=1, max_length=20)
    billing_country: str = Field(..., min_length=1, max_length=100)

    @field_validator("nip")
    @classmethod
    def validate_nip(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        nip_clean = v.replace(" ", "").replace("-", "")
        if not re.match(r"^\d{10}$", nip_clean):
            raise ValueError("NIP must contain exactly 10 digits")
        return nip_clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        phone_clean = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not re.match(r"^(\+?\d{9,15})$", phone_clean):
            raise ValueError("Phone number must contain 9-15 digits (optionally starting with +)")
        return phone_clean

    @field_validator("billing_postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        postal_clean = v.replace(" ", "")
        if not re.match(r"^\d{2}-?\d{3}$", postal_clean):
            raise ValueError("Postal code must be in format XX-XXX or XXXXX (5 digits)")
        if len(postal_clean) == 5:
            postal_clean = f"{postal_clean[:2]}-{postal_clean[2:]}"
        return postal_clean


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""

    id: UUID
    owner_id: UUID
    stripe_customer_id: Optional[str]
    type: Optional[str]
    email: Optional[str]
    nip: Optional[str]
    phone: Optional[str]
    billing_street: Optional[str]
    billing_city: Optional[str]
    billing_postal_code: Optional[str]
    billing_country: Optional[str]
    is_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationWithStats(OrganizationResponse):
    """Schema for organization with statistics"""

    user_count: int = 0
    subscription_status: Optional[str] = None


# ============================================================================
# Member Schemas
# ============================================================================

class MemberBase(BaseModel):
    model_config = {"strict": True}
    """Base member schema with common fields"""

    role: MemberRole = Field(..., description="Member role in organization")


class MemberCreate(BaseModel):
    model_config = {"strict": True}
    """Schema for inviting a new member to organization"""

    email: EmailStr = Field(..., description="Email of user to invite")
    role: MemberRole = Field(default=MemberRole.ADMIN, description="Role to assign to member")


class MemberUpdate(BaseModel):
    model_config = {"strict": True}
    """Schema for updating member (only role can be changed)"""

    role: MemberRole = Field(..., description="New role for member")


class UserBasicInfo(BaseModel):
    model_config = {"strict": True, "from_attributes": True}
    """Basic user info for member response"""

    id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool


class MemberResponse(MemberBase):
    model_config = {"from_attributes": True}
    """Full member response with user details"""

    id: UUID
    user_id: UUID
    organization_id: UUID
    role: MemberRole
    joined_at: datetime

    user: UserBasicInfo


class MemberListResponse(BaseModel):
    model_config = {"strict": True, "from_attributes": True}
    """Response for listing members"""

    members: list[MemberResponse]
    total: int


# ============================================================================
# Auth Schemas
# ============================================================================

class UserRegister(BaseModel):
    model_config = {"strict": True}
    """Schema for user registration"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    organization_name: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
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
