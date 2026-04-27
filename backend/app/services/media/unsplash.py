"""
Unsplash API service — search stock photos for website sections.
Uses official Unsplash API (not deprecated source.unsplash.com).
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

UNSPLASH_API = "https://api.unsplash.com"
UTM = "utm_source=lab_creator&utm_medium=referral"


class UnsplashService:
    """Search stock photos from Unsplash API."""

    def __init__(self):
        self.api_key = settings.UNSPLASH_ACCESS_KEY
        self.enabled = bool(self.api_key)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=UNSPLASH_API,
            headers={"Authorization": f"Client-ID {self.api_key}"},
            timeout=10.0,
        )

    async def search_photo(
        self,
        query: str,
        orientation: str = "landscape",
        width: int = 1200,
    ) -> dict | None:
        """Search for a photo and return full metadata.

        Returns dict with keys:
            url, photo_id, photographer_name, photographer_url, photo_page_url
        or None on failure.
        """
        if not self.enabled:
            return None

        try:
            async with self._client() as client:
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
                return {
                    "url": f"{raw_url}&w={width}&fit=crop&auto=format",
                    "photo_id": photo["id"],
                    "photographer_name": photo["user"]["name"],
                    "photographer_url": f"{photo['user']['links']['html']}?{UTM}",
                    "photo_page_url": f"{photo['links']['html']}?{UTM}",
                }

        except Exception as e:
            logger.warning("Unsplash search failed for '%s': %s", query, e)
            return None

    async def trigger_download(self, photo_id: str) -> dict | None:
        """Trigger the required download event for a photo (Unsplash API requirement).

        Also fetches photographer attribution data.

        Returns dict with photographer_name, photographer_url or None on failure.
        """
        if not self.enabled:
            return None

        try:
            async with self._client() as client:
                # Required by Unsplash API Guidelines — must be called on each use
                await client.get(f"/photos/{photo_id}/download")

                # Fetch photo details for attribution
                info_resp = await client.get(f"/photos/{photo_id}")
                info_resp.raise_for_status()
                photo = info_resp.json()

                return {
                    "photographer_name": photo["user"]["name"],
                    "photographer_url": f"{photo['user']['links']['html']}?{UTM}",
                    "photo_page_url": f"{photo['links']['html']}?{UTM}",
                }

        except Exception as e:
            logger.warning("Unsplash trigger_download failed for '%s': %s", photo_id, e)
            return None

    async def search_photos_gallery(
        self,
        query: str,
        orientation: str = "landscape",
        width: int = 800,
        count: int = 8,
    ) -> list[dict]:
        """Search for multiple photos for ImagePicker gallery display.

        Returns list of photo dicts (same keys as search_photo) or empty list.
        """
        if not self.enabled:
            return []

        try:
            async with self._client() as client:
                resp = await client.get("/search/photos", params={
                    "query": query,
                    "orientation": orientation,
                    "per_page": min(count, 30),
                    "content_filter": "high",
                })
                resp.raise_for_status()
                results = resp.json().get("results", [])

                return [
                    {
                        "url": f"{p['urls']['raw']}&w={width}&fit=crop&auto=format",
                        "photo_id": p["id"],
                        "photographer_name": p["user"]["name"],
                        "photographer_url": f"{p['user']['links']['html']}?{UTM}",
                        "photo_page_url": f"{p['links']['html']}?{UTM}",
                    }
                    for p in results
                ]

        except Exception as e:
            logger.warning("Unsplash gallery search failed for '%s': %s", query, e)
            return []

    async def get_photo_for_section(
        self,
        photo_query: str,
        media_type: str,
    ) -> dict | None:
        """Get photo for section based on media_type.

        media_type → orientation and size:
          photo_wide   → landscape, 1600px (hero, background)
          photo_split  → landscape, 800px (next to text)
          avatars      → squarish, 200px (testimonials, team)

        Returns full photo dict (url + attribution) or None.
        """
        if media_type == "photo_wide":
            return await self.search_photo(photo_query, "landscape", 1600)
        elif media_type == "photo_split":
            return await self.search_photo(photo_query, "landscape", 800)
        elif media_type == "avatars":
            return await self.search_photo(photo_query, "squarish", 200)
        else:
            return await self.search_photo(photo_query, "landscape", 1200)
