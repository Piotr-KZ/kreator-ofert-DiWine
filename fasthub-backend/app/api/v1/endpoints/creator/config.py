"""
Creator: Config endpoints (step 7) — save/get project configuration.
"""

import copy
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.creator import AIVisibilityData, ConfigData
from app.services.creator.project_service import ProjectService

router = APIRouter()


def _encrypt_ftp_password(config: dict) -> dict:
    """Encrypt FTP password before storing in DB."""
    hosting = config.get("hosting")
    if not hosting or not isinstance(hosting, dict):
        return config
    ftp = hosting.get("ftp")
    if not ftp or not isinstance(ftp, dict):
        return config
    password = ftp.get("password")
    if password and not password.startswith("ENC:"):
        try:
            from fasthub_core.security.encryption import encrypt_credentials
            ftp["password"] = encrypt_credentials({"p": password})
        except Exception:
            pass  # Keep plain if encryption unavailable
    return config


def _decrypt_ftp_password(config: dict) -> dict:
    """Decrypt FTP password when returning to frontend."""
    config = copy.deepcopy(config)
    hosting = config.get("hosting")
    if not hosting or not isinstance(hosting, dict):
        return config
    ftp = hosting.get("ftp")
    if not ftp or not isinstance(ftp, dict):
        return config
    password = ftp.get("password")
    if password and password.startswith("ENC:"):
        try:
            from fasthub_core.security.encryption import decrypt_credentials
            decrypted = decrypt_credentials(password)
            ftp["password"] = decrypted.get("p", "")
        except Exception:
            ftp["password"] = ""
    return config


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

    existing = dict(project.config_json or {})
    incoming = data.model_dump(exclude_none=True)

    # Merge at top level (forms, social, seo, legal, hosting)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(existing.get(key), dict):
            existing[key] = {**existing[key], **value}
        else:
            existing[key] = value

    # Encrypt FTP password before saving
    existing = _encrypt_ftp_password(existing)

    # Assign a new dict to ensure SQLAlchemy detects the change
    project.config_json = existing
    await db.flush()
    await db.refresh(project)
    return {"config_json": _decrypt_ftp_password(project.config_json or {})}


@router.put("/{project_id}/ai-visibility")
async def save_ai_visibility(
    project_id: UUID,
    data: AIVisibilityData,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Save AI Visibility data (Brief 41)."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)

    project.ai_visibility = data.model_dump(exclude_unset=True)
    await db.flush()
    await db.refresh(project)
    return {"ai_visibility": project.ai_visibility or {}}


@router.get("/{project_id}/ai-visibility")
async def get_ai_visibility(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI Visibility data."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    return {"ai_visibility": project.ai_visibility or {}}


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
    return {"config_json": _decrypt_ftp_password(project.config_json or {})}
