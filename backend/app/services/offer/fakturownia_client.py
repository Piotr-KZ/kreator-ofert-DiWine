"""
Fakturownia API client — standalone, no base class dependency.
Uses httpx (already in project). Adapted from REFERENCJA_wzorzec.
"""

import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class FakturowniaClient:
    """Simple Fakturownia API client for invoice operations."""

    def __init__(self, api_token: str, account_name: str):
        self.api_token = api_token
        self.account_name = account_name
        self.base_url = f"https://{account_name}.fakturownia.pl"

    async def _request(self, method: str, path: str, data: dict = None, params: dict = None) -> dict:
        """Make API request with token."""
        url = f"{self.base_url}{path}"
        p = {"api_token": self.api_token}
        if params:
            p.update(params)

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                resp = await client.get(url, params=p)
            elif method == "POST":
                resp = await client.post(url, params=p, json=data)
            elif method == "PUT":
                resp = await client.put(url, params=p, json=data)
            elif method == "DELETE":
                resp = await client.delete(url, params=p)
            else:
                raise ValueError(f"Unknown method: {method}")

            if resp.status_code == 401:
                raise Exception("Fakturownia: błąd autoryzacji. Sprawdź API token.")
            if resp.status_code == 404:
                raise Exception(f"Fakturownia: nie znaleziono zasobu {path}")
            if resp.status_code >= 400:
                raise Exception(f"Fakturownia error {resp.status_code}: {resp.text[:200]}")

            return resp.json()

    # ─── INVOICES ───

    async def create_invoice(
        self,
        buyer_name: str,
        buyer_tax_no: Optional[str],
        buyer_email: Optional[str],
        positions: list[dict],
        kind: str = "proforma",
        issue_date: str = "",
        sell_date: str = "",
        payment_method: str = "transfer",
        payment_days: int = 14,
        notes: Optional[str] = None,
        buyer_street: Optional[str] = None,
        buyer_city: Optional[str] = None,
        buyer_post_code: Optional[str] = None,
    ) -> dict:
        """
        Create invoice/proforma in Fakturownia.

        Args:
            positions: [{"name": str, "quantity": int, "price_net": float, "tax": int}, ...]
            kind: "proforma", "vat", "estimate"
        """
        invoice = {
            "invoice": {
                "kind": kind,
                "buyer_name": buyer_name,
                "issue_date": issue_date,
                "sell_date": sell_date or issue_date,
                "payment_to_kind": payment_method,
                "payment_to": payment_days,
                "positions": positions,
            }
        }
        if buyer_tax_no:
            invoice["invoice"]["buyer_tax_no"] = buyer_tax_no
        if buyer_email:
            invoice["invoice"]["buyer_email"] = buyer_email
        if notes:
            invoice["invoice"]["description"] = notes
        if buyer_street:
            invoice["invoice"]["buyer_street"] = buyer_street
        if buyer_city:
            invoice["invoice"]["buyer_city"] = buyer_city
        if buyer_post_code:
            invoice["invoice"]["buyer_post_code"] = buyer_post_code

        response = await self._request("POST", "/invoices.json", data=invoice)

        return {
            "invoice_id": str(response["id"]),
            "invoice_number": response.get("number", ""),
            "status": response.get("status", ""),
            "pdf_url": f"{self.base_url}{response.get('view_url', '')}.pdf",
            "view_url": f"{self.base_url}{response.get('view_url', '')}",
            "total_net": float(response.get("total_price_net", 0)),
            "total_gross": float(response.get("total_price_gross", 0)),
            "kind": kind,
        }

    async def send_invoice_email(self, invoice_id: str, email_to: Optional[str] = None) -> dict:
        """Send invoice by email."""
        data = {}
        if email_to:
            data = {"email_to": email_to}
        return await self._request("POST", f"/invoices/{invoice_id}/send_by_email.json", data=data)

    async def get_invoice(self, invoice_id: str) -> dict:
        """Get invoice details."""
        return await self._request("GET", f"/invoices/{invoice_id}.json")

    # ─── CLIENTS ───

    async def find_or_create_client(
        self,
        name: str,
        tax_no: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        post_code: Optional[str] = None,
    ) -> dict:
        """Find client by NIP or create new."""
        # Search by NIP first
        if tax_no:
            try:
                clients = await self._request("GET", "/clients.json", params={"query": tax_no})
                if clients and len(clients) > 0:
                    c = clients[0]
                    return {"client_id": str(c["id"]), "name": c.get("name"), "found": True}
            except Exception:
                pass

        # Create new
        client_data = {"client": {"name": name, "country": "PL"}}
        if tax_no:
            client_data["client"]["tax_no"] = tax_no
        if email:
            client_data["client"]["email"] = email
        if phone:
            client_data["client"]["phone"] = phone
        if street:
            client_data["client"]["street"] = street
        if city:
            client_data["client"]["city"] = city
        if post_code:
            client_data["client"]["post_code"] = post_code

        response = await self._request("POST", "/clients.json", data=client_data)
        return {"client_id": str(response["id"]), "name": name, "found": False}

    # ─── TEST ───

    async def test_connection(self) -> dict:
        """Test API connection."""
        try:
            await self._request("GET", "/account.json")
            return {"success": True, "account": self.account_name}
        except Exception as e:
            return {"success": False, "error": str(e)}
