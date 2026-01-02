"""
User model
Represents users in the system with multi-tenant support
"""

import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """
    User model with multi-tenant support
    Each user belongs to an organization
    """

    __tablename__ = "users"

    # Basic fields
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)  # Platform SuperAdmin

    # Magic link authentication
    magic_link_token = Column(String(255), nullable=True)
    magic_link_expires = Column(DateTime, nullable=True)

    # Multi-org: memberships relationship (replaces single organization_id)
    memberships = relationship("Member", back_populates="user", cascade="all, delete-orphan")

    # API tokens
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
