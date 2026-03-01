"""
API endpoints RBAC.
Zarządzanie rolami i uprawnieniami w organizacji.
Prefix: /api/rbac
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from fasthub_core.db.session import get_db
from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.rbac.service import RBACService
from fasthub_core.rbac.models import Role, Permission
from fasthub_core.rbac.middleware import require_permission
from fasthub_core.rbac.schemas import (
    PermissionResponse, RoleResponse, RoleCreateRequest,
    RoleUpdateRequest, AssignRoleRequest, UserPermissionsResponse,
)

router = APIRouter(prefix="/api/rbac", tags=["RBAC"])


# === PERMISSIONS ===

@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    category: Optional[str] = Query(None, description="Filtr po kategorii np. 'team', 'billing'"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista wszystkich dostępnych uprawnień"""
    rbac = RBACService(db)
    permissions = await rbac.list_permissions(category=category)
    return permissions


# === ROLES ===

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    organization_id: UUID = Query(..., description="ID organizacji"),
    current_user=Depends(require_permission("team.view_members")),
    db: AsyncSession = Depends(get_db),
):
    """Lista ról w organizacji (systemowe + custom)"""
    rbac = RBACService(db)
    roles = await rbac.list_organization_roles(organization_id)

    result = []
    for role in roles:
        perm_names = []
        for rp in role.permissions:
            if rp.permission:
                perm_names.append(rp.permission.name)
        result.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system=role.is_system,
            is_default=role.is_default,
            permissions=perm_names,
        ))

    return result


@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    organization_id: UUID = Query(..., description="ID organizacji"),
    request: RoleCreateRequest = ...,
    current_user=Depends(require_permission("team.change_roles")),
    db: AsyncSession = Depends(get_db),
):
    """Stwórz nową rolę custom w organizacji"""
    rbac = RBACService(db)
    role = await rbac.create_custom_role(
        organization_id=organization_id,
        name=request.name,
        description=request.description,
        permission_names=request.permissions,
    )
    await db.commit()
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        is_default=role.is_default,
        permissions=request.permissions,
    )


@router.put("/roles/{role_id}")
async def update_role(
    role_id: UUID,
    request: RoleUpdateRequest,
    current_user=Depends(require_permission("team.change_roles")),
    db: AsyncSession = Depends(get_db),
):
    """Aktualizuj rolę (tylko custom, nie systemowe)"""
    role = await db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rola nie znaleziona")
    if role.is_system:
        raise HTTPException(status_code=403, detail="Nie można edytować roli systemowej")

    if request.name:
        role.name = request.name
    if request.description is not None:
        role.description = request.description
    if request.permissions is not None:
        rbac = RBACService(db)
        await rbac.update_role_permissions(role_id, request.permissions)

    await db.commit()
    return {"status": "updated"}


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    current_user=Depends(require_permission("team.change_roles")),
    db: AsyncSession = Depends(get_db),
):
    """Usuń rolę custom (systemowych nie można usunąć)"""
    rbac = RBACService(db)
    try:
        deleted = await rbac.delete_role(role_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="Rola nie znaleziona")
    await db.commit()
    return {"status": "deleted"}


# === USER-ROLE ASSIGNMENTS ===

@router.post("/assign")
async def assign_role_to_user(
    request: AssignRoleRequest,
    organization_id: UUID = Query(...),
    current_user=Depends(require_permission("team.change_roles")),
    db: AsyncSession = Depends(get_db),
):
    """Przypisz rolę użytkownikowi w organizacji"""
    rbac = RBACService(db)
    result = await rbac.assign_role(
        user_id=request.user_id,
        role_id=request.role_id,
        organization_id=organization_id,
        assigned_by=current_user.id,
    )
    if result is None:
        raise HTTPException(status_code=409, detail="Użytkownik już ma tę rolę")
    await db.commit()
    return {"status": "assigned"}


@router.post("/unassign")
async def unassign_role_from_user(
    request: AssignRoleRequest,
    organization_id: UUID = Query(...),
    current_user=Depends(require_permission("team.change_roles")),
    db: AsyncSession = Depends(get_db),
):
    """Usuń rolę użytkownikowi"""
    rbac = RBACService(db)
    removed = await rbac.remove_role(
        user_id=request.user_id,
        role_id=request.role_id,
        organization_id=organization_id,
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Użytkownik nie ma tej roli")
    await db.commit()
    return {"status": "unassigned"}


# === USER PERMISSIONS CHECK ===

@router.get("/user-permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: UUID = Query(...),
    organization_id: UUID = Query(...),
    current_user=Depends(require_permission("team.view_members")),
    db: AsyncSession = Depends(get_db),
):
    """Pobierz wszystkie role i uprawnienia użytkownika w organizacji"""
    rbac = RBACService(db)
    roles = await rbac.get_user_roles(user_id, organization_id)
    permissions = await rbac.get_user_permissions(user_id, organization_id)

    role_responses = [
        RoleResponse(
            id=r["id"],
            name=r["name"],
            description=None,
            is_system=r["is_system"],
            is_default=False,
            permissions=[],
        )
        for r in roles
    ]

    return UserPermissionsResponse(
        user_id=user_id,
        organization_id=organization_id,
        roles=role_responses,
        permissions=list(permissions),
    )
