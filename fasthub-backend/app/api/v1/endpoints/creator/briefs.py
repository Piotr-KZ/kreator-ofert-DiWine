"""
Creator: Brief endpoints (step 1).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.creator import BriefData
from app.services.creator.project_service import ProjectService

router = APIRouter()


@router.put("/{project_id}/brief")
async def save_brief(
    project_id: UUID,
    data: BriefData,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Save the full brief (step 1 — 11 questions). Auto-save on each change."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    project.brief_json = data.model_dump(exclude_unset=True)
    project.current_step = max(project.current_step, 1)
    return {"ok": True}


@router.get("/{project_id}/brief")
async def get_brief(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the brief data."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    return project.brief_json or {}
