"""
AutoInvoiceHook — automatic invoice generation after payment success.

Hooks into payment_succeeded event, creates invoice via Fakturownia API.
Optional — does nothing if FAKTUROWNIA_* not configured.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AutoInvoiceHook:
    """
    After successful payment → issue invoice via Fakturownia.

    Usage:
        hook = AutoInvoiceHook(db)
        result = await hook.handle(event_data)
    """

    def __init__(self, db):
        self.db = db

    async def handle(self, event_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Process payment_succeeded event.

        event_data should contain:
            tenant_id, plan_name, amount (in grosz/cents), currency
        """
        from fasthub_core.config import get_settings
        settings = get_settings()

        api_token = getattr(settings, "FAKTUROWNIA_API_TOKEN", None)
        account = getattr(settings, "FAKTUROWNIA_ACCOUNT", None)
        if not api_token or not account:
            logger.debug("AutoInvoiceHook: Fakturownia not configured, skipping")
            return None

        tenant_id = event_data.get("tenant_id")
        if not tenant_id:
            return None

        org = await self._get_organization(tenant_id)
        if not org or not org.nip:
            logger.warning(f"AutoInvoiceHook: org {tenant_id} has no NIP, skipping invoice")
            return None

        try:
            import httpx

            amount_gross = event_data.get("amount", 0) / 100
            invoice_data = {
                "api_token": api_token,
                "invoice": {
                    "kind": "vat",
                    "number": None,  # auto-numbered by Fakturownia
                    "buyer_name": org.name,
                    "buyer_tax_no": org.nip,
                    "buyer_email": org.email,
                    "buyer_street": org.billing_street or "",
                    "buyer_city": org.billing_city or "",
                    "buyer_post_code": org.billing_postal_code or "",
                    "buyer_country": org.billing_country or "PL",
                    "positions": [{
                        "name": event_data.get("plan_name", "Subskrypcja"),
                        "quantity": 1,
                        "total_price_gross": str(amount_gross),
                        "tax": "23",
                    }],
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://{account}.fakturownia.pl/invoices.json",
                    json=invoice_data,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

            logger.info(f"AutoInvoiceHook: invoice created for org {tenant_id}: {result.get('id')}")
            return result

        except Exception as e:
            logger.error(f"AutoInvoiceHook: failed for org {tenant_id}: {e}")
            return None

    async def _get_organization(self, tenant_id: str):
        """Load organization by ID."""
        try:
            from uuid import UUID as PyUUID
            from sqlalchemy import select
            from fasthub_core.users.models import Organization

            org_uuid = PyUUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
            result = await self.db.execute(
                select(Organization).where(Organization.id == org_uuid)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
