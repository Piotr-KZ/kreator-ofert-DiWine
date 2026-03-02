"""
Przelewy24 REST API Client.

Auth: Basic (merchantId + CRC key).
API: https://secure.przelewy24.pl/api/v1/
IMPORTANT: P24 REQUIRES verification after callback — without /transaction/verify the payment is NOT confirmed.
"""

import hashlib
import logging
from base64 import b64encode
from typing import Any, Dict

from fasthub_core.clients.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class P24Client(BaseHTTPClient):
    """Przelewy24 API client with Basic auth."""

    def __init__(
        self,
        merchant_id: str,
        pos_id: str,
        crc_key: str,
        sandbox: bool = True,
    ):
        base_url = "https://sandbox.przelewy24.pl" if sandbox else "https://secure.przelewy24.pl"
        super().__init__(base_url=base_url)
        self.merchant_id = merchant_id
        self.pos_id = pos_id or merchant_id
        self.crc_key = crc_key

        credentials = b64encode(f"{self.pos_id}:{self.crc_key}".encode()).decode()
        self.default_headers["Authorization"] = f"Basic {credentials}"

    async def register_transaction(
        self,
        amount: int,
        currency: str,
        description: str,
        email: str,
        return_url: str,
        notify_url: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        POST /api/v1/transaction/register — register transaction, get token.

        Returns: {"data": {"token": "..."}}
        """
        sign_str = f'{{"sessionId":"{session_id}","merchantId":{self.merchant_id},"amount":{amount},"currency":"{currency.upper()}","crc":"{self.crc_key}"}}'
        sign = hashlib.sha384(sign_str.encode("utf-8")).hexdigest()

        payload = {
            "merchantId": int(self.merchant_id),
            "posId": int(self.pos_id),
            "sessionId": session_id,
            "amount": amount,
            "currency": currency.upper(),
            "description": description,
            "email": email,
            "urlReturn": return_url,
            "urlStatus": notify_url,
            "sign": sign,
        }

        return await self.post("/api/v1/transaction/register", json=payload)

    def get_payment_url(self, token: str) -> str:
        """Build redirect URL for payment."""
        return f"{self.base_url}/trnRequest/{token}"

    async def verify_transaction(
        self,
        session_id: str,
        order_id: int,
        amount: int,
        currency: str,
    ) -> Dict[str, Any]:
        """
        PUT /api/v1/transaction/verify — REQUIRED after callback.

        Without this call, P24 does NOT confirm the payment.
        """
        sign_str = f'{{"sessionId":"{session_id}","orderId":{order_id},"amount":{amount},"currency":"{currency.upper()}","crc":"{self.crc_key}"}}'
        sign = hashlib.sha384(sign_str.encode("utf-8")).hexdigest()

        payload = {
            "merchantId": int(self.merchant_id),
            "posId": int(self.pos_id),
            "sessionId": session_id,
            "amount": amount,
            "currency": currency.upper(),
            "orderId": order_id,
            "sign": sign,
        }

        return await self.put("/api/v1/transaction/verify", json=payload)

    def verify_callback(self, body: bytes) -> bool:
        """Verify P24 callback signature."""
        try:
            import json
            data = json.loads(body)

            session_id = data.get("sessionId", "")
            merchant_id = str(data.get("merchantId", ""))
            amount = data.get("amount", 0)
            currency = data.get("currency", "PLN")
            order_id = data.get("orderId", 0)
            received_sign = data.get("sign", "")

            sign_str = f'{{"sessionId":"{session_id}","orderId":{order_id},"amount":{amount},"currency":"{currency}","crc":"{self.crc_key}"}}'
            computed = hashlib.sha384(sign_str.encode("utf-8")).hexdigest()

            return computed == received_sign
        except Exception:
            return False
