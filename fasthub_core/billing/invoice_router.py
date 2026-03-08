"""
Invoice Router — factory do wyboru backendu fakturowania.

Config: INVOICE_BACKEND=ksef|fakturownia|none

Uzycie:
    hook = get_invoice_hook(db)
    if hook:
        await hook.handle(event_data)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_invoice_hook(db) -> Optional[object]:
    """
    Factory — zwroc hook na podstawie config.

    Returns:
        KSeFInvoiceHook | AutoInvoiceHook | None
    """
    from fasthub_core.config import get_settings
    settings = get_settings()

    backend = getattr(settings, "INVOICE_BACKEND", "none")

    if backend == "ksef":
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        return KSeFInvoiceHook(db)
    elif backend == "fakturownia":
        from fasthub_core.billing.invoice_hook import AutoInvoiceHook
        return AutoInvoiceHook(db)
    else:
        return None
