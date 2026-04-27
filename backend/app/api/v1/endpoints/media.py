"""
Media endpoints — Unsplash photo search and download trigger.

GET  /api/v1/media/unsplash/search?query=...&orientation=landscape&width=1200
GET  /api/v1/media/unsplash/trigger-download/{photo_id}
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
    """Search Unsplash for a photo matching query.

    Returns full photo metadata:
      { url, photo_id, photographer_name, photographer_url, photo_page_url }
    or { url: null } if not found / API not configured.
    """
    service = UnsplashService()
    photo = await service.search_photo(query, orientation, width)
    if photo is None:
        return {"url": None}
    return photo


@router.get("/unsplash/gallery")
async def gallery_unsplash(
    query: str,
    orientation: str = "landscape",
    width: int = 800,
    count: int = 8,
):
    """Return multiple photos for ImagePicker gallery.

    Each item: { url, photo_id, photographer_name, photographer_url, photo_page_url }
    Returns { photos: [] } when API not configured.
    """
    service = UnsplashService()
    photos = await service.search_photos_gallery(query, orientation, width, count)
    return {"photos": photos}


@router.get("/unsplash/trigger-download/{photo_id}")
async def trigger_unsplash_download(photo_id: str):
    """Trigger the required Unsplash download event and return photographer info.

    Must be called each time a photo is actually used on a page.
    Required by Unsplash API Guidelines.

    Returns:
      { photographer_name, photographer_url, photo_page_url }
    or { photographer_name: null } if API not configured / photo not found.
    """
    service = UnsplashService()
    result = await service.trigger_download(photo_id)
    if result is None:
        return {"photographer_name": None, "photographer_url": None, "photo_page_url": None}
    return result
