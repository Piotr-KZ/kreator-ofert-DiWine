"""
UserSession model — tracking active sessions per user/device.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fasthub_core.db.base import BaseModel


class UserSession(BaseModel):
    __tablename__ = "user_sessions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)

    # Device info
    device_type = Column(String(50), nullable=True)
    device_name = Column(String(255), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)

    # Network
    ip_address = Column(String(45), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_active_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User")

    def __repr__(self):
        return f"<UserSession user={self.user_id} device={self.device_name}>"
