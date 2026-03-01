"""
Dependency do ochrony endpointów Super Admin.
Użycie: @router.get("/admin/orgs", dependencies=[Depends(require_superadmin)])
"""

from fastapi import Depends, HTTPException, status
from fasthub_core.auth.dependencies import get_current_user


async def require_superadmin(current_user=Depends(get_current_user)):
    """
    Sprawdza czy zalogowany user jest Super Adminem.
    Jeśli nie — zwraca 403 Forbidden.
    """
    if not getattr(current_user, 'is_superadmin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dostęp tylko dla Super Admina"
        )
    return current_user
