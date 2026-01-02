"""
Audit Log model
Tracks SuperAdmin actions for accountability and security
"""

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from datetime import datetime
from uuid import uuid4


class AuditLog(Base):
    """
    Audit log for tracking SuperAdmin actions
    """

    __tablename__ = "audit_logs"

    # Primary key and timestamp
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Who performed the action
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user = relationship("User")

    # What action was performed
    action = Column(String(100), nullable=False, index=True)  # e.g., 'user.delete', 'user.update'
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., 'user', 'organization'
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Additional context
    details = Column(JSON, nullable=True)  # What changed, old/new values, etc.
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
