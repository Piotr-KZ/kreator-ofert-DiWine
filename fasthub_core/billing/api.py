"""
FastHub Core — Billing API endpoints.

User-facing + admin + catalog endpoints.

Usage:
    from fasthub_core.billing.api import router
    app.include_router(router, prefix="/api/v1")
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel as PydanticModel
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.db.session import get_db

logger = logging.getLogger("fasthub.billing")

router = APIRouter(tags=["billing"])


# === Pydantic Schemas ===

class PlanResponse(PydanticModel):
    slug: str
    name: str
    description: Optional[str] = None
    billing_mode: str = "fixed"
    price_monthly: float = 0.0
    price_yearly: float = 0.0
    currency: str = "PLN"
    max_processes: int = 0
    max_executions_month: int = 0
    max_integrations: int = 0
    max_ai_operations_month: int = 0
    max_team_members: int = 0
    max_file_storage_mb: int = 0
    features: dict = {}
    badge: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class UsageResponse(PydanticModel):
    resource: str
    current: int
    limit: int
    remaining: int
    exceeded: bool


class CheckoutRequest(PydanticModel):
    price_id: str
    success_url: str
    cancel_url: str


class PortalRequest(PydanticModel):
    return_url: str


# === User-facing endpoints ===

@router.get("/billing/subscription")
async def get_subscription(
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription for user's organization."""
    from fasthub_core.billing.service import BillingService
    org_id = request.headers.get("X-Organization-Id")
    if not org_id:
        org_id = str(getattr(current_user, 'organization_id', ''))
    if not org_id:
        raise HTTPException(status_code=400, detail="X-Organization-Id required")

    service = BillingService(db)
    sub = await service.get_subscription(org_id)
    if not sub:
        return {"subscription": None, "plan": None}

    plan_data = None
    if sub.get("plan"):
        plan = sub["plan"]
        plan_data = {
            "slug": plan.slug, "name": plan.name,
            "billing_mode": plan.billing_mode,
        }

    return {
        "subscription": {
            "status": sub.get("status"),
            "stripe_subscription_id": sub.get("stripe_subscription_id"),
        },
        "plan": plan_data,
    }


@router.get("/billing/usage")
async def get_usage(
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage summary for current billing period."""
    from fasthub_core.billing.service import BillingService
    org_id = request.headers.get("X-Organization-Id")
    if not org_id:
        org_id = str(getattr(current_user, 'organization_id', ''))

    service = BillingService(db)
    return await service.get_usage_summary(org_id)


@router.post("/billing/checkout")
async def create_checkout(
    body: CheckoutRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe Checkout Session."""
    from fasthub_core.billing.service import BillingService
    org_id = request.headers.get("X-Organization-Id")
    if not org_id:
        org_id = str(getattr(current_user, 'organization_id', ''))

    service = BillingService(db)
    result = await service.create_checkout_session(
        tenant_id=org_id,
        price_id=body.price_id,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
    )
    if not result:
        raise HTTPException(status_code=500, detail="Stripe checkout failed")
    return result


@router.post("/billing/portal")
async def create_portal(
    body: PortalRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe Customer Portal session."""
    from fasthub_core.billing.service import BillingService
    org_id = request.headers.get("X-Organization-Id")
    if not org_id:
        org_id = str(getattr(current_user, 'organization_id', ''))

    service = BillingService(db)
    sub = await service.get_subscription(org_id)
    if not sub or not sub.get("subscription"):
        raise HTTPException(status_code=404, detail="No subscription found")

    customer_id = getattr(sub["subscription"], "stripe_customer_id", None)
    if not customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer ID")

    result = await service.create_portal_session(customer_id, body.return_url)
    if not result:
        raise HTTPException(status_code=500, detail="Stripe portal failed")
    return result


@router.post("/billing/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    from fasthub_core.billing.service import BillingService
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    service = BillingService(db)
    result = await service.handle_stripe_webhook(payload, sig_header)
    if not result:
        raise HTTPException(status_code=400, detail="Webhook processing failed")
    return {"status": "ok"}


# === Catalog (public) ===

@router.get("/catalog/plans", response_model=List[PlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    """Public list of billing plans (pricing page)."""
    from fasthub_core.billing.service import BillingService
    service = BillingService(db)
    plans = await service.list_plans(visible_only=True)
    return plans


@router.get("/catalog/addons")
async def list_addons(
    plan: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Public list of billing addons."""
    from fasthub_core.billing.service import BillingService
    service = BillingService(db)
    addons = await service.get_available_addons(plan_slug=plan)
    return [
        {
            "slug": a.slug, "name": a.name,
            "resource_type": a.resource_type, "quantity": a.quantity,
            "price_monthly": a.price_monthly, "price_yearly": a.price_yearly,
        }
        for a in addons
    ]
