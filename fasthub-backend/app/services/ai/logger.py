"""
AI call logging — saves every Claude API call to ai_generation_logs.
Uses cache-aware cost estimation (from Axonet).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_conversation import AIGenerationLog
from app.services.ai.claude_client import estimate_cost

logger = logging.getLogger(__name__)


async def log_ai_call(
    db: AsyncSession,
    project,
    action: str,
    response,
    screenshots_count: int = 0,
    iterations: int = 1,
):
    """Log an AI call to ai_generation_logs."""
    cache_read = getattr(response, "cache_read_tokens", 0) or 0
    cache_creation = getattr(response, "cache_creation_tokens", 0) or 0

    cost = estimate_cost(
        response.model,
        response.tokens_in,
        response.tokens_out,
        cache_read=cache_read,
        cache_creation=cache_creation,
        images=screenshots_count,
    )

    log = AIGenerationLog(
        project_id=project.id if project else None,
        organization_id=project.organization_id if project else None,
        action=action,
        model=response.model,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        cost_usd=cost,
        duration_ms=response.duration_ms,
        screenshots_count=screenshots_count,
        iterations=iterations,
        success=not getattr(response, "_parse_error", False),
    )
    db.add(log)
    await db.flush()
