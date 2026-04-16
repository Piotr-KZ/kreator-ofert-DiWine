"""
Model selector — Haiku/Sonnet per stage (from Axonet).

Optimizes costs by routing cheap tasks to Haiku, complex ones to Sonnet.
"""

from app.core.config import settings

# Mapowanie etapów kreacji na tier modelu
_STAGE_TIER: dict[str, str] = {
    # Haiku — szybkie, tanie ($1/M input)
    "chat_validation": "fast",
    "chat_editing": "fast",
    "chat_config": "fast",
    "suggest_seo": "fast",
    "generate_rodo_clause": "fast",
    "generate_cookie_info": "fast",
    # Sonnet — główne zadania ($3/M input)
    "validate_consistency": "smart",
    "generate_structure": "smart",
    "generate_section_content": "smart",
    "generate_privacy_policy": "smart",
    "generate_terms": "smart",
    "check_readiness": "smart",
    "visual_review": "smart",
    "visual_fix_review": "smart",
}

_TIER_MODEL: dict[str, str] = {
    "fast": settings.AI_MODEL_FAST,
    "smart": settings.AI_MODEL_SMART,
}


def get_model_tier(stage: str) -> str:
    """Get model tier (fast/smart) for a given pipeline stage."""
    return _STAGE_TIER.get(stage, "smart")


def get_model(stage: str) -> str:
    """Get model ID for a given pipeline stage."""
    tier = get_model_tier(stage)
    return _TIER_MODEL.get(tier, settings.AI_MODEL_SMART)
