"""
Member model
Represents membership relationship between users and organizations
Enables multi-org support and role-based permissions
"""

import enum

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class MemberRole(str, enum.Enum):
    """Member roles within an organization"""
    
    ADMIN = "admin"  # Can manage members, edit org, view billing
    VIEWER = "viewer"  # Read-only access, cannot manage


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
        index=True  # Index for filtering by role
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
