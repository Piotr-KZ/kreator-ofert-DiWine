"""
Member schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.member import MemberRole


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


class MemberInDB(MemberBase):
    model_config = {"from_attributes": True}
    """Member schema as stored in database"""
    
    id: int
    user_id: UUID
    organization_id: UUID
    joined_at: datetime
    created_at: datetime
    updated_at: datetime


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
    
    # Nested user info
    user: UserBasicInfo


class MemberListResponse(BaseModel):
    model_config = {"strict": True, "from_attributes": True}
    """Response for listing members"""
    
    members: list[MemberResponse]
    total: int
