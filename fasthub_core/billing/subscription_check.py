"""
Subscription Enforcement — blokada dostępu bez aktywnej subskrypcji.

Grace period: 7 dni po past_due (płatność się nie udała, ale user jeszcze działa).
Trial: działa do trial_end.
Exempt paths: auth, health, billing — dostępne zawsze (żeby user mógł zapłacić!).

Użycie:
    from fasthub_core.billing.subscription_check import require_active_subscription

    @router.get("/protected", dependencies=[Depends(require_active_subscription)])
    async def protected():
        ...

Albo jako middleware:
    from fasthub_core.billing.subscription_check import SubscriptionChecker

    # W middleware albo dependency
    await SubscriptionChecker.check_subscription(user, db, request.url.path)
"""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.billing.models import Subscription, SubscriptionStatus
from fasthub_core.db.session import get_db

try:
    from fasthub_core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SubscriptionChecker:
    """
    Walidacja subskrypcji per organizacja.

    Konfigurowalny:
    - GRACE_PERIOD_DAYS: ile dni po past_due user jeszcze działa
    - EXEMPT_PATHS: ścieżki które nie wymagają subskrypcji
    - ACTIVE_STATUSES: statusy traktowane jako "aktywne"
    """

    GRACE_PERIOD_DAYS: int = 7

    EXEMPT_PATHS: List[str] = [
        "/api/auth",
        "/api/v1/auth",
        "/api/billing",
        "/api/v1/billing",
        "/api/v1/subscriptions",
        "/api/health",
        "/api/v1/health",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    ACTIVE_STATUSES = [
        SubscriptionStatus.active,
        SubscriptionStatus.trialing,
        SubscriptionStatus.past_due,
    ]

    @classmethod
    def configure(
        cls,
        grace_period_days: int = None,
        exempt_paths: List[str] = None,
    ) -> None:
        """
        Konfiguruj checker (wywołaj raz przy starcie).

        Aplikacja może dodać własne exempt paths:
            SubscriptionChecker.configure(
                exempt_paths=["/api/auth", "/api/health", "/api/my-custom-path"],
            )
        """
        if grace_period_days is not None:
            cls.GRACE_PERIOD_DAYS = grace_period_days
        if exempt_paths is not None:
            cls.EXEMPT_PATHS = exempt_paths

    @classmethod
    async def check_subscription(
        cls,
        organization_id: UUID,
        db: AsyncSession,
        path: str,
    ) -> None:
        """
        Sprawdź subskrypcję organizacji.

        Raises:
            HTTPException 402: Brak subskrypcji lub wygasła
            HTTPException 403: Brak organizacji
        """
        if cls._is_exempt_path(path):
            return

        subscription = await cls._get_subscription(organization_id, db)

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "no_subscription",
                    "message": "Brak aktywnej subskrypcji. Wybierz plan.",
                    "action": "subscribe",
                    "billing_url": "/billing",
                },
            )

        await cls._validate_status(subscription)

    @classmethod
    def _is_exempt_path(cls, path: str) -> bool:
        return any(path.startswith(exempt) for exempt in cls.EXEMPT_PATHS)

    @classmethod
    async def _get_subscription(
        cls, organization_id: UUID, db: AsyncSession
    ) -> Optional[Subscription]:
        result = await db.execute(
            select(Subscription).where(
                Subscription.organization_id == organization_id,
                Subscription.status.in_(cls.ACTIVE_STATUSES),
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def _validate_status(cls, subscription: Subscription) -> None:
        now = datetime.utcnow()

        # Active — sprawdź period
        if subscription.status == SubscriptionStatus.active:
            if subscription.current_period_end and subscription.current_period_end < now:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "subscription_expired",
                        "message": "Okres subskrypcji wygasł. Odnów plan.",
                        "action": "renew",
                    },
                )
            return

        # Trial — sprawdź trial_end
        if subscription.status == SubscriptionStatus.trialing:
            if subscription.trial_end and subscription.trial_end < now:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "trial_expired",
                        "message": "Okres próbny się skończył. Wybierz plan.",
                        "action": "subscribe",
                    },
                )
            return

        # Past due — grace period
        if subscription.status == SubscriptionStatus.past_due:
            if subscription.current_period_end:
                grace_end = subscription.current_period_end + timedelta(
                    days=cls.GRACE_PERIOD_DAYS
                )
                if now > grace_end:
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail={
                            "error": "payment_overdue",
                            "message": "Płatność przeterminowana. Zaktualizuj metodę płatności.",
                            "action": "update_payment",
                        },
                    )
            logger.warning(
                "subscription_past_due_access",
                organization_id=str(subscription.organization_id),
                status="past_due",
            ) if hasattr(logger, 'warning') else None
            return

        # Inne statusy — blokuj
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "subscription_inactive",
                "message": f"Subskrypcja jest {subscription.status.value}.",
                "action": "subscribe",
            },
        )

    @classmethod
    async def is_subscription_active(
        cls, organization_id: UUID, db: AsyncSession
    ) -> bool:
        """
        Helper bez rzucania wyjątku — True/False.

        Użycie: warunkowe renderowanie w UI, nie blokowanie.
        """
        subscription = await cls._get_subscription(organization_id, db)
        if not subscription:
            return False

        now = datetime.utcnow()
        if subscription.status == SubscriptionStatus.active:
            return not (subscription.current_period_end and subscription.current_period_end < now)
        if subscription.status == SubscriptionStatus.trialing:
            return not (subscription.trial_end and subscription.trial_end < now)
        if subscription.status == SubscriptionStatus.past_due:
            if subscription.current_period_end:
                grace_end = subscription.current_period_end + timedelta(days=cls.GRACE_PERIOD_DAYS)
                return now <= grace_end
        return False


# ============================================================================
# FastAPI Dependency
# ============================================================================

def require_active_subscription():
    """
    FastAPI Depends — wymaga aktywnej subskrypcji.

    Użycie:
        @router.get("/protected")
        async def endpoint(
            ...,
            _sub = Depends(require_active_subscription()),
        ):
    """
    async def _check(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        # Pobierz organization_id z request
        org_id = request.headers.get("X-Organization-Id")
        if not org_id:
            # Spróbuj z current_user
            user = getattr(request.state, "user", None)
            org_id = getattr(user, "organization_id", None) if user else None

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Organization-Id header required",
            )

        await SubscriptionChecker.check_subscription(
            UUID(str(org_id)), db, request.url.path,
        )

    return _check
