"""
User, Organization, and Member models
Core models for multi-tenant SaaS architecture
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fasthub_core.db.base import BaseModel


# ============================================================================
# User Model
# ============================================================================

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
    is_superuser = Column(Boolean, default=False, nullable=False)  # Legacy field
    is_superadmin = Column(Boolean, default=False, nullable=False)  # Platform Super Admin

    # Email verification
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)

    # Magic link authentication
    magic_link_token = Column(String(255), nullable=True, index=True)
    magic_link_expires = Column(DateTime, nullable=True)

    # Multi-org: memberships relationship (replaces single organization_id)
    memberships = relationship("Member", back_populates="user", cascade="all, delete-orphan")

    # API tokens
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


# ============================================================================
# Organization Model
# ============================================================================

class Organization(BaseModel):
    """
    Organization model for multi-tenancy
    Each organization has multiple users and subscriptions
    """

    __tablename__ = "organizations"

    # Basic fields
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)

    # Organization details
    type = Column(String(50), nullable=True)  # 'business' or 'individual'
    email = Column(String(255), nullable=True)  # Organization email
    nip = Column(String(50), nullable=True)  # Tax ID
    phone = Column(String(50), nullable=True)

    # Billing address
    billing_street = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(100), nullable=True)

    # Onboarding status
    is_complete = Column(Boolean, default=False, nullable=False)

    # Owner (nullable to break circular dependency)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True)

    # Relationships
    members = relationship("Member", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name}>"


# ============================================================================
# Member Model (User-Organization junction)
# ============================================================================

class MemberRole(str, enum.Enum):
    """Member roles within an organization"""

    ADMIN = "admin"
    VIEWER = "viewer"


class Member(BaseModel):
    """
    Member model for many-to-many user-organization relationship

    Enables:
    - Multi-org support (users can belong to multiple organizations)
    - Role-based permissions (admin vs viewer)
    - Team management (invite/remove members)
    """

    __tablename__ = "members"

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Role within organization
    role = Column(
        SQLEnum(MemberRole, name="memberrole", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MemberRole.ADMIN,
        index=True
    )

    # Membership metadata
    joined_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="members")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
        {'comment': 'Members table for multi-org support with role-based permissions'}
    )

    def __repr__(self):
        return f"<Member user_id={self.user_id} org_id={self.organization_id} role={self.role}>"

    @property
    def is_admin(self) -> bool:
        """Check if member has admin role"""
        return self.role == MemberRole.ADMIN

    @property
    def is_viewer(self) -> bool:
        """Check if member has viewer role"""
        return self.role == MemberRole.VIEWER
