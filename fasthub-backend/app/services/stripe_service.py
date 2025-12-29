"""
Stripe service
Handles all Stripe API interactions
"""

from typing import Any, Dict, Optional

import stripe
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.organization import Organization
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, "STRIPE_SECRET_KEY") else None


class StripeService:
    """Service for Stripe operations"""

    def __init__(self):
        if not stripe.api_key:
            raise ValueError("STRIPE_SECRET_KEY not configured")

    async def create_customer(
        self, email: str, name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.Customer:
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(email=email, name=name, metadata=metadata or {})
            return customer
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def get_customer(self, customer_id: str) -> stripe.Customer:
        """Get Stripe customer"""
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer not found: {str(e)}"
            )

    async def update_customer(self, customer_id: str, **kwargs) -> stripe.Customer:
        """Update Stripe customer"""
        try:
            return stripe.Customer.modify(customer_id, **kwargs)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None,
    ) -> stripe.Subscription:
        """Create Stripe subscription"""
        try:
            params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"],
            }

            if payment_method_id:
                params["default_payment_method"] = payment_method_id

            if trial_days:
                params["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**params)
            return subscription
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def get_subscription(self, subscription_id: str) -> stripe.Subscription:
        """Get Stripe subscription"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscription not found: {str(e)}"
            )

    async def update_subscription(self, subscription_id: str, **kwargs) -> stripe.Subscription:
        """Update Stripe subscription"""
        try:
            return stripe.Subscription.modify(subscription_id, **kwargs)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def cancel_subscription(
        self, subscription_id: str, at_period_end: bool = True
    ) -> stripe.Subscription:
        """Cancel Stripe subscription"""
        try:
            if at_period_end:
                return stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                return stripe.Subscription.delete(subscription_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> stripe.billing_portal.Session:
        """Create Stripe billing portal session"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=return_url
            )
            return session
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: Optional[int] = None,
    ) -> stripe.checkout.Session:
        """Create Stripe checkout session"""
        try:
            params = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
            }

            if trial_days:
                params["subscription_data"] = {"trial_period_days": trial_days}

            session = stripe.checkout.Session.create(**params)
            return session
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stripe error: {str(e)}"
            )

    async def construct_webhook_event(
        self, payload: bytes, signature: str, webhook_secret: str
    ) -> stripe.Event:
        """Construct and verify Stripe webhook event"""
        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
            return event
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
