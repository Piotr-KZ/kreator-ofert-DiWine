"""
API v1 router — aggregates all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, blocks, company, export, media, offer_ai, offer_export, offer_fakturownia, offer_pages, offer_photos, offers, projects

api_router = APIRouter()

api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(blocks.router, tags=["blocks"])
api_router.include_router(export.router, tags=["export"])
api_router.include_router(media.router, tags=["media"])
api_router.include_router(offer_ai.router)
api_router.include_router(offer_photos.router)
api_router.include_router(offer_pages.router)
api_router.include_router(offer_pages.public_router)
api_router.include_router(offer_export.router)
api_router.include_router(offer_fakturownia.router)
api_router.include_router(company.router)
api_router.include_router(offers.router)
