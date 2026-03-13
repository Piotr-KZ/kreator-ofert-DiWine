"""
Creator: Publishing endpoints (steps 8-9) — readiness check, publish, unpublish, export.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User
from app.services.creator.publisher import PublishingEngine
from app.services.creator.readiness_checker import ReadinessChecker

router = APIRouter()


async def _get_project_full(project_id: UUID, org_id: UUID, db: AsyncSession) -> Project:
    """Load project with sections and materials for publishing."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.sections), selectinload(Project.materials))
        .where(Project.id == project_id, Project.organization_id == org_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/check-readiness")
async def check_readiness(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 8: Run programmatic readiness checks."""
    project = await _get_project_full(project_id, org.id, db)

    checker = ReadinessChecker()
    result = checker.check(project)

    # Save in project
    project.check_json = result
    await db.flush()

    return result


@router.post("/{project_id}/publish")
async def publish_project(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 9: Publish the site."""
    project = await _get_project_full(project_id, org.id, db)

    engine = PublishingEngine(db)
    site = await engine.publish(project)
    await db.commit()

    return {
        "subdomain": site.subdomain,
        "url": f"https://{site.custom_domain or site.subdomain}.fasthub.site",
        "status": "published",
        "published_at": site.published_at.isoformat() if site.published_at else None,
    }


@router.post("/{project_id}/unpublish")
async def unpublish_project(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Take site offline."""
    project = await _get_project_full(project_id, org.id, db)

    engine = PublishingEngine(db)
    await engine.unpublish(project)
    await db.commit()

    return {"status": "unpublished"}


@router.post("/{project_id}/republish")
async def republish_project(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing published site."""
    project = await _get_project_full(project_id, org.id, db)

    engine = PublishingEngine(db)
    site = await engine.republish(project)
    await db.commit()

    return {
        "subdomain": site.subdomain,
        "url": f"https://{site.custom_domain or site.subdomain}.fasthub.site",
        "status": "republished",
        "published_at": site.published_at.isoformat() if site.published_at else None,
    }


@router.get("/{project_id}/export-zip")
async def export_zip(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Download project as ZIP file."""
    project = await _get_project_full(project_id, org.id, db)

    engine = PublishingEngine(db)
    zip_bytes = await engine.generate_zip(project)

    filename = f"{project.name.replace(' ', '_')}.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
