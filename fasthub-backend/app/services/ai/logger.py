"""
AI call logging — saves every Claude API call to ai_generation_logs.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_conversation import AIGenerationLog

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
    cost = estimate_cost(
        response.model, response.tokens_in, response.tokens_out, screenshots_count
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


def estimate_cost(
    model: str, tokens_in: int, tokens_out: int, images: int = 0
) -> float:
    """Estimate API call cost in USD."""
    PRICES = {
        "claude-haiku-4-5-20251001": {"in": 1.0, "out": 5.0},
        "claude-sonnet-4-20250514": {"in": 3.0, "out": 15.0},
    }
    prices = PRICES.get(model, {"in": 3.0, "out": 15.0})

    cost = (tokens_in * prices["in"] + tokens_out * prices["out"]) / 1_000_000

    # Images: ~1600 tokens per image (Sonnet vision pricing)
    if images:
        cost += images * 1600 * prices["in"] / 1_000_000

    return round(cost, 6)
