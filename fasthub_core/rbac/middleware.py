"""
FastAPI dependency do sprawdzania uprawnień w endpointach.

Użycie:
  @router.get("/processes", dependencies=[Depends(require_permission("processes.view"))])
  async def list_processes(...):
      ...

  # Lub z dostępem do usera:
  @router.post("/processes")
  async def create_process(user = Depends(require_permission("processes.create"))):
      ...
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.db.session import get_db
from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.rbac.service import RBACService


def require_permission(permission: str):
    """
    Factory function — tworzy dependency które sprawdza uprawnienie.

    Parametr permission: np. "processes.edit", "billing.change_plan"

    Logika:
    1. Pobierz zalogowanego usera (z JWT tokenu)
    2. Pobierz organization_id z headera X-Organization-Id lub z tokenu
    3. Sprawdź czy user ma permission w tej organizacji
    4. Jeśli nie — 403 Forbidden
    5. Jeśli tak — zwróć usera
    """
    async def _check_permission(
        request: Request,
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        # Pobierz organization_id — z headera lub z tokenu
        org_id = request.headers.get("X-Organization-Id")
        if not org_id:
            org_id = getattr(current_user, 'organization_id', None)

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brak X-Organization-Id header"
            )

        # Super Admin omija sprawdzanie uprawnień
        if getattr(current_user, 'is_superadmin', False):
            return current_user

        # Sprawdź uprawnienie w RBAC
        rbac = RBACService(db)
        has_permission = await rbac.check_permission(
            user_id=current_user.id,
            organization_id=org_id,
            permission=permission,
        )

        if has_permission:
            return current_user

        # Fallback: sprawdź stary system Member.role
        # Jeśli user ma ADMIN w starym systemie → traktuj jak Owner (wszystkie uprawnienia)
        # Jeśli user ma VIEWER → traktuj jak Member (podstawowe uprawnienia)
        try:
            from sqlalchemy import select
            from fasthub_core.users.models import Member, MemberRole
            from fasthub_core.rbac.defaults import SYSTEM_ROLES

            result = await db.execute(
                select(Member).where(
                    Member.user_id == current_user.id,
                    Member.organization_id == org_id,
                )
            )
            member = result.scalar_one_or_none()
            if member and member.role:
                if member.role == MemberRole.ADMIN:
                    return current_user  # ADMIN = all permissions
                elif member.role == MemberRole.VIEWER:
                    member_perms = SYSTEM_ROLES.get("member", {}).get("permissions", [])
                    if permission in member_perms:
                        return current_user
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Brak uprawnienia: {permission}"
        )

    return _check_permission
