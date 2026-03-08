"""
PayU REST API Client.

Auth: OAuth2 client_credentials grant (token cache).
Docs: https://developers.payu.com/en/restapi.html
"""

import hashlib
import logging
import time
from typing import Any, Dict, Optional

from fasthub_core.clients.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class PayUClient(BaseHTTPClient):
    """PayU API client with OAuth2 token caching."""

    def __init__(
        self,
        pos_id: str,
        md5_key: str,
        client_id: str,
        client_secret: str,
        sandbox: bool = True,
    ):
        base_url = "https://secure.snd.payu.com" if sandbox else "https://secure.payu.com"
        super().__init__(base_url=base_url)
        self.pos_id = pos_id
        self.md5_key = md5_key
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None
        self._token_expires: float = 0

    async def _ensure_auth(self) -> None:
        """Get or refresh OAuth2 bearer token."""
        if self._token and time.time() < self._token_expires:
            return

        import httpx

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/pl/standard/user/oauth/authorize",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()

        self._token = data["access_token"]
        self._token_expires = time.time() + data.get("expires_in", 3600) - 60
        self.default_headers["Authorization"] = f"Bearer {self._token}"

    async def create_order(
        self,
        amount: int,
        currency: str,
        description: str,
        buyer_email: str,
        return_url: str,
        notify_url: str,
        method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /api/v2_1/orders — create payment order.

        Returns: {"redirectUri": "...", "orderId": "...", "status": {...}}
        """
        await self._ensure_auth()

        payload: Dict[str, Any] = {
            "notifyUrl": notify_url,
            "continueUrl": return_url,
            "customerIp": "127.0.0.1",
            "merchantPosId": self.pos_id,
            "description": description,
            "currencyCode": currency.upper(),
            "totalAmount": str(amount),
            "buyer": {"email": buyer_email},
            "products": [
                {
                    "name": description,
                    "unitPrice": str(amount),
                    "quantity": "1",
                }
            ],
        }

        if method:
            payload["payMethods"] = {
                "payMethod": {"type": "PBL" if method == "blik" else "PBL", "value": method}
            }

        return await self.post("/api/v2_1/orders", json=payload)

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """GET /api/v2_1/orders/{order_id} — check order status."""
        await self._ensure_auth()
        return await self.get(f"/api/v2_1/orders/{order_id}")

    def verify_notification(self, body: bytes, headers: Dict[str, str]) -> bool:
        """Verify PayU notification signature (MD5 or SHA256)."""
        signature_header = headers.get("openpayu-signature", "")
        if not signature_header:
            return False

        parts = dict(
            p.split("=", 1) for p in signature_header.split(";") if "=" in p
        )
        expected_sig = parts.get("signature", "")
        algorithm = parts.get("algorithm", "MD5")

        concat = body.decode("utf-8") + self.md5_key

        if algorithm.upper() == "SHA256":
            computed = hashlib.sha256(concat.encode("utf-8")).hexdigest()
        else:
            computed = hashlib.md5(concat.encode("utf-8")).hexdigest()

        return computed == expected_sig
