"""
Stats service — project statistics.
V1: leads from form_submissions, rest is stub (real tracking in Brief 38).
"""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.form_submission import FormSubmission


async def get_project_stats(
    db: AsyncSession,
    site_id: UUID,
    period: str = "30d",
    published_at: datetime | None = None,
) -> dict:
    """Get project statistics. V1: leads from form_submissions, rest stubbed."""
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    since = datetime.utcnow() - timedelta(days=days)

    # Real data: count form submissions (leads)
    leads_result = await db.execute(
        select(func.count(FormSubmission.id)).where(
            FormSubmission.site_id == site_id,
            FormSubmission.created_at >= since,
        )
    )
    leads = leads_result.scalar() or 0

    # Stub data for V1 (real tracking comes in Brief 38)
    return {
        "period": period,
        "visitors": 0,  # Brief 38: natywny tracking
        "leads": leads,
        "bounce_rate": None,  # Brief 38: tracking
        "avg_time_on_site": None,  # Brief 38: tracking
        "published_at": published_at.isoformat() if published_at else None,
        "daily_visitors": [],  # Brief 38: [{date, count}]
        "traffic_sources": [],  # Brief 38: [{source, percentage}]
    }
