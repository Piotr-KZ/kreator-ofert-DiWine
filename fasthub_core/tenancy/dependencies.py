"""
Tenant Dependencies — FastAPI Depends.

Użycie:
    @router.get("/data")
    async def get_data(tenant: TenantContext = Depends(require_tenant)):
        # tenant.tenant_id gwarantowane

    @router.post("/settings")
    async def update(tenant: TenantContext = Depends(require_tenant_admin)):
        # tenant.user_role == "admin" gwarantowane
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.db.session import get_db
from fasthub_core.tenancy.context import TenantContext, get_current_tenant


async def require_tenant() -> TenantContext:
    """
    Wymagaj tenant context.

    Raises:
        HTTPException 401 jeśli brak tenanta (nie zalogowany lub brak organizacji)
    """
    tenant = get_current_tenant()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context required. User must belong to an organization.",
        )
    return tenant


async def require_tenant_admin() -> TenantContext:
    """
    Wymagaj tenant context z rolą admin.

    Raises:
        HTTPException 403 jeśli user nie jest adminem organizacji
    """
    tenant = await require_tenant()
    if tenant.user_role not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin privileges required.",
        )
    return tenant


async def get_tenant_db(
    tenant: TenantContext = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """
    DB session z gwarantowanym tenant context.

    Convenience dependency — daje sesję DB wiedząc że tenant istnieje.
    Serwis może pobrać tenant_id z get_current_tenant_id().
    """
    return db
