"""
Media endpoints — Unsplash photo search.
GET /api/v1/media/unsplash/search?query=...&orientation=landscape&width=1200
"""

from fastapi import APIRouter

from app.services.media.unsplash import UnsplashService

router = APIRouter(prefix="/media")


@router.get("/unsplash/search")
async def search_unsplash(
    query: str,
    orientation: str = "landscape",
    width: int = 1200,
):
    """Search Unsplash for a photo matching query. Returns {url} or {url: null}."""
    service = UnsplashService()
    url = await service.search_photo(query, orientation, width)
    return {"url": url}
