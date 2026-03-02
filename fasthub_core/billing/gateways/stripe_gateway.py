"""
Stripe Gateway — implementacja PaymentGateway dla Stripe.

Wzorzec dla pozostalych bramek (PayU, Tpay, P24 — Brief 20).
"""

import logging
from typing import Any, Dict, List, Optional

from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, PaymentStatus, WebhookResult,
)

logger = logging.getLogger(__name__)


class StripeGateway(PaymentGateway):

    def __init__(self, api_key: str = None, webhook_secret: str = None):
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            self._api_key = api_key or getattr(settings, "STRIPE_SECRET_KEY", None)
            self._webhook_secret = webhook_secret or getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
        except Exception:
            self._api_key = api_key
            self._webhook_secret = webhook_secret

    @property
    def gateway_id(self) -> str:
        return "stripe"

    @property
    def display_name(self) -> str:
        return "Stripe"

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _stripe(self):
        import stripe
        stripe.api_key = self._api_key
        return stripe

    def get_payment_methods(self) -> List[PaymentMethod]:
        return [
            PaymentMethod(id="card", name="Karta platnicza", gateway_id="stripe", icon=""),
            PaymentMethod(id="blik", name="BLIK", gateway_id="stripe", icon=""),
            PaymentMethod(id="google_pay", name="Google Pay", gateway_id="stripe", icon=""),
            PaymentMethod(id="apple_pay", name="Apple Pay", gateway_id="stripe", icon=""),
        ]

    async def create_payment(
        self, amount, currency, description, return_url,
        cancel_url="", method=None, metadata=None,
    ) -> PaymentResult:
        try:
            stripe = self._stripe()
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[{
                    "price_data": {
                        "currency": currency.lower(),
                        "unit_amount": amount,
                        "product_data": {"name": description},
                    },
                    "quantity": 1,
                }],
                success_url=return_url,
                cancel_url=cancel_url or return_url,
                metadata=metadata or {},
            )
            return PaymentResult(
                success=True,
                payment_id=session.id,
                payment_url=session.url,
                gateway_id="stripe",
                raw_response={"session_id": session.id},
            )
        except Exception as e:
            logger.error(f"Stripe create_payment error: {e}")
            return PaymentResult(success=False, gateway_id="stripe", error=str(e))

    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        try:
            stripe = self._stripe()
            session = stripe.checkout.Session.retrieve(payment_id)
            status_map = {
                "complete": PaymentStatus.completed,
                "expired": PaymentStatus.canceled,
                "open": PaymentStatus.pending,
            }
            return status_map.get(session.status, PaymentStatus.pending)
        except Exception as e:
            logger.error(f"Stripe verify error: {e}")
            return PaymentStatus.failed

    async def handle_webhook(self, payload, headers) -> WebhookResult:
        """Obsluga webhookow Stripe."""
        try:
            stripe = self._stripe()
            sig_header = headers.get("stripe-signature", "")

            event = stripe.Webhook.construct_event(
                payload, sig_header, self._webhook_secret
            )

            event_type = event["type"]
            data = event["data"]["object"]

            status_map = {
                "checkout.session.completed": PaymentStatus.completed,
                "invoice.payment_succeeded": PaymentStatus.completed,
                "invoice.payment_failed": PaymentStatus.failed,
                "customer.subscription.deleted": PaymentStatus.canceled,
            }

            return WebhookResult(
                status="processed",
                event_type=event_type,
                payment_id=data.get("id", ""),
                payment_status=status_map.get(event_type),
                tenant_id=data.get("metadata", {}).get("tenant_id", "unknown"),
                metadata=data.get("metadata", {}),
            )
        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            return WebhookResult(status="error", event_type="stripe_error")

    async def create_subscription(
        self, plan_id, amount, currency, interval,
        metadata=None, return_url="", cancel_url="",
    ) -> PaymentResult:
        try:
            stripe = self._stripe()
            interval_map = {"monthly": "month", "yearly": "year"}

            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{
                    "price_data": {
                        "currency": currency.lower(),
                        "unit_amount": amount,
                        "recurring": {"interval": interval_map.get(interval, "month")},
                        "product_data": {"name": f"Plan {plan_id}"},
                    },
                    "quantity": 1,
                }],
                success_url=return_url,
                cancel_url=cancel_url or return_url,
                metadata=metadata or {},
            )
            return PaymentResult(
                success=True,
                payment_id=session.id,
                payment_url=session.url,
                gateway_id="stripe",
            )
        except Exception as e:
            logger.error(f"Stripe subscription error: {e}")
            return PaymentResult(success=False, gateway_id="stripe", error=str(e))

    async def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            stripe = self._stripe()
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            logger.error(f"Stripe cancel subscription error: {e}")
            return False

    async def refund_payment(self, payment_id: str, amount=None) -> bool:
        try:
            stripe = self._stripe()
            kwargs = {"payment_intent": payment_id}
            if amount:
                kwargs["amount"] = amount
            stripe.Refund.create(**kwargs)
            return True
        except Exception as e:
            logger.error(f"Stripe refund error: {e}")
            return False
