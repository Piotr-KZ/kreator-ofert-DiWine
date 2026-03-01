"""
API endpoints Audit Trail.
Prefix: /api/audit
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from uuid import UUID

from fasthub_core.db.session import get_db
from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.auth.superadmin import require_superadmin
from fasthub_core.audit.service import AuditService
from fasthub_core.audit.schemas import (
    AuditLogList, AuditStatsResponse, RetentionResult, AuditLogResponse,
)

router = APIRouter(prefix="/api/audit", tags=["Audit Trail"])


@router.get("/logs", response_model=AuditLogList)
async def get_audit_logs(
    organization_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    resource_type: Optional[str] = Query(None, description="np. 'user', 'subscription', 'process'"),
    resource_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None, description="np. 'create', 'update', 'delete', 'login'"),
    date_from: Optional[datetime] = Query(None, description="ISO format: 2026-01-01T00:00:00"),
    date_to: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None, description="Szukaj w summary, IP, email"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pobierz logi audytu z filtrami.
    Zwykły user widzi tylko logi swojej organizacji.
    Super Admin widzi wszystko.
    """
    audit = AuditService(db)

    # Jeśli nie jest super admin — ogranicz do swojej organizacji
    if not getattr(current_user, 'is_superadmin', False):
        organization_id = getattr(current_user, 'organization_id', organization_id)

    return await audit.get_logs(
        organization_id=str(organization_id) if organization_id else None,
        user_id=str(user_id) if user_id else None,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        per_page=per_page,
    )


@router.get("/resource/{resource_type}/{resource_id}", response_model=list[AuditLogResponse])
async def get_resource_history(
    resource_type: str,
    resource_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Historia zmian jednego zasobu (np. jednej subskrypcji, jednego procesu)"""
    audit = AuditService(db)
    return await audit.get_resource_history(resource_type, resource_id)


@router.get("/stats", response_model=AuditStatsResponse)
async def get_audit_stats(
    organization_id: Optional[UUID] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Statystyki audit logu"""
    audit = AuditService(db)
    return await audit.get_stats(
        organization_id=str(organization_id) if organization_id else None
    )


@router.post("/cleanup", response_model=RetentionResult)
async def cleanup_old_logs(
    retention_days: int = Query(90, ge=7, le=365, description="Usuń logi starsze niż X dni"),
    admin=Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    """
    Ręczne czyszczenie starych logów. Tylko Super Admin.
    Domyślnie: 90 dni. Minimum: 7 dni. Maximum: 365 dni.
    """
    audit = AuditService(db)
    deleted = await audit.cleanup_old_logs(retention_days)
    return RetentionResult(deleted_count=deleted, retention_days=retention_days)
