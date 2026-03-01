"""
API Token model
Database model for API authentication tokens
"""

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class APIToken(BaseModel):
    """
    API Token model for programmatic API access
    Stores hashed tokens for security (never store plaintext!)
    """

    __tablename__ = "api_tokens"

    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Token data
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)  # User-friendly name for token

    # Metadata
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_tokens")

    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if token is valid (not expired)"""
        return not self.is_expired
