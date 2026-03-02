"""
FastHub Core — Billing Middleware.

FastAPI dependencies for enforcing resource limits.

Usage:
    @router.post("/processes", dependencies=[Depends(require_limit("processes"))])
    async def create_process(...):
        ...
"""

import logging

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.db.session import get_db
from fasthub_core.auth.dependencies import get_current_user

logger = logging.getLogger("fasthub.billing")


async def enforce_limit(tenant_id: str, resource: str, db: AsyncSession) -> None:
    """
    Check resource limit. Raises HTTP 402 if exceeded.
    """
    from fasthub_core.billing.service import BillingService
    service = BillingService(db)
    within_limit = await service.check_limit(tenant_id, resource)
    if not within_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Resource limit exceeded for '{resource}'. Upgrade your plan.",
        )


def require_limit(resource: str):
    """
    FastAPI Depends factory — checks limit before endpoint execution.

    Usage:
        @router.post("/processes", dependencies=[Depends(require_limit("processes"))])
    """
    async def _check_limit(
        request: Request,
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        org_id = request.headers.get("X-Organization-Id")
        if not org_id:
            org_id = getattr(current_user, 'organization_id', None)
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Organization-Id header required",
            )
        await enforce_limit(str(org_id), resource, db)
        return current_user

    return _check_limit
