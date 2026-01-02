"""
Subscription status check endpoint
Allows users to check their subscription status
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.member import Member
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from uuid import UUID
from fastapi import HTTPException, status


async def get_user_primary_org_id(user: User, db: AsyncSession) -> Optional[UUID]:
    """Get user's primary organization ID (first membership), returns None if no org"""
    result = await db.execute(
        select(Member.organization_id)
        .where(Member.user_id == user.id)
        .order_by(Member.joined_at)
        .limit(1)
    )
    return result.scalar_one_or_none()

router = APIRouter()


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's subscription status

    Returns subscription details including:
    - Status (active, trialing, past_due, etc.)
    - Current period (start/end dates)
    - Trial information (if applicable)
    - Plan details
    """
    org_id = await get_user_primary_org_id(current_user, db)
    if not org_id:
        return {
            "has_subscription": False,
            "status": "no_organization",
            "message": "User has no organization",
        }

    # Get subscription
    query = select(Subscription).where(Subscription.organization_id == org_id)
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {
            "has_subscription": False,
            "status": "no_subscription",
            "message": "No subscription found",
            "action": "subscribe",
            "subscription_url": "/api/v1/subscriptions",
        }

    # Calculate subscription validity
    now = datetime.utcnow()
    is_valid = False
    expires_at: Optional[datetime] = None

    if subscription.status == SubscriptionStatus.active:
        is_valid = True
        expires_at = subscription.current_period_end
    elif subscription.status == SubscriptionStatus.trialing:
        is_valid = True
        expires_at = subscription.trial_end
    elif subscription.status == SubscriptionStatus.past_due:
        # Grace period check
        from datetime import timedelta

        from app.core.subscription_check import SubscriptionChecker

        grace_period_end = subscription.current_period_end + timedelta(
            days=SubscriptionChecker.GRACE_PERIOD_DAYS
        )
        is_valid = now <= grace_period_end
        expires_at = grace_period_end

    return {
        "has_subscription": True,
        "is_valid": is_valid,
        "status": subscription.status.value,
        "plan": subscription.plan,
        "current_period_start": (
            subscription.current_period_start.isoformat()
            if subscription.current_period_start
            else None
        ),
        "current_period_end": (
            subscription.current_period_end.isoformat() if subscription.current_period_end else None
        ),
        "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "message": _get_status_message(subscription.status, is_valid),
        "action": _get_status_action(subscription.status, is_valid),
    }


def _get_status_message(status: SubscriptionStatus, is_valid: bool) -> str:
    """Get user-friendly status message"""
    if status == SubscriptionStatus.active:
        return "Your subscription is active"
    elif status == SubscriptionStatus.trialing:
        return "You are on a trial period"
    elif status == SubscriptionStatus.past_due:
        if is_valid:
            return "Payment is overdue but you're still within the grace period"
        else:
            return "Payment is overdue and grace period has expired"
    elif status == SubscriptionStatus.canceled:
        return "Your subscription has been canceled"
    elif status == SubscriptionStatus.incomplete:
        return "Your subscription setup is incomplete"
    elif status == SubscriptionStatus.incomplete_expired:
        return "Your subscription setup has expired"
    elif status == SubscriptionStatus.unpaid:
        return "Your subscription is unpaid"
    else:
        return f"Subscription status: {status.value}"


def _get_status_action(status: SubscriptionStatus, is_valid: bool) -> Optional[str]:
    """Get recommended action for status"""
    if status == SubscriptionStatus.active or status == SubscriptionStatus.trialing:
        return None
    elif status == SubscriptionStatus.past_due:
        return "update_payment"
    elif status == SubscriptionStatus.canceled:
        return "resubscribe"
    elif status == SubscriptionStatus.incomplete:
        return "complete_setup"
    else:
        return "contact_support"
