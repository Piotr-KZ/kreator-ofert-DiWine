"""
Creator: Stats endpoint — project statistics.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.published_site import PublishedSite
from app.models.user import User
from app.services.creator.stats_service import get_project_stats

router = APIRouter()


@router.get("/{project_id}/stats")
async def project_stats(
    project_id: UUID,
    period: str = "30d",
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get project statistics (visitors, leads, sources)."""
    result = await db.execute(
        select(PublishedSite).where(
            PublishedSite.project_id == project_id,
            PublishedSite.organization_id == org.id,
        )
    )
    site = result.scalar_one_or_none()

    if not site:
        return {
            "period": period,
            "visitors": 0,
            "leads": 0,
            "bounce_rate": None,
            "avg_time_on_site": None,
            "published_at": None,
            "daily_visitors": [],
            "traffic_sources": [],
        }

    return await get_project_stats(db, site.id, period, site.published_at)
