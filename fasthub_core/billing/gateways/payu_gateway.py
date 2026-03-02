"""
PayU Gateway — implementacja PaymentGateway dla PayU.

~40% polskiego rynku platnosci online.
Obsluguje: BLIK, karty, przelewy bankowe, Google Pay, Apple Pay.
Flow: redirect — tworzymy order -> dostajemy URL -> klient placi na PayU -> notify.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, PaymentStatus, WebhookResult,
)

logger = logging.getLogger(__name__)


class PayUGateway(PaymentGateway):

    def __init__(self):
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            self._pos_id = getattr(settings, "PAYU_POS_ID", None)
            self._md5_key = getattr(settings, "PAYU_MD5_KEY", None)
            self._client_id = getattr(settings, "PAYU_CLIENT_ID", None)
            self._client_secret = getattr(settings, "PAYU_CLIENT_SECRET", None)
            self._sandbox = getattr(settings, "PAYU_SANDBOX", True)
        except Exception:
            self._pos_id = None
            self._md5_key = None
            self._client_id = None
            self._client_secret = None
            self._sandbox = True

    @property
    def gateway_id(self) -> str:
        return "payu"

    @property
    def display_name(self) -> str:
        return "PayU"

    def is_configured(self) -> bool:
        return bool(self._pos_id and self._md5_key and self._client_id and self._client_secret)

    def _get_client(self):
        from fasthub_core.clients.payu_client import PayUClient
        return PayUClient(
            pos_id=self._pos_id,
            md5_key=self._md5_key,
            client_id=self._client_id,
            client_secret=self._client_secret,
            sandbox=self._sandbox,
        )

    def get_payment_methods(self) -> List[PaymentMethod]:
        return [
            PaymentMethod(id="blik", name="BLIK", gateway_id="payu"),
            PaymentMethod(id="card", name="Karta platnicza", gateway_id="payu"),
            PaymentMethod(id="transfer", name="Przelew bankowy", gateway_id="payu"),
            PaymentMethod(id="google_pay", name="Google Pay", gateway_id="payu"),
            PaymentMethod(id="apple_pay", name="Apple Pay", gateway_id="payu"),
        ]

    async def create_payment(
        self, amount, currency, description, return_url,
        cancel_url="", method=None, metadata=None,
    ) -> PaymentResult:
        try:
            client = self._get_client()
            metadata = metadata or {}
            notify_url = metadata.pop("notify_url", return_url)
            buyer_email = metadata.pop("buyer_email", "customer@example.com")

            result = await client.create_order(
                amount=amount,
                currency=currency,
                description=description,
                buyer_email=buyer_email,
                return_url=return_url,
                notify_url=notify_url,
                method=method,
            )

            redirect_uri = result.get("redirectUri", "")
            order_id = result.get("orderId", "")

            return PaymentResult(
                success=bool(redirect_uri),
                payment_id=order_id,
                payment_url=redirect_uri,
                gateway_id="payu",
                raw_response=result,
            )
        except Exception as e:
            logger.error(f"PayU create_payment error: {e}")
            return PaymentResult(success=False, gateway_id="payu", error=str(e))

    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        try:
            client = self._get_client()
            result = await client.get_order(payment_id)
            orders = result.get("orders", [])
            if not orders:
                return PaymentStatus.pending

            status = orders[0].get("status", "").upper()
            status_map = {
                "COMPLETED": PaymentStatus.completed,
                "CANCELED": PaymentStatus.canceled,
                "PENDING": PaymentStatus.pending,
                "WAITING_FOR_CONFIRMATION": PaymentStatus.processing,
                "REJECTED": PaymentStatus.failed,
            }
            return status_map.get(status, PaymentStatus.pending)
        except Exception as e:
            logger.error(f"PayU verify error: {e}")
            return PaymentStatus.failed

    async def handle_webhook(self, payload, headers) -> WebhookResult:
        try:
            client = self._get_client()
            if not client.verify_notification(payload, headers):
                return WebhookResult(status="error", event_type="invalid_signature")

            data = json.loads(payload)
            order = data.get("order", {})
            order_id = order.get("orderId", "")
            status_str = order.get("status", "").upper()

            status_map = {
                "COMPLETED": PaymentStatus.completed,
                "CANCELED": PaymentStatus.canceled,
                "PENDING": PaymentStatus.pending,
                "WAITING_FOR_CONFIRMATION": PaymentStatus.processing,
                "REJECTED": PaymentStatus.failed,
            }

            properties = data.get("properties", [])
            metadata = {}
            for prop in properties:
                if prop.get("name") == "tenant_id":
                    metadata["tenant_id"] = prop.get("value", "")

            return WebhookResult(
                status="processed",
                event_type=f"payu.order.{status_str.lower()}",
                payment_id=order_id,
                payment_status=status_map.get(status_str, PaymentStatus.pending),
                tenant_id=metadata.get("tenant_id", ""),
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"PayU webhook error: {e}")
            return WebhookResult(status="error", event_type="payu_error")

    async def create_subscription(
        self, plan_id, amount, currency, interval,
        metadata=None, return_url="", cancel_url="",
    ) -> PaymentResult:
        """PayU nie ma natywnych subskrypcji — RecurringManager je obsluguje."""
        return await self.create_payment(
            amount=amount,
            currency=currency,
            description=f"Subskrypcja: {plan_id}",
            return_url=return_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """PayU nie ma natywnych subskrypcji — cancel via RecurringManager."""
        logger.info(f"PayU cancel_subscription: {subscription_id} (handled by RecurringManager)")
        return True

    async def refund_payment(self, payment_id: str, amount=None) -> bool:
        try:
            client = self._get_client()
            payload = {}
            if amount:
                payload["refund"] = {"description": "Refund", "amount": str(amount)}
            else:
                payload["refund"] = {"description": "Full refund"}

            await client.post(f"/api/v2_1/orders/{payment_id}/refunds", json=payload)
            return True
        except Exception as e:
            logger.error(f"PayU refund error: {e}")
            return False
