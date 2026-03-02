"""
Stripe Client — wrapper na Stripe SDK.

Uzywany przez:
- Billing (fasthub_core) — checkout, portal, webhook verification

Thin wrapper — glownie po to zeby:
1. Trzymac import stripe w jednym miejscu
2. Miec spojny error handling
3. Moc zamockowac w testach
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class StripeClient:
    """Wrapper na Stripe SDK."""

    def __init__(self, api_key: str = None):
        import stripe
        if api_key:
            self.api_key = api_key
        else:
            from fasthub_core.config import get_settings
            self.api_key = get_settings().STRIPE_SECRET_KEY
        stripe.api_key = self.api_key
        self._stripe = stripe

    @classmethod
    def from_config(cls) -> "StripeClient":
        return cls()

    def create_checkout_session(self, **kwargs) -> Dict[str, Any]:
        session = self._stripe.checkout.Session.create(**kwargs)
        return {"session_id": session.id, "url": session.url}

    def create_portal_session(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        session = self._stripe.billing_portal.Session.create(
            customer=customer_id, return_url=return_url,
        )
        return {"url": session.url}

    def construct_webhook_event(self, payload: bytes, sig_header: str, secret: str):
        return self._stripe.Webhook.construct_event(payload, sig_header, secret)

    def create_customer(self, **kwargs):
        return self._stripe.Customer.create(**kwargs)
