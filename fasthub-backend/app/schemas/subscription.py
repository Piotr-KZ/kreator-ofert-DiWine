"""
Subscription schemas (DTOs)
Pydantic models for subscription data
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubscriptionStatus(str, Enum):
    """Subscription status enum"""

    active = "active"
    canceled = "canceled"
    past_due = "past_due"
    trialing = "trialing"
    incomplete = "incomplete"


class SubscriptionPlan(str, Enum):
    """Subscription plan enum"""

    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"


class SubscriptionBase(BaseModel):
    model_config = {"strict": True}
    """Base subscription schema"""

    plan: Optional[SubscriptionPlan] = None
    status: SubscriptionStatus


class SubscriptionCreate(BaseModel):
    model_config = {"strict": True}
    """Schema for creating subscription"""

    plan: SubscriptionPlan
    payment_method_id: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    model_config = {"strict": True}
    """Schema for updating subscription"""

    plan: Optional[SubscriptionPlan] = None
    status: Optional[SubscriptionStatus] = None


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response"""

    id: Optional[UUID] = None
    organization_id: UUID
    stripe_subscription_id: Optional[str]
    stripe_price_id: Optional[str]
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionWithDetails(SubscriptionResponse):
    """Schema for subscription with additional details"""

    organization_name: Optional[str] = None
    days_until_renewal: Optional[int] = None
    is_trial: bool = False
