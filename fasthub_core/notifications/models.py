"""
Model powiadomienia in-app + preferencje.

Notification — powiadomienie dla usera (typ, tytuł, treść, link, status)
NotificationPreference — preferencje per user per typ (in-app, email)
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from fasthub_core.db.base import BaseModel


class Notification(BaseModel):
    """Powiadomienie in-app dla uzytkownika"""

    __tablename__ = "notifications"

    # Odbiorca
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)

    # Tresc
    type = Column(String(50), nullable=False, index=True)
    # Typy: "invitation", "role_change", "security_alert", "billing",
    #        "system", "impersonation", "approval_request", "approval_result"
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)

    # Status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Kto wywolal (opcjonalnie)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_notif_user_unread", "user_id", "is_read"),
        Index("ix_notif_user_created", "user_id", "created_at"),
    )


class NotificationPreference(BaseModel):
    """
    Preferencje powiadomien per user per typ.

    Przyklad:
    user_id=Jan, notification_type="invitation", channel_inapp=True, channel_email=True
    user_id=Jan, notification_type="billing", channel_inapp=True, channel_email=False
    """

    __tablename__ = "notification_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(String(50), nullable=False)

    channel_inapp = Column(Boolean, default=True)
    channel_email = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_notifpref_user_type", "user_id", "notification_type", unique=True),
    )
