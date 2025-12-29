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


class UserRole(str, enum.Enum):
    """User roles enum"""

    admin = "admin"
    user = "user"
    viewer = "viewer"


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

    # Magic link authentication
    magic_link_token = Column(String(255), nullable=True)
    magic_link_expires = Column(DateTime, nullable=True)

    # Role
    role = Column(SQLEnum(UserRole), default=UserRole.user, nullable=False)

    # Multi-tenant: organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    organization = relationship(
        "Organization", back_populates="users", foreign_keys=[organization_id]
    )

    # API tokens
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
