"""
Subscription model
Manages Stripe subscriptions for organizations
"""

import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum (matches Stripe statuses)"""

    active = "active"
    canceled = "canceled"
    incomplete = "incomplete"
    incomplete_expired = "incomplete_expired"
    past_due = "past_due"
    trialing = "trialing"
    unpaid = "unpaid"


class Subscription(BaseModel):
    """
    Subscription model linked to Stripe
    Each organization can have one active subscription
    """

    __tablename__ = "subscriptions"

    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="subscriptions")

    # Stripe fields
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_price_id = Column(String(255), nullable=False)

    # Status
    status = Column(SQLEnum(SubscriptionStatus), nullable=False)

    # Billing period
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Subscription {self.stripe_subscription_id} - {self.status}>"
