"""
API Token schemas (DTOs)
Pydantic models for API token data
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APITokenCreate(BaseModel):
    model_config = {"strict": True}
    """Schema for creating API token"""

    name: str
    expires_in_days: Optional[int] = None  # None = never expires


class APITokenResponse(BaseModel):
    model_config = {"strict": True}
    """Schema for API token response (without plaintext token)"""

    id: UUID
    user_id: UUID
    name: str
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    is_expired: bool

    model_config = ConfigDict(from_attributes=True)


class APITokenCreateResponse(BaseModel):
    model_config = {"strict": True}
    """Schema for API token creation response (includes plaintext token)"""

    token: APITokenResponse
    plaintext_token: str
    warning: str = "⚠️ Save this token now - it will never be shown again!"
