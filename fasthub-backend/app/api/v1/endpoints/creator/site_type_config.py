"""
Creator: Site Type Config API — per-type configuration (Brief 42).
Read-only endpoint, no auth needed — pure in-memory config.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.creator import SiteTypeConfigResponse, SiteTypeListItem
from app.services.creator.site_type_config import (
    SITE_TYPE_CONFIGS,
    get_all_site_types,
    get_site_type_config,
    to_api_dict,
)

router = APIRouter()


@router.get("/creator/site-type-config", response_model=list[SiteTypeListItem])
async def list_site_type_configs():
    """List all available site types with basic info."""
    return get_all_site_types()


@router.get("/creator/site-type-config/{site_type}", response_model=SiteTypeConfigResponse)
async def get_site_type_config_endpoint(site_type: str):
    """Get full configuration for a specific site type."""
    if site_type not in SITE_TYPE_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nieznany typ strony: {site_type}",
        )
    config = get_site_type_config(site_type)
    return to_api_dict(config)
