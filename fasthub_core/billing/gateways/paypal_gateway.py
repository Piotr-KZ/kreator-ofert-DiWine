"""
PayPal Gateway — implementacja PaymentGateway dla PayPal.

~5% polskiego rynku (miedzynarodowy).
Obsluguje: PayPal balance, karty przez PayPal.
PayPal MA natywne subskrypcje (Billing Plans) — RecurringManager NIE jest potrzebny.
Flow: create order -> redirect -> capture.
"""

import logging
from typing import Any, Dict, List, Optional

from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, PaymentStatus, WebhookResult,
)

logger = logging.getLogger(__name__)


class PayPalGateway(PaymentGateway):

    def __init__(self):
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            self._client_id = getattr(settings, "PAYPAL_CLIENT_ID", None)
            self._client_secret = getattr(settings, "PAYPAL_CLIENT_SECRET", None)
            self._sandbox = getattr(settings, "PAYPAL_SANDBOX", True)
        except Exception:
            self._client_id = None
            self._client_secret = None
            self._sandbox = True

    @property
    def gateway_id(self) -> str:
        return "paypal"

    @property
    def display_name(self) -> str:
        return "PayPal"

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def _get_client(self):
        from fasthub_core.clients.paypal_client import PayPalClient
        return PayPalClient(
            client_id=self._client_id,
            client_secret=self._client_secret,
            sandbox=self._sandbox,
        )

    def get_payment_methods(self) -> List[PaymentMethod]:
        return [
            PaymentMethod(id="paypal", name="PayPal", gateway_id="paypal"),
            PaymentMethod(id="card", name="Karta przez PayPal", gateway_id="paypal"),
        ]

    async def create_payment(
        self, amount, currency, description, return_url,
        cancel_url="", method=None, metadata=None,
    ) -> PaymentResult:
        try:
            client = self._get_client()
            amount_str = f"{amount / 100:.2f}"

            result = await client.create_order(
                amount=amount_str,
                currency=currency.upper(),
                description=description,
                return_url=return_url,
                cancel_url=cancel_url or return_url,
            )

            order_id = result.get("id", "")
            links = result.get("links", [])
            approval_url = ""
            for link in links:
                if link.get("rel") == "approve":
                    approval_url = link.get("href", "")
                    break

            return PaymentResult(
                success=bool(approval_url),
                payment_id=order_id,
                payment_url=approval_url,
                gateway_id="paypal",
                raw_response=result,
            )
        except Exception as e:
            logger.error(f"PayPal create_payment error: {e}")
            return PaymentResult(success=False, gateway_id="paypal", error=str(e))

    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        try:
            client = self._get_client()
            result = await client.get_order(payment_id)
            status = result.get("status", "").upper()

            status_map = {
                "COMPLETED": PaymentStatus.completed,
                "APPROVED": PaymentStatus.processing,
                "CREATED": PaymentStatus.pending,
                "VOIDED": PaymentStatus.canceled,
            }
            return status_map.get(status, PaymentStatus.pending)
        except Exception as e:
            logger.error(f"PayPal verify error: {e}")
            return PaymentStatus.failed

    async def handle_webhook(self, payload, headers) -> WebhookResult:
        try:
            import json
            data = json.loads(payload)

            event_type = data.get("event_type", "")
            resource = data.get("resource", {})
            order_id = resource.get("id", "")

            status_map = {
                "CHECKOUT.ORDER.APPROVED": PaymentStatus.processing,
                "PAYMENT.CAPTURE.COMPLETED": PaymentStatus.completed,
                "PAYMENT.CAPTURE.DENIED": PaymentStatus.failed,
                "PAYMENT.CAPTURE.REFUNDED": PaymentStatus.refunded,
                "BILLING.SUBSCRIPTION.ACTIVATED": PaymentStatus.completed,
                "BILLING.SUBSCRIPTION.CANCELLED": PaymentStatus.canceled,
            }

            custom_id = resource.get("custom_id", "")
            purchase_units = resource.get("purchase_units", [])
            if purchase_units:
                custom_id = purchase_units[0].get("custom_id", custom_id)

            return WebhookResult(
                status="processed",
                event_type=event_type,
                payment_id=order_id,
                payment_status=status_map.get(event_type),
                tenant_id=custom_id,
                metadata={"event_type": event_type},
            )
        except Exception as e:
            logger.error(f"PayPal webhook error: {e}")
            return WebhookResult(status="error", event_type="paypal_error")

    async def create_subscription(
        self, plan_id, amount, currency, interval,
        metadata=None, return_url="", cancel_url="",
    ) -> PaymentResult:
        """PayPal MA natywne subskrypcje — Billing Plans."""
        try:
            client = self._get_client()
            result = await client.create_subscription(
                plan_id=plan_id,
                return_url=return_url,
                cancel_url=cancel_url or return_url,
            )

            sub_id = result.get("id", "")
            links = result.get("links", [])
            approval_url = ""
            for link in links:
                if link.get("rel") == "approve":
                    approval_url = link.get("href", "")
                    break

            return PaymentResult(
                success=bool(approval_url),
                payment_id=sub_id,
                payment_url=approval_url,
                gateway_id="paypal",
                raw_response=result,
            )
        except Exception as e:
            logger.error(f"PayPal create_subscription error: {e}")
            return PaymentResult(success=False, gateway_id="paypal", error=str(e))

    async def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            client = self._get_client()
            await client.cancel_subscription(subscription_id)
            return True
        except Exception as e:
            logger.error(f"PayPal cancel_subscription error: {e}")
            return False

    async def refund_payment(self, payment_id: str, amount=None) -> bool:
        logger.warning("PayPal refunds: use PayPal dashboard or extend client")
        return False
