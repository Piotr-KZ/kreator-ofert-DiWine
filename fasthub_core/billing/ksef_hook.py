"""
KSeF Invoice Hook — auto-faktura przez KSeF po udanej platnosci.

Alternatywa do AutoInvoiceHook (Fakturownia).
Config: INVOICE_BACKEND=ksef|fakturownia|none

Flow:
    1. Platnosc przechodzi (webhook)
    2. Hook pobiera dane organizacji (NIP, adres)
    3. KSeFXMLBuilder generuje XML FA(3)
    4. KSeFClient otwiera sesje -> wysyla fakture -> zamyka sesje
    5. Numer KSeF zapisany w BillingEvent
    6. UPO pobrane i zapisane
"""

import logging
from datetime import date
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class KSeFInvoiceHook:
    """
    Hook: payment_succeeded -> wystaw fakture przez KSeF.

    Uzycie:
        hook = KSeFInvoiceHook(db)
        result = await hook.handle(event_data)

    event_data powinno zawierac:
        tenant_id, plan_name, amount (w groszach), currency
    """

    def __init__(self, db):
        self.db = db

    async def handle(self, event_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Process payment_succeeded event -> create KSeF invoice.

        1. Pobierz dane kupujacego (org: NIP, nazwa)
        2. Zbuduj XML (KSeFXMLBuilder)
        3. Waliduj XML (KSeFClient.validate_invoice)
        4. Otworz sesje (KSeFClient.open_session)
        5. Wyslij fakture (KSeFClient.send_invoice)
        6. Zamknij sesje (KSeFClient.close_session)
        7. Pobierz UPO (KSeFClient.get_upo)
        """
        from fasthub_core.config import get_settings

        settings = get_settings()

        ksef_nip = getattr(settings, "KSEF_NIP", None)
        ksef_token = getattr(settings, "KSEF_AUTH_TOKEN", None)
        if not ksef_nip or not ksef_token:
            logger.debug("KSeFInvoiceHook: KSeF not configured, skipping")
            return None

        tenant_id = event_data.get("tenant_id")
        if not tenant_id:
            return None

        org = await self._get_organization(tenant_id)
        if not org:
            logger.warning(f"KSeFInvoiceHook: org {tenant_id} not found, skipping")
            return None

        org_nip = getattr(org, "nip", None)
        if not org_nip:
            logger.warning(f"KSeFInvoiceHook: org {tenant_id} has no NIP, skipping")
            return None

        try:
            from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
            from fasthub_core.clients.ksef_client import KSeFClient

            # Build XML
            builder = KSeFXMLBuilder()
            amount_gross = event_data.get("amount", 0) / 100
            amount_net = round(amount_gross / 1.23, 2)

            xml_result = builder.build(
                seller_nip=ksef_nip,
                seller_name=getattr(settings, "INVOICE_SELLER_NAME", "") or settings.APP_NAME,
                buyer_nip=org_nip,
                buyer_name=org.name,
                issue_date=date.today().isoformat(),
                sale_date=date.today().isoformat(),
                positions=[{
                    "name": event_data.get("plan_name", "Subskrypcja"),
                    "quantity": 1,
                    "unit": "szt",
                    "price_net": amount_net,
                    "vat_rate": 23,
                }],
                currency=event_data.get("currency", "PLN"),
                payment_method="przelew",
                bank_account=getattr(settings, "INVOICE_BANK_ACCOUNT", "") or "",
                system_info=settings.APP_NAME,
            )

            # Send to KSeF
            client = KSeFClient.from_config()

            # Validate
            validation = await client.validate_invoice(xml_result["invoice_xml_base64"])
            if validation.get("error"):
                logger.error(f"KSeFInvoiceHook: validation failed: {validation}")
                return {"error": "validation_failed", "details": validation}

            # Open session -> send -> close
            session = await client.open_session()
            reference = session.get("referenceNumber", "")

            ksef_number = None
            try:
                invoice_result = await client.send_invoice(
                    reference, xml_result["invoice_xml_base64"]
                )
                ksef_number = invoice_result.get("elementReferenceNumber")
            finally:
                if reference:
                    await client.close_session(reference)

            # Get UPO
            upo = None
            if reference:
                try:
                    upo = await client.get_upo(reference)
                except Exception:
                    logger.debug("KSeFInvoiceHook: UPO not ready yet")

            logger.info(
                f"KSeFInvoiceHook: invoice sent for org {tenant_id}, "
                f"KSeF number: {ksef_number}"
            )

            return {
                "ksef_number": ksef_number,
                "reference_number": reference,
                "upo": upo,
                "xml_summary": xml_result["summary"],
            }

        except Exception as e:
            logger.error(f"KSeFInvoiceHook: failed for org {tenant_id}: {e}")
            return {"error": str(e)}

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
