"""
API endpoints Super Admin.
WSZYSTKIE endpointy wymagają is_superadmin=True.
Prefix: /api/admin
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.admin.schemas import (
    ImpersonateRequest,
    ImpersonateResponse,
    OrganizationList,
    SystemStats,
    UserList,
)
from fasthub_core.admin.service import AdminService
from fasthub_core.auth.superadmin import require_superadmin
from fasthub_core.db.session import get_db

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    admin=Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """Globalne statystyki systemu"""
    service = AdminService(db)
    return await service.get_system_stats()


@router.get("/organizations", response_model=OrganizationList)
async def list_organizations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None, description="Szukaj po nazwie lub slug"),
    sort_by: str = Query("created_at", description="Pole sortowania"),
    sort_order: str = Query("desc", description="asc lub desc"),
    admin=Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """Lista wszystkich organizacji z metrykami"""
    service = AdminService(db)
    return await service.list_organizations(page, per_page, search, sort_by, sort_order)


@router.get("/organizations/{org_id}")
async def get_organization_detail(
    org_id: UUID,
    admin=Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """Szczegóły organizacji z listą członków"""
    service = AdminService(db)
    result = await service.get_organization_detail(org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Organizacja nie znaleziona")
    return result


@router.get("/users", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None, description="Szukaj po email lub nazwisku"),
    admin=Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """Lista wszystkich użytkowników w systemie"""
    service = AdminService(db)
    return await service.list_users(page, per_page, search)


@router.post("/impersonate", response_model=ImpersonateResponse)
async def impersonate_user(
    request: ImpersonateRequest,
    admin=Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """
    Zaloguj się jako inny user (do debugowania problemów).
    WYMAGA podania powodu (reason) — logowane w audit trail.
    Token ważny 30 minut.
    """
    service = AdminService(db)
    result = await service.impersonate_user(admin, str(request.user_id), request.reason)
    if not result:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")
    return result
