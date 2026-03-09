"""
Dunning — konfigurowalna sciezka windykacyjna.

DunningPath: szablon sciezki (np. "Standardowa", "Lagodna", "Agresywna")
DunningStep: krok w sciezce (dzien X -> akcja Y)
DunningEvent: log wykonanych akcji per subskrypcja

Wlasciciel aplikacji konfiguruje sciezke w admin panelu.
RecurringManager czyta kroki z DunningPath zamiast hardcodowanych wartosci.
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fasthub_core.db.base import BaseModel


class DunningActionType(str, enum.Enum):
    """Typ akcji w kroku windykacyjnym."""
    EMAIL_REMINDER = "email_reminder"
    EMAIL_WARNING = "email_warning"
    EMAIL_FINAL = "email_final"
    RETRY_PAYMENT = "retry_payment"
    RESTRICT_ACCESS = "restrict_access"
    BLOCK_ACCESS = "block_access"
    DOWNGRADE_FREE = "downgrade_free"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    DISABLE_SITES = "disable_sites"
    NOTIFY_ADMIN = "notify_admin"
    WEBHOOK = "webhook"


class DunningPath(BaseModel):
    """Szablon sciezki windykacyjnej."""
    __tablename__ = "dunning_paths"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    applicable_plans = Column(JSON, nullable=True)

    steps = relationship(
        "DunningStep",
        back_populates="path",
        order_by="DunningStep.day_offset",
        cascade="all, delete-orphan",
    )


class DunningStep(BaseModel):
    """Krok w sciezce windykacyjnej."""
    __tablename__ = "dunning_steps"

    path_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dunning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    day_offset = Column(Integer, nullable=False)
    action_type = Column(SQLEnum(DunningActionType), nullable=False)

    email_template_id = Column(String(100), nullable=True)
    email_subject = Column(String(500), nullable=True)
    email_body_override = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    description = Column(String(500), nullable=True)

    path = relationship("DunningPath", back_populates="steps")


class DunningEvent(BaseModel):
    """Log wykonanej akcji windykacyjnej."""
    __tablename__ = "dunning_events"

    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id"),
        nullable=False,
        index=True,
    )
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    step_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dunning_steps.id"),
        nullable=True,
    )

    day_offset = Column(Integer, nullable=False)
    action_type = Column(SQLEnum(DunningActionType), nullable=False)
    status = Column(String(50), default="executed")
    details = Column(JSON, nullable=True)

    executed_at = Column(DateTime, server_default=func.now())
