"""
Tenant-scoped query helpers.

Zamiast ręcznego:
    query = select(Process).where(Process.organization_id == tenant_id)

Użyj:
    query = tenant_query(select(Process), Process.organization_id)
    # automatycznie dodaje WHERE organization_id = current_tenant_id

Lub dekorator:
    @tenant_scoped("organization_id")
    async def list_processes(db):
        return await db.execute(select(Process))
"""

import logging
from typing import Any

from sqlalchemy import Select

from fasthub_core.tenancy.context import get_current_tenant_id

logger = logging.getLogger(__name__)


def tenant_query(query: Select, tenant_column: Any) -> Select:
    """
    Dodaj filtr tenant do query.

    Args:
        query: SQLAlchemy Select
        tenant_column: kolumna do filtrowania (np. Process.organization_id)

    Returns:
        Query z dodanym WHERE tenant_column = current_tenant_id

    Raises:
        ValueError: jeśli brak tenant context

    Przykład:
        from fasthub_core.tenancy import tenant_query

        query = tenant_query(
            select(Process).order_by(Process.created_at.desc()),
            Process.organization_id,
        )
        result = await db.execute(query)
    """
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        raise ValueError("No tenant context — cannot scope query. Use require_tenant dependency.")

    return query.where(tenant_column == tenant_id)


def optional_tenant_query(query: Select, tenant_column: Any) -> Select:
    """
    Dodaj filtr tenant jeśli jest kontekst. Bez kontekstu — zwróć query bez zmian.

    Przydatne dla endpointów które działają z i bez auth (np. publiczne listy).
    """
    tenant_id = get_current_tenant_id()
    if tenant_id is not None:
        return query.where(tenant_column == tenant_id)
    return query
