"""
Organization schemas (DTOs)
Pydantic models for organization data
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
        # Remove leading/trailing whitespace
        v = v.strip()
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Organization name contains invalid characters')
        # Check minimum length
        if len(v) < 2:
            raise ValueError('Organization name must be at least 2 characters long')
        return v


class OrganizationUpdate(BaseModel):
    model_config = {"strict": True}
    """Schema for updating organization"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Remove leading/trailing whitespace
            v = v.strip()
            # Check for dangerous characters
            dangerous_chars = ['<', '>', '&', '"', "'", '\\', '/']
            if any(char in v for char in dangerous_chars):
                raise ValueError('Organization name contains invalid characters')
            # Check minimum length
            if len(v) < 2:
                raise ValueError('Organization name must be at least 2 characters long')
        return v


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
        """Validate NIP (Polish Tax ID) - must be 10 digits"""
        if v is None:
            return v
        
        # Remove spaces and dashes
        nip_clean = v.replace(" ", "").replace("-", "")
        
        # Check if exactly 10 digits
        if not re.match(r"^\d{10}$", nip_clean):
            raise ValueError("NIP must contain exactly 10 digits")
        
        return nip_clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number - must be valid format"""
        if v is None:
            return v
        
        # Remove spaces, dashes, parentheses
        phone_clean = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Check if starts with + and has 9-15 digits (international format)
        # OR has 9-15 digits (local format)
        if not re.match(r"^(\+?\d{9,15})$", phone_clean):
            raise ValueError("Phone number must contain 9-15 digits (optionally starting with +)")
        
        return phone_clean

    @field_validator("billing_postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        """Validate postal code - Polish format XX-XXX or XXXXX"""
        # Remove spaces
        postal_clean = v.replace(" ", "")
        
        # Check Polish format: XX-XXX or XXXXX (5 digits)
        if not re.match(r"^\d{2}-?\d{3}$", postal_clean):
            raise ValueError("Postal code must be in format XX-XXX or XXXXX (5 digits)")
        
        # Normalize to XX-XXX format
        if len(postal_clean) == 5:
            postal_clean = f"{postal_clean[:2]}-{postal_clean[2:]}"
        
        return postal_clean


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""

    id: UUID
    owner_id: UUID
    stripe_customer_id: Optional[str]
    type: Optional[str]
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
