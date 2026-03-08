"""
Tpay (Autopay) Gateway — implementacja PaymentGateway dla Tpay.

~25% polskiego rynku platnosci online.
Obsluguje: BLIK, karty, przelewy bankowe, Google Pay, Apple Pay.
Flow: redirect — tworzymy transakcje -> dostajemy URL -> klient placi -> callback.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, PaymentStatus, WebhookResult,
)

logger = logging.getLogger(__name__)


class TpayGateway(PaymentGateway):

    def __init__(self):
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            self._client_id = getattr(settings, "TPAY_CLIENT_ID", None)
            self._client_secret = getattr(settings, "TPAY_CLIENT_SECRET", None)
            self._security_code = getattr(settings, "TPAY_SECURITY_CODE", None)
            self._sandbox = getattr(settings, "TPAY_SANDBOX", True)
        except Exception:
            self._client_id = None
            self._client_secret = None
            self._security_code = None
            self._sandbox = True

    @property
    def gateway_id(self) -> str:
        return "tpay"

    @property
    def display_name(self) -> str:
        return "Tpay"

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret and self._security_code)

    def _get_client(self):
        from fasthub_core.clients.tpay_client import TpayClient
        return TpayClient(
            client_id=self._client_id,
            client_secret=self._client_secret,
            security_code=self._security_code,
            sandbox=self._sandbox,
        )

    def get_payment_methods(self) -> List[PaymentMethod]:
        return [
            PaymentMethod(id="blik", name="BLIK", gateway_id="tpay"),
            PaymentMethod(id="card", name="Karta platnicza", gateway_id="tpay"),
            PaymentMethod(id="transfer", name="Przelew bankowy", gateway_id="tpay"),
            PaymentMethod(id="google_pay", name="Google Pay", gateway_id="tpay"),
            PaymentMethod(id="apple_pay", name="Apple Pay", gateway_id="tpay"),
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

            amount_decimal = amount / 100.0

            result = await client.create_transaction(
                amount=amount_decimal,
                description=description,
                payer_email=buyer_email,
                return_url=return_url,
                notify_url=notify_url,
            )

            payment_url = result.get("transactionPaymentUrl", "")
            transaction_id = result.get("transactionId", result.get("title", ""))

            return PaymentResult(
                success=bool(payment_url),
                payment_id=str(transaction_id),
                payment_url=payment_url,
                gateway_id="tpay",
                raw_response=result,
            )
        except Exception as e:
            logger.error(f"Tpay create_payment error: {e}")
            return PaymentResult(success=False, gateway_id="tpay", error=str(e))

    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        try:
            client = self._get_client()
            result = await client.get_transaction(payment_id)
            status = result.get("status", "").lower()

            status_map = {
                "correct": PaymentStatus.completed,
                "paid": PaymentStatus.completed,
                "pending": PaymentStatus.pending,
                "error": PaymentStatus.failed,
                "refund": PaymentStatus.refunded,
            }
            return status_map.get(status, PaymentStatus.pending)
        except Exception as e:
            logger.error(f"Tpay verify error: {e}")
            return PaymentStatus.failed

    async def handle_webhook(self, payload, headers) -> WebhookResult:
        try:
            client = self._get_client()
            if not client.verify_callback(payload):
                return WebhookResult(status="error", event_type="invalid_checksum")

            data = json.loads(payload)
            tr_id = str(data.get("tr_id", ""))
            tr_status = data.get("tr_status", "").upper()
            tr_crc = data.get("tr_crc", "")

            status_map = {
                "TRUE": PaymentStatus.completed,
                "FALSE": PaymentStatus.failed,
            }

            return WebhookResult(
                status="processed",
                event_type=f"tpay.transaction.{'completed' if tr_status == 'TRUE' else 'failed'}",
                payment_id=tr_id,
                payment_status=status_map.get(tr_status, PaymentStatus.pending),
                tenant_id=tr_crc,
                metadata={"tr_crc": tr_crc},
            )
        except Exception as e:
            logger.error(f"Tpay webhook error: {e}")
            return WebhookResult(status="error", event_type="tpay_error")

    async def create_subscription(
        self, plan_id, amount, currency, interval,
        metadata=None, return_url="", cancel_url="",
    ) -> PaymentResult:
        """Tpay nie ma natywnych subskrypcji — RecurringManager je obsluguje."""
        return await self.create_payment(
            amount=amount,
            currency=currency,
            description=f"Subskrypcja: {plan_id}",
            return_url=return_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )

    async def cancel_subscription(self, subscription_id: str) -> bool:
        logger.info(f"Tpay cancel_subscription: {subscription_id} (handled by RecurringManager)")
        return True

    async def refund_payment(self, payment_id: str, amount=None) -> bool:
        try:
            client = self._get_client()
            payload = {"transactionId": payment_id}
            if amount:
                payload["amount"] = amount / 100.0
            await client.post("/transactions/refunds", json=payload)
            return True
        except Exception as e:
            logger.error(f"Tpay refund error: {e}")
            return False
