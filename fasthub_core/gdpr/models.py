"""
DeletionRequest — GDPR Art. 17 account deletion workflow.

Statuses: pending → processing → completed
                → canceled
                → failed
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from fasthub_core.db.base import BaseModel


class DeletionRequest(BaseModel):
    __tablename__ = "deletion_requests"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    # pending, canceled, processing, completed, failed

    execute_after = Column(DateTime, nullable=False)  # requested_at + grace period
    executed_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    export_file_path = Column(String(500), nullable=True)
    reason = Column(Text, nullable=True)  # optional user-provided reason
