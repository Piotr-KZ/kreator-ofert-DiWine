"""
Webhook config per organizacja — model + delivery log.

Organizacja moze zdefiniowac URL na ktory wysylamy POST
z danymi o zdarzeniach (nowy lead, publikacja strony, platnosc itd.).
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from fasthub_core.db.base import BaseModel


# Dostepne typy zdarzen
WEBHOOK_EVENT_TYPES = [
    "form_submission",
    "newsletter_signup",
    "site_published",
    "site_updated",
    "site_unpublished",
    "member_invited",
    "member_joined",
    "member_removed",
    "payment_completed",
    "payment_failed",
    "subscription_changed",
    "subscription_canceled",
    "invoice_issued",
]


class WebhookEndpoint(BaseModel):
    """Konfiguracja webhooka per organizacja."""
    __tablename__ = "webhook_endpoints"

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url = Column(String(1000), nullable=False)
    secret = Column(String(255), nullable=False)

    events = Column(JSON, nullable=False, default=list)

    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime, nullable=True)
    last_status_code = Column(Integer, nullable=True)
    consecutive_failures = Column(Integer, default=0)

    description = Column(String(500), nullable=True)


class WebhookDelivery(BaseModel):
    """Log pojedynczego wyslania webhooka."""
    __tablename__ = "webhook_deliveries"

    endpoint_id = Column(
        UUID(as_uuid=True),
        ForeignKey("webhook_endpoints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=True)

    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=False)
    error = Column(Text, nullable=True)

    attempt = Column(Integer, default=1)

    created_at = Column(DateTime, server_default=func.now())
