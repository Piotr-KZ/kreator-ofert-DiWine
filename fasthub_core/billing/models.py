"""
Subscription and Invoice models
Manages Stripe subscriptions and invoicing
"""

import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


# ============================================================================
# Subscription Model
# ============================================================================

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


# ============================================================================
# Invoice Model
# ============================================================================

class InvoiceStatus(str, enum.Enum):
    """Invoice status enum"""

    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class Invoice(BaseModel):
    """
    Invoice model
    Can be generated from Stripe or manually created
    """

    __tablename__ = "invoices"

    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="invoices")

    # Invoice details
    invoice_number = Column(String(255), unique=True, nullable=False)

    # External IDs
    stripe_invoice_id = Column(String(255), unique=True, nullable=True)
    fakturownia_id = Column(String(255), unique=True, nullable=True)

    # Status
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)

    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Description
    description = Column(Text, nullable=True)

    # PDF
    pdf_url = Column(Text, nullable=True)

    # Dates
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status}>"
