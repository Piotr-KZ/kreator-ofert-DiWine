"""
Creator: Config endpoints (step 7) — save/get project configuration.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.creator import ConfigData
from app.services.creator.project_service import ProjectService

router = APIRouter()


@router.put("/{project_id}/config")
async def save_config(
    project_id: UUID,
    data: ConfigData,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Merge-save config (tab-level auto-save)."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)

    existing = project.config_json or {}
    incoming = data.model_dump(exclude_none=True)

    # Merge at top level (forms, social, seo, legal, hosting)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(existing.get(key), dict):
            existing[key] = {**existing[key], **value}
        else:
            existing[key] = value

    project.config_json = existing
    await db.flush()
    await db.refresh(project)
    return {"config_json": project.config_json}


@router.get("/{project_id}/config")
async def get_config(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get project configuration."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    return {"config_json": project.config_json or {}}
