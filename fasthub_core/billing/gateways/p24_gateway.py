"""
Przelewy24 Gateway — implementacja PaymentGateway dla P24.

~20% polskiego rynku platnosci online.
Obsluguje: BLIK, karty, przelewy bankowe, Google Pay, Apple Pay.
Flow: register -> redirect -> callback -> VERIFY (obowiazkowe!).
IMPORTANT: P24 WYMAGA weryfikacji po callbacku — bez /transaction/verify platnosc NIE jest potwierdzona.
"""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, PaymentStatus, WebhookResult,
)

logger = logging.getLogger(__name__)


class P24Gateway(PaymentGateway):

    def __init__(self):
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            self._merchant_id = getattr(settings, "P24_MERCHANT_ID", None)
            self._pos_id = getattr(settings, "P24_POS_ID", None) or self._merchant_id
            self._crc_key = getattr(settings, "P24_CRC_KEY", None)
            self._sandbox = getattr(settings, "P24_SANDBOX", True)
        except Exception:
            self._merchant_id = None
            self._pos_id = None
            self._crc_key = None
            self._sandbox = True

    @property
    def gateway_id(self) -> str:
        return "p24"

    @property
    def display_name(self) -> str:
        return "Przelewy24"

    def is_configured(self) -> bool:
        return bool(self._merchant_id and self._crc_key)

    def _get_client(self):
        from fasthub_core.clients.p24_client import P24Client
        return P24Client(
            merchant_id=self._merchant_id,
            pos_id=self._pos_id or self._merchant_id,
            crc_key=self._crc_key,
            sandbox=self._sandbox,
        )

    def get_payment_methods(self) -> List[PaymentMethod]:
        return [
            PaymentMethod(id="blik", name="BLIK", gateway_id="p24"),
            PaymentMethod(id="card", name="Karta platnicza", gateway_id="p24"),
            PaymentMethod(id="transfer", name="Przelew bankowy", gateway_id="p24"),
            PaymentMethod(id="google_pay", name="Google Pay", gateway_id="p24"),
            PaymentMethod(id="apple_pay", name="Apple Pay", gateway_id="p24"),
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
            session_id = metadata.pop("session_id", str(uuid.uuid4()))

            result = await client.register_transaction(
                amount=amount,
                currency=currency,
                description=description,
                email=buyer_email,
                return_url=return_url,
                notify_url=notify_url,
                session_id=session_id,
            )

            token = result.get("data", {}).get("token", "")
            payment_url = client.get_payment_url(token) if token else ""

            return PaymentResult(
                success=bool(token),
                payment_id=session_id,
                payment_url=payment_url,
                gateway_id="p24",
                raw_response={"token": token, "session_id": session_id},
            )
        except Exception as e:
            logger.error(f"P24 create_payment error: {e}")
            return PaymentResult(success=False, gateway_id="p24", error=str(e))

    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        """P24 doesn't have a simple status check — use webhook + verify."""
        return PaymentStatus.pending

    async def handle_webhook(self, payload, headers) -> WebhookResult:
        """
        P24 callback + MANDATORY verification.

        After receiving callback, we MUST call /transaction/verify.
        Without this, the payment is NOT confirmed by P24.
        """
        try:
            client = self._get_client()
            if not client.verify_callback(payload):
                return WebhookResult(status="error", event_type="invalid_signature")

            data = json.loads(payload)
            session_id = data.get("sessionId", "")
            order_id = data.get("orderId", 0)
            amount = data.get("amount", 0)
            currency = data.get("currency", "PLN")

            # MANDATORY: verify transaction with P24
            try:
                await client.verify_transaction(
                    session_id=session_id,
                    order_id=order_id,
                    amount=amount,
                    currency=currency,
                )
                payment_status = PaymentStatus.completed
                event_type = "p24.transaction.verified"
            except Exception as verify_error:
                logger.error(f"P24 verify_transaction failed: {verify_error}")
                payment_status = PaymentStatus.failed
                event_type = "p24.transaction.verify_failed"

            return WebhookResult(
                status="processed",
                event_type=event_type,
                payment_id=session_id,
                payment_status=payment_status,
                tenant_id=data.get("statement", ""),
                metadata={"order_id": order_id, "session_id": session_id},
            )
        except Exception as e:
            logger.error(f"P24 webhook error: {e}")
            return WebhookResult(status="error", event_type="p24_error")

    async def create_subscription(
        self, plan_id, amount, currency, interval,
        metadata=None, return_url="", cancel_url="",
    ) -> PaymentResult:
        """P24 nie ma natywnych subskrypcji — RecurringManager je obsluguje."""
        return await self.create_payment(
            amount=amount,
            currency=currency,
            description=f"Subskrypcja: {plan_id}",
            return_url=return_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )

    async def cancel_subscription(self, subscription_id: str) -> bool:
        logger.info(f"P24 cancel_subscription: {subscription_id} (handled by RecurringManager)")
        return True

    async def refund_payment(self, payment_id: str, amount=None) -> bool:
        logger.warning("P24 refunds require manual processing via panel")
        return False
