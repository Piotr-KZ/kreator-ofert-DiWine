"""
Fakturownia HTTP Client — czyste wywolania API.

Uzywany przez:
- Provider Fakturownia (AutoFlow) — token KLIENTA
- Billing hook (fasthub_core) — token NASZ firmowy

Uzycie:
    # Kontekst 1: Provider (token klienta)
    client = FakturowniaClient(account="klient-firma", api_token="abc123")

    # Kontekst 2: Billing (nasz token z .env)
    client = FakturowniaClient.from_config()

    invoice = await client.create_invoice(invoice_data={...})
    invoices = await client.list_invoices(period="this_month")
"""

import logging
from typing import Any, Dict, List, Optional

from fasthub_core.clients.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class FakturowniaClient(BaseHTTPClient):
    """Klient API Fakturownia.pl."""

    def __init__(self, account: str, api_token: str):
        self.account = account
        self.api_token = api_token
        super().__init__(
            base_url=f"https://{account}.fakturownia.pl",
            default_headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    @classmethod
    def from_config(cls) -> "FakturowniaClient":
        """Stworz klienta z config (.env) — NASZ firmowy token."""
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            account = getattr(settings, "FAKTUROWNIA_ACCOUNT", None)
            token = getattr(settings, "FAKTUROWNIA_API_TOKEN", None)
            if not account or not token:
                raise ValueError("FAKTUROWNIA_ACCOUNT and FAKTUROWNIA_API_TOKEN required")
            return cls(account=account, api_token=token)
        except Exception as e:
            raise ValueError(f"Fakturownia config error: {e}")

    def _with_token(self, params: dict = None) -> dict:
        """Dodaj api_token do parametrow."""
        params = params or {}
        params["api_token"] = self.api_token
        return params

    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Utworz fakture."""
        return await self.post(
            "/invoices.json",
            json={"invoice": invoice_data, "api_token": self.api_token},
        )

    async def get_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Pobierz fakture po ID."""
        return await self.get(f"/invoices/{invoice_id}.json", params=self._with_token())

    async def list_invoices(
        self, page: int = 1, period: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista faktur. period: "this_month", "last_month", "this_year"."""
        params = self._with_token({"page": page})
        if period:
            params["period"] = period
        return await self.get("/invoices.json", params=params)

    async def send_invoice_by_email(self, invoice_id: int) -> Dict[str, Any]:
        """Wyslij fakture emailem do kupujacego."""
        return await self.post(
            f"/invoices/{invoice_id}/send_by_email.json",
            json={"api_token": self.api_token},
        )
