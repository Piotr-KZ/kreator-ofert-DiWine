"""
PayPal REST API Client.

Auth: OAuth2 client_credentials grant (token cache).
API: https://api-m.paypal.com/v2/
"""

import logging
import time
from base64 import b64encode
from typing import Any, Dict, Optional

from fasthub_core.clients.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class PayPalClient(BaseHTTPClient):
    """PayPal API client with OAuth2 token caching."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        sandbox: bool = True,
    ):
        base_url = "https://api-m.sandbox.paypal.com" if sandbox else "https://api-m.paypal.com"
        super().__init__(base_url=base_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None
        self._token_expires: float = 0

    async def _ensure_auth(self) -> None:
        """Get or refresh OAuth2 bearer token."""
        if self._token and time.time() < self._token_expires:
            return

        import httpx

        credentials = b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data="grant_type=client_credentials",
            )
            response.raise_for_status()
            data = response.json()

        self._token = data["access_token"]
        self._token_expires = time.time() + data.get("expires_in", 32400) - 60
        self.default_headers["Authorization"] = f"Bearer {self._token}"

    async def create_order(
        self,
        amount: str,
        currency: str,
        description: str,
        return_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """
        POST /v2/checkout/orders — create order.

        Returns: {"id": "...", "links": [...]}
        """
        await self._ensure_auth()

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": amount,
                    },
                    "description": description,
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }

        return await self.post("/v2/checkout/orders", json=payload)

    async def capture_order(self, order_id: str) -> Dict[str, Any]:
        """POST /v2/checkout/orders/{id}/capture — capture payment after approval."""
        await self._ensure_auth()
        return await self.post(f"/v2/checkout/orders/{order_id}/capture", json={})

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """GET /v2/checkout/orders/{id} — check order status."""
        await self._ensure_auth()
        return await self.get(f"/v2/checkout/orders/{order_id}")

    async def create_subscription(
        self,
        plan_id: str,
        return_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """POST /v1/billing/subscriptions — create PayPal subscription (native)."""
        await self._ensure_auth()

        payload = {
            "plan_id": plan_id,
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }

        return await self.post("/v1/billing/subscriptions", json=payload)

    async def cancel_subscription(self, subscription_id: str, reason: str = "") -> Dict[str, Any]:
        """POST /v1/billing/subscriptions/{id}/cancel — cancel subscription."""
        await self._ensure_auth()
        return await self.post(
            f"/v1/billing/subscriptions/{subscription_id}/cancel",
            json={"reason": reason or "Cancelled by user"},
        )
