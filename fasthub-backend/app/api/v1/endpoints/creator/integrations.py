"""
Creator: Integrations endpoints — catalog + per-site CRUD.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.published_site import PublishedSite
from app.models.site_integration import SiteIntegration
from app.models.user import User
from app.schemas.creator import SiteIntegrationCreate, SiteIntegrationResponse
from app.services.creator.integrations_catalog import (
    get_automation_templates,
    get_catalog,
)

# Public router — catalog doesn't need auth
public_router = APIRouter()

# Protected router — per-site operations
router = APIRouter()


@public_router.get("/integrations/catalog")
async def integrations_catalog():
    """Return full integrations catalog (static data)."""
    return get_catalog()


@public_router.get("/integrations/automations")
async def automations_catalog():
    """Return automation templates."""
    return get_automation_templates()


@router.get(
    "/{project_id}/integrations",
    response_model=list[SiteIntegrationResponse],
)
async def list_integrations(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List connected integrations for a project's published site."""
    site = await _get_site(project_id, org.id, db)
    if not site:
        return []

    result = await db.execute(
        select(SiteIntegration)
        .where(SiteIntegration.site_id == site.id)
        .order_by(SiteIntegration.connected_at.desc())
    )
    return result.scalars().all()


@router.post(
    "/{project_id}/integrations",
    response_model=SiteIntegrationResponse,
    status_code=201,
)
async def connect_integration(
    project_id: UUID,
    body: SiteIntegrationCreate,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect an integration to a project's site."""
    site = await _get_site(project_id, org.id, db)
    if not site:
        raise HTTPException(status_code=404, detail="Published site not found")

    # Check for duplicate provider
    existing = await db.execute(
        select(SiteIntegration).where(
            SiteIntegration.site_id == site.id,
            SiteIntegration.provider == body.provider,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail=f"Integration '{body.provider}' already connected"
        )

    integration = SiteIntegration(
        site_id=site.id,
        provider=body.provider,
        config_json=body.config_json,
        status="configured",
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return integration


@router.delete("/{project_id}/integrations/{integration_id}")
async def disconnect_integration(
    project_id: UUID,
    integration_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect an integration."""
    site = await _get_site(project_id, org.id, db)
    if not site:
        raise HTTPException(status_code=404, detail="Published site not found")

    result = await db.execute(
        select(SiteIntegration).where(
            SiteIntegration.id == integration_id,
            SiteIntegration.site_id == site.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    await db.delete(integration)
    await db.flush()
    return {"deleted": True}


@router.post("/{project_id}/integrations/{integration_id}/test")
async def test_integration(
    project_id: UUID,
    integration_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Test an integration connection (stub — always returns OK for V1)."""
    site = await _get_site(project_id, org.id, db)
    if not site:
        raise HTTPException(status_code=404, detail="Published site not found")

    result = await db.execute(
        select(SiteIntegration).where(
            SiteIntegration.id == integration_id,
            SiteIntegration.site_id == site.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    return {"status": "ok", "provider": integration.provider}


async def _get_site(
    project_id: UUID, org_id: UUID, db: AsyncSession
) -> PublishedSite | None:
    """Get published site for project + org."""
    result = await db.execute(
        select(PublishedSite).where(
            PublishedSite.project_id == project_id,
            PublishedSite.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()
