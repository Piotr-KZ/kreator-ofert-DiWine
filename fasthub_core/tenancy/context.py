"""
Tenant Context — ContextVar dla izolacji multi-tenancy.

ContextVar jest async-safe: każdy request ma własny kontekst.
Middleware ustawia tenant na początku requestu, czyści na końcu.

Użycie w serwisach:
    from fasthub_core.tenancy import get_current_tenant_id

    tenant_id = get_current_tenant_id()  # UUID organizacji lub None

Użycie w query:
    from fasthub_core.tenancy import get_current_tenant_id

    query = select(Process).where(Process.organization_id == get_current_tenant_id())
"""

import logging
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class TenantContext:
    """
    Dane tenanta w bieżącym request.

    Atrybuty:
        tenant_id: UUID organizacji
        tenant_slug: slug organizacji (np. "moja-firma")
        tenant_name: nazwa organizacji
        user_id: UUID użytkownika
        user_role: rola w organizacji ("admin", "viewer")
    """
    tenant_id: UUID
    tenant_slug: str = ""
    tenant_name: str = ""
    user_id: Optional[UUID] = None
    user_role: str = ""


# ContextVar — async-safe, per-request
_tenant_context: ContextVar[Optional[TenantContext]] = ContextVar(
    "tenant_context", default=None
)


def get_current_tenant() -> Optional[TenantContext]:
    """
    Pobierz pełny kontekst tenanta.

    Returns:
        TenantContext lub None (jeśli request bez auth, np. /health, /login)
    """
    return _tenant_context.get()


def get_current_tenant_id() -> Optional[UUID]:
    """
    Pobierz UUID tenanta (shortcut).

    Returns:
        UUID organizacji lub None

    Użycie:
        query = select(X).where(X.organization_id == get_current_tenant_id())
    """
    ctx = _tenant_context.get()
    return ctx.tenant_id if ctx else None


def set_current_tenant(context: TenantContext) -> None:
    """Ustaw kontekst tenanta (wywoływane przez TenantMiddleware)."""
    _tenant_context.set(context)
    logger.debug(f"Tenant context set: {context.tenant_id} ({context.tenant_slug})")


def clear_tenant_context() -> None:
    """Wyczyść kontekst tenanta (wywoływane po request)."""
    _tenant_context.set(None)
