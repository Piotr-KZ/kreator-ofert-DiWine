"""
Feature Flags — sprawdzanie uprawnień per plan.

Model BillingPlan ma pole features: JSON, np.:
    {"webhooks": True, "api_access": True, "sub_processes": False}

Ten moduł dodaje:
- check_feature(tenant_id, feature_name) -> bool
- require_feature(feature_name) -> FastAPI Depends

Użycie:
    # Bezpośrednio:
    enabled = await check_feature(db, tenant_id, "webhooks")

    # Jako dependency:
    @router.post("/webhooks/create")
    async def create_webhook(
        ...,
        _feature = Depends(require_feature("webhooks")),
    ):
        ...
"""

import logging
from typing import Dict

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.db.session import get_db

logger = logging.getLogger(__name__)


async def check_feature(
    db: AsyncSession,
    tenant_id: str,
    feature_name: str,
) -> bool:
    """
    Sprawdź czy plan tenanta ma włączoną feature.

    Returns:
        True jeśli feature włączona, False jeśli nie (lub brak planu).
    """
    try:
        from fasthub_core.billing.service import BillingService
        service = BillingService(db)
        subscription = await service.get_subscription(tenant_id)

        if not subscription or not subscription.get("plan"):
            return False

        plan = subscription["plan"]
        features = getattr(plan, "features", None) or {}

        return bool(features.get(feature_name, False))
    except Exception as e:
        logger.warning(f"Feature check failed for {feature_name}: {e}")
        return False


async def get_plan_features(
    db: AsyncSession,
    tenant_id: str,
) -> Dict[str, bool]:
    """
    Zwróć wszystkie features planu jako dict.

    Returns:
        {"webhooks": True, "api_access": False, ...}
    """
    try:
        from fasthub_core.billing.service import BillingService
        service = BillingService(db)
        subscription = await service.get_subscription(tenant_id)

        if not subscription or not subscription.get("plan"):
            return {}

        plan = subscription["plan"]
        return dict(getattr(plan, "features", None) or {})
    except Exception:
        return {}


def require_feature(feature_name: str, error_message: str = None):
    """
    FastAPI Depends — blokuje endpoint jeśli plan nie ma feature.

    HTTP 402 Payment Required — zachęca do upgrade'u planu.

    Użycie:
        @router.post("/webhooks")
        async def create_webhook(
            ...,
            _f = Depends(require_feature("webhooks")),
        ):
            ...

        # Z custom message:
        @router.get("/api/external")
        async def external_api(
            ...,
            _f = Depends(require_feature("api_access", "Dostęp API wymaga planu Pro")),
        ):
            ...
    """
    async def _check(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        # Resolve tenant/org ID
        org_id = request.headers.get("X-Organization-Id")
        if not org_id:
            user = getattr(request.state, "user", None)
            org_id = getattr(user, "organization_id", None) if user else None

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Organization-Id header required",
            )

        enabled = await check_feature(db, str(org_id), feature_name)

        if not enabled:
            # Pobierz nazwę planu dla lepszego komunikatu
            plan_name = "obecny"
            try:
                from fasthub_core.billing.service import BillingService
                service = BillingService(db)
                subscription = await service.get_subscription(str(org_id))
                if subscription and subscription.get("plan"):
                    plan_name = getattr(subscription["plan"], "name", "obecny")
            except Exception:
                pass

            msg = error_message or (
                f"Funkcja '{feature_name}' nie jest dostępna w planie '{plan_name}'. "
                f"Zmień plan na wyższy."
            )

            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "feature_not_available",
                    "feature": feature_name,
                    "plan": plan_name,
                    "message": msg,
                    "upgrade_url": "/billing",
                },
            )

        return True

    return _check
