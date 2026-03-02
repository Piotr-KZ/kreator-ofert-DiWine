"""
Invitation model — GDPR-compliant team invitations.
"""

import enum

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from fasthub_core.db.base import BaseModel


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    canceled = "canceled"


class Invitation(BaseModel):
    __tablename__ = "invitations"

    email = Column(String(320), nullable=False, index=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    role = Column(String(50), default="viewer", nullable=False)
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.pending, nullable=False, index=True)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    accepted_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
