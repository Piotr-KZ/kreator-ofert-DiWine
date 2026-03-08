"""
Base HTTP Client — retry, logging, error handling.

Wszystkie klienty dziedzicza po BaseHTTPClient.

Uzycie:
    client = BaseHTTPClient(
        base_url="https://api.fakturownia.pl",
        default_headers={"Authorization": f"Token {token}"},
    )
    response = await client.get("/invoices.json")
    response = await client.post("/invoices.json", json=data)
"""

import logging
import httpx
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseHTTPClient:
    """Bazowy klient HTTP z retry i error handling."""

    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

    async def get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: Dict = None) -> Dict[str, Any]:
        return await self._request("POST", path, json=json)

    async def put(self, path: str, json: Dict = None) -> Dict[str, Any]:
        return await self._request("PUT", path, json=json)

    async def delete(self, path: str) -> Dict[str, Any]:
        return await self._request("DELETE", path)

    async def _request(
        self, method: str, path: str, **kwargs
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method, url, headers=self.default_headers, **kwargs
                    )
                    response.raise_for_status()
                    return response.json() if response.content else {}
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP {e.response.status_code} for {method} {url} (attempt {attempt+1})")
                last_error = e
                if e.response.status_code < 500:
                    raise  # 4xx — nie retryuj
            except Exception as e:
                logger.warning(f"Request error {method} {url} (attempt {attempt+1}): {e}")
                last_error = e

        raise last_error or Exception(f"Request failed after {self.max_retries + 1} attempts")
