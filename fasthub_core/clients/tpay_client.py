"""
Tpay (Autopay) REST API Client.

Auth: OAuth2 client_credentials grant (token cache).
API: https://api.tpay.com/ (new REST API)
"""

import hashlib
import logging
import time
from typing import Any, Dict, Optional

from fasthub_core.clients.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class TpayClient(BaseHTTPClient):
    """Tpay API client with OAuth2 token caching."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        security_code: str,
        sandbox: bool = True,
    ):
        base_url = "https://openapi.sandbox.tpay.com" if sandbox else "https://openapi.tpay.com"
        super().__init__(base_url=base_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self.security_code = security_code
        self._token: Optional[str] = None
        self._token_expires: float = 0

    async def _ensure_auth(self) -> None:
        """Get or refresh OAuth2 bearer token."""
        if self._token and time.time() < self._token_expires:
            return

        import httpx

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/oauth/auth",
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()

        self._token = data["access_token"]
        self._token_expires = time.time() + data.get("expires_in", 7200) - 60
        self.default_headers["Authorization"] = f"Bearer {self._token}"

    async def create_transaction(
        self,
        amount: float,
        description: str,
        payer_email: str,
        return_url: str,
        notify_url: str,
        method: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        POST /transactions — create transaction.

        Returns: {"transactionId": "...", "transactionPaymentUrl": "..."}
        """
        await self._ensure_auth()

        payload: Dict[str, Any] = {
            "amount": amount,
            "description": description,
            "payer": {"email": payer_email},
            "callbacks": {
                "payerUrls": {"success": return_url, "error": return_url},
                "notification": {"url": notify_url},
            },
        }

        if method:
            payload["pay"] = {"groupId": method}

        return await self.post("/transactions", json=payload)

    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """GET /transactions/{id} — check transaction status."""
        await self._ensure_auth()
        return await self.get(f"/transactions/{transaction_id}")

    def verify_callback(self, body: bytes) -> bool:
        """Verify Tpay callback checksum using security code."""
        try:
            import json
            data = json.loads(body)
            received_md5 = data.get("md5sum", "")

            tr_id = str(data.get("tr_id", ""))
            tr_amount = str(data.get("tr_amount", ""))
            tr_crc = str(data.get("tr_crc", ""))

            concat = tr_id + tr_amount + tr_crc + self.security_code
            computed = hashlib.md5(concat.encode("utf-8")).hexdigest()

            return computed == received_md5
        except Exception:
            return False
