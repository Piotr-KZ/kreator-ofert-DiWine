"""
Billing models — Subscription, Invoice + AutoFlow billing system.

Existing models (Brief 0): Subscription, Invoice — UUID BaseModel.
New models (Brief 10): BillingPlan, BillingAddon, TenantAddon, UsageRecord, BillingEvent — Integer PK.
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel
from fasthub_core.db.session import Base


# ============================================================================
# Subscription Model (existing — UUID BaseModel)
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

    # Plan reference (optional — links to BillingPlan)
    plan_id = Column(Integer, ForeignKey("billing_plans.id"), nullable=True)
    billing_interval = Column(String(20), nullable=True)  # "monthly" or "yearly"

    # Stripe fields
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=False)

    # Status
    status = Column(SQLEnum(SubscriptionStatus), nullable=False)

    # Billing period
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)

    # Trial
    trial_end = Column(DateTime, nullable=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Subscription {self.stripe_subscription_id} - {self.status}>"


# ============================================================================
# Invoice Model (existing — UUID BaseModel)
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


# ============================================================================
# BillingPlan — plan definition (Integer PK, from AutoFlow)
# ============================================================================

class BillingPlan(Base):
    """
    Billing plan definition.
    billing_mode: "fixed" (flat price) or "modular" (base + addons).
    """

    __tablename__ = "billing_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    billing_mode = Column(String(20), default="fixed")  # "fixed" or "modular"

    # Pricing
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    currency = Column(String(3), default="PLN")

    # Stripe IDs
    stripe_price_monthly_id = Column(String(100), nullable=True)
    stripe_price_yearly_id = Column(String(100), nullable=True)
    stripe_product_id = Column(String(100), nullable=True)

    # Limits (resource caps per plan)
    max_processes = Column(Integer, default=3)
    max_executions_month = Column(Integer, default=100)
    max_integrations = Column(Integer, default=3)
    max_ai_operations_month = Column(Integer, default=50)
    max_team_members = Column(Integer, default=1)
    max_file_storage_mb = Column(Integer, default=100)

    # Features (JSON — app-specific feature flags)
    features = Column(JSON, default=dict)

    # Display
    sort_order = Column(Integer, default=0)
    badge = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # hex color

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BillingPlan {self.slug} ({self.billing_mode})>"


# ============================================================================
# BillingAddon — purchasable resource packs
# ============================================================================

class BillingAddon(Base):
    """Add-on resource pack (extra processes, AI calls, storage)."""

    __tablename__ = "billing_addons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=False)  # e.g. "processes", "ai_operations"
    quantity = Column(Integer, default=0)  # how many units this addon adds

    # Pricing
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    currency = Column(String(3), default="PLN")

    # Stripe IDs
    stripe_price_monthly_id = Column(String(100), nullable=True)
    stripe_price_yearly_id = Column(String(100), nullable=True)
    stripe_product_id = Column(String(100), nullable=True)

    # Availability
    available_for_plans = Column(JSON, nullable=True)  # list of plan slugs
    max_quantity_per_tenant = Column(Integer, default=0)  # 0 = unlimited
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BillingAddon {self.slug} ({self.resource_type})>"


# ============================================================================
# TenantAddon — purchased addon per tenant
# ============================================================================

class TenantAddon(Base):
    """Active addon purchase for a tenant (organization)."""

    __tablename__ = "tenant_addons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(100), index=True, nullable=False)
    addon_id = Column(Integer, ForeignKey("billing_addons.id"), nullable=False)
    quantity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    stripe_subscription_item_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationship
    addon = relationship("BillingAddon")

    def __repr__(self):
        return f"<TenantAddon tenant={self.tenant_id} addon={self.addon_id}>"


# ============================================================================
# UsageRecord — monthly usage tracking per tenant
# ============================================================================

class UsageRecord(Base):
    """Monthly resource usage for a tenant."""

    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(100), index=True, nullable=False)
    period = Column(String(7), index=True, nullable=False)  # "2026-03"

    # Usage counters
    executions_count = Column(Integer, default=0)
    ai_operations_count = Column(Integer, default=0)
    active_processes_count = Column(Integer, default=0)
    active_integrations_count = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0.0)
    webhook_calls_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UsageRecord tenant={self.tenant_id} period={self.period}>"


# ============================================================================
# BillingEvent — audit trail for billing operations
# ============================================================================

class BillingEvent(Base):
    """Audit trail for billing events (Stripe webhooks, plan changes)."""

    __tablename__ = "billing_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(100), index=True, nullable=False)
    event_type = Column(String(100), index=True, nullable=False)
    stripe_event_id = Column(String(100), nullable=True, unique=True)
    data = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BillingEvent {self.event_type} tenant={self.tenant_id}>"
