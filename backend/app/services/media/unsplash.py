"""
Unsplash API service — search stock photos for website sections.
Uses official Unsplash API (not deprecated source.unsplash.com).
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

UNSPLASH_API = "https://api.unsplash.com"


class UnsplashService:
    """Search stock photos from Unsplash API."""

    def __init__(self):
        self.api_key = settings.UNSPLASH_ACCESS_KEY
        self.enabled = bool(self.api_key)

    async def search_photo(
        self,
        query: str,
        orientation: str = "landscape",
        width: int = 1200,
    ) -> str | None:
        """Search for a photo and return its URL.

        Args:
            query: contextual query (e.g. "business team professional office")
            orientation: landscape | portrait | squarish
            width: width in px

        Returns:
            Photo URL or None
        """
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(
                base_url=UNSPLASH_API,
                headers={"Authorization": f"Client-ID {self.api_key}"},
                timeout=10.0,
            ) as client:
                resp = await client.get("/search/photos", params={
                    "query": query,
                    "orientation": orientation,
                    "per_page": 1,
                    "content_filter": "high",
                })
                resp.raise_for_status()
                data = resp.json()

                results = data.get("results", [])
                if not results:
                    return None

                photo = results[0]
                raw_url = photo["urls"]["raw"]
                return f"{raw_url}&w={width}&fit=crop&auto=format"

        except Exception as e:
            logger.warning("Unsplash search failed for '%s': %s", query, e)
            return None

    async def get_photo_for_section(
        self,
        photo_query: str,
        media_type: str,
    ) -> str | None:
        """Get photo for section based on media_type.

        media_type → orientation and size:
          photo_wide   → landscape, 1600px (hero, background)
          photo_split  → landscape, 800px (next to text)
          avatars      → squarish, 200px (testimonials, team)
        """
        if media_type == "photo_wide":
            return await self.search_photo(photo_query, "landscape", 1600)
        elif media_type == "photo_split":
            return await self.search_photo(photo_query, "landscape", 800)
        elif media_type == "avatars":
            return await self.search_photo(photo_query, "squarish", 200)
        else:
            return await self.search_photo(photo_query, "landscape", 1200)
