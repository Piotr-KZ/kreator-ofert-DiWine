"""
Subscriptions endpoints
API routes for subscription operations (matching Firebase use cases)
"""

from typing import Optional

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_active_user, require_organization_owner
from app.db.session import get_db
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate
from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService

router = APIRouter()


@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create subscription for user's organization

    Firebase equivalent: createSubscriptionForUser
    Creates a new subscription with the specified plan.
    """
    subscription_service = SubscriptionService(db)

    # Map plan to Stripe price ID (configure in settings)
    price_map = {
        "free": None,  # Free plan doesn't need Stripe
        "starter": (
            settings.STRIPE_STARTER_PRICE_ID
            if hasattr(settings, "STRIPE_STARTER_PRICE_ID")
            else None
        ),
        "professional": (
            settings.STRIPE_PRO_PRICE_ID if hasattr(settings, "STRIPE_PRO_PRICE_ID") else None
        ),
        "enterprise": (
            settings.STRIPE_ENTERPRISE_PRICE_ID
            if hasattr(settings, "STRIPE_ENTERPRISE_PRICE_ID")
            else None
        ),
    }

    price_id = price_map.get(subscription_data.plan)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan or price not configured: {subscription_data.plan}",
        )

    subscription = await subscription_service.create_subscription_for_user(
        user=current_user,
        price_id=price_id,
        payment_method_id=subscription_data.payment_method_id,
        trial_days=14,  # 14-day trial
    )

    return subscription


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """
    Get current user's organization subscription

    Returns active subscription details.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization"
        )

    subscription_service = SubscriptionService(db)
    subscription = await subscription_service.get_subscription_by_organization(
        current_user.organization_id
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
        )

    return subscription


@router.patch("/change-plan", response_model=SubscriptionResponse)
async def change_subscription_plan(
    new_plan: str,
    current_user: User = Depends(require_organization_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Change subscription plan

    Firebase equivalent: changeSubscriptionPlan
    Only organization owner can change the plan.
    """
    # Map plan to Stripe price ID
    price_map = {
        "starter": (
            settings.STRIPE_STARTER_PRICE_ID
            if hasattr(settings, "STRIPE_STARTER_PRICE_ID")
            else None
        ),
        "professional": (
            settings.STRIPE_PRO_PRICE_ID if hasattr(settings, "STRIPE_PRO_PRICE_ID") else None
        ),
        "enterprise": (
            settings.STRIPE_ENTERPRISE_PRICE_ID
            if hasattr(settings, "STRIPE_ENTERPRISE_PRICE_ID")
            else None
        ),
    }

    new_price_id = price_map.get(new_plan)
    if not new_price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan or price not configured: {new_plan}",
        )

    subscription_service = SubscriptionService(db)
    subscription = await subscription_service.change_subscription_plan(
        organization_id=current_user.organization_id,
        new_price_id=new_price_id,
        current_user=current_user,
    )

    return subscription


@router.post("/cancel")
async def cancel_subscription(
    at_period_end: bool = True,
    current_user: User = Depends(require_organization_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel subscription

    Only organization owner can cancel.
    If at_period_end=True, cancels at end of billing period.
    If at_period_end=False, cancels immediately.
    """
    subscription_service = SubscriptionService(db)
    subscription = await subscription_service.cancel_subscription(
        organization_id=current_user.organization_id,
        at_period_end=at_period_end,
        current_user=current_user,
    )

    return {"status": "canceled", "at_period_end": at_period_end}


@router.get("/invoice/check")
async def check_subscription_invoice(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """
    Check current subscription invoice status

    Firebase equivalent: checkSubscriptionInvoice
    Returns latest invoice details from Stripe.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization"
        )

    subscription_service = SubscriptionService(db)
    invoice_data = await subscription_service.check_subscription_invoice(
        organization_id=current_user.organization_id
    )

    return invoice_data


@router.post("/billing-portal")
async def create_billing_portal(
    return_url: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe billing portal session

    Firebase equivalent: createBillingCustomerPortal
    Returns URL to Stripe's hosted billing portal.
    """
    subscription_service = SubscriptionService(db)
    result = await subscription_service.create_billing_portal_session(
        organization_id=current_user.organization_id,
        return_url=return_url,
        current_user=current_user,
    )

    return result


@router.post("/webhooks/stripe", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhooks

    Firebase equivalents:
    - handleSubscriptionStatusUpdate
    - handleCustomerUpdate
    - handleFailedPayment
    - handleSubscriptionCycle
    """
    payload = await request.body()

    # Verify webhook signature
    webhook_secret = (
        settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, "STRIPE_WEBHOOK_SECRET") else None
    )
    if not webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured",
        )

    try:
        stripe_service = StripeService()
        event = await stripe_service.construct_webhook_event(
            payload=payload, signature=stripe_signature, webhook_secret=webhook_secret
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    subscription_service = SubscriptionService(db)

    # Handle different event types
    if event.type == "customer.subscription.updated":
        await subscription_service.handle_subscription_updated(event.data.object)

    elif event.type == "customer.subscription.deleted":
        await subscription_service.handle_subscription_deleted(event.data.object)

    elif event.type == "customer.updated":
        await subscription_service.handle_customer_updated(event.data.object)

    elif event.type == "invoice.payment_failed":
        # Firebase equivalent: handleFailedPayment
        await subscription_service.handle_failed_payment(event.data.object)

    elif event.type == "invoice.payment_succeeded":
        # Firebase equivalent: handleSubscriptionCycle
        await subscription_service.handle_subscription_cycle(event.data.object)

    return {"status": "success"}
