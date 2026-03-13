"""
Creator: Style endpoints (step 3).
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.creator import StyleData
from app.services.creator.project_service import ProjectService

router = APIRouter()


@router.put("/{project_id}/style")
async def save_style(
    project_id: UUID,
    data: StyleData,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Save visual style (step 3 — palette, fonts, theme, borders)."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    project.style_json = data.model_dump(exclude_unset=True)
    project.current_step = max(project.current_step, 3)
    return {"ok": True}


@router.get("/{project_id}/style")
async def get_style(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the style data."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    return project.style_json or {}
