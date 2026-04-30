"""
API v1 router — aggregates all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, blocks, export, media, offer_export, offers, projects

api_router = APIRouter()

api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(blocks.router, tags=["blocks"])
api_router.include_router(export.router, tags=["export"])
api_router.include_router(media.router, tags=["media"])
api_router.include_router(offers.router)
api_router.include_router(offer_export.router)
