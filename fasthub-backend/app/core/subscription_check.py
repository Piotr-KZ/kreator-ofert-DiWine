"""
Subscription status check middleware
Revenue protection - ensures users have active subscriptions
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from uuid import UUID

logger = logging.getLogger(__name__)


class SubscriptionChecker:
    """
    Subscription status checker

    Validates user subscription status and enforces access control.
    """

    # Grace period for past_due subscriptions (days)
    GRACE_PERIOD_DAYS = 7

    # Endpoints that don't require subscription check
    EXEMPT_PATHS = [
        "/api/v1/auth",  # Auth endpoints
        "/api/v1/health",  # Health checks
        "/api/v1/ready",  # Readiness checks
        "/api/v1/metrics",  # Metrics
        "/api/v1/subscriptions",  # Subscription management
        "/docs",  # API docs
        "/redoc",  # API docs
        "/openapi.json",  # OpenAPI spec
    ]
    
    @classmethod
    async def _get_user_primary_org_id(cls, user: User, db: AsyncSession) -> Optional[UUID]:
        """Get user's primary organization ID (first membership)"""
        result = await db.execute(
            select(Member.organization_id)
            .where(Member.user_id == user.id)
            .order_by(Member.joined_at)
            .limit(1)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def check_subscription(cls, user: User, db: AsyncSession, path: str) -> None:
        """
        Check if user has active subscription

        Args:
            user: Current user
            db: Database session
            path: Request path

        Raises:
            HTTPException: If subscription is invalid or expired
        """
        # Skip check for exempt paths
        if cls._is_exempt_path(path):
            return

        # Get user's organization subscription
        org_id = await cls._get_user_primary_org_id(user, db)
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No organization found. Please contact support.",
            )

        # Get active subscription
        subscription = await cls._get_subscription(org_id, db)

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": "No active subscription found",
                    "action": "subscribe",
                    "subscription_url": "/api/v1/subscriptions",
                },
            )

        # Check subscription status
        await cls._validate_subscription_status(subscription)

    @classmethod
    def _is_exempt_path(cls, path: str) -> bool:
        """Check if path is exempt from subscription check"""
        for exempt_path in cls.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False

    @classmethod
    async def _get_subscription(
        cls, organization_id: UUID, db: AsyncSession
    ) -> Optional[Subscription]:
        """Get active subscription for organization"""
        query = select(Subscription).where(
            Subscription.organization_id == organization_id,
            Subscription.status.in_(
                [
                    SubscriptionStatus.active,
                    SubscriptionStatus.trialing,
                    SubscriptionStatus.past_due,
                ]
            ),
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def _validate_subscription_status(cls, subscription: Subscription) -> None:
        """
        Validate subscription status

        Raises:
            HTTPException: If subscription is invalid
        """
        now = datetime.utcnow()

        # Check if subscription is active
        if subscription.status == SubscriptionStatus.active:
            # Check if subscription period is valid
            if subscription.current_period_end and subscription.current_period_end < now:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "message": "Subscription period has ended",
                        "action": "renew",
                        "subscription_url": "/api/v1/subscriptions",
                    },
                )
            return

        # Check if subscription is trialing
        if subscription.status == SubscriptionStatus.trialing:
            if subscription.trial_end and subscription.trial_end < now:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "message": "Trial period has ended",
                        "action": "subscribe",
                        "subscription_url": "/api/v1/subscriptions",
                    },
                )
            return

        # Check if subscription is past_due (with grace period)
        if subscription.status == SubscriptionStatus.past_due:
            grace_period_end = subscription.current_period_end + timedelta(
                days=cls.GRACE_PERIOD_DAYS
            )

            if now > grace_period_end:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "message": "Payment is overdue. Please update your payment method.",
                        "action": "update_payment",
                        "subscription_url": "/api/v1/subscriptions/billing-portal",
                    },
                )

            # Within grace period - log warning but allow access
            logger.warning(
                f"User {subscription.organization_id} accessing with past_due subscription "
                f"(grace period ends {grace_period_end})"
            )
            return

        # All other statuses (canceled, incomplete, etc.) - deny access
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": f"Subscription is {subscription.status.value}",
                "action": "subscribe",
                "subscription_url": "/api/v1/subscriptions",
            },
        )


async def require_active_subscription(user: User, db: AsyncSession, path: str) -> None:
    """
    Dependency for endpoints that require active subscription

    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
            _: None = Depends(require_active_subscription)
        ):
            ...
    """
    await SubscriptionChecker.check_subscription(user, db, path)


# ============================================================================
# WRAPPER FUNCTIONS FOR TESTS
# ============================================================================

async def check_subscription_active(
    db: AsyncSession, 
    organization_id: UUID
) -> bool:
    """
    Check if organization has active subscription (wrapper for tests)
    
    Args:
        db: Database session
        organization_id: Organization UUID
        
    Returns:
        True if subscription is active, False otherwise
    """
    subscription = await SubscriptionChecker._get_subscription(organization_id, db)
    
    if not subscription:
        return False
        
    # Check if subscription is in valid state
    now = datetime.utcnow()
    
    if subscription.status == SubscriptionStatus.active:
        if subscription.current_period_end and subscription.current_period_end >= now:
            return True
    elif subscription.status == SubscriptionStatus.trialing:
        if subscription.trial_end and subscription.trial_end >= now:
            return True
    elif subscription.status == SubscriptionStatus.past_due:
        grace_period_end = subscription.current_period_end + timedelta(
            days=SubscriptionChecker.GRACE_PERIOD_DAYS
        )
        if now <= grace_period_end:
            return True
            
    return False
