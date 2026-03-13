"""
Stock photo search — Unsplash + Pexels fallback.
Brief 34: image search for block slots.
"""

import httpx

from fasthub_core.config import settings


class StockPhotoService:
    """Search stock photos from Unsplash (primary) and Pexels (fallback)."""

    async def search(self, query: str, per_page: int = 12) -> list[dict]:
        """Search photos. Returns list of {url, thumb, author, source}."""
        results: list[dict] = []

        if getattr(settings, "UNSPLASH_ACCESS_KEY", None):
            results = await self._search_unsplash(query, per_page)

        if len(results) < per_page and getattr(settings, "PEXELS_API_KEY", None):
            results += await self._search_pexels(query, per_page - len(results))

        return results[:per_page]

    async def _search_unsplash(self, query: str, per_page: int) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": query,
                        "per_page": per_page,
                        "orientation": "landscape",
                    },
                    headers={
                        "Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"
                    },
                )
                r.raise_for_status()
                return [
                    {
                        "url": p["urls"]["regular"],
                        "thumb": p["urls"]["small"],
                        "author": p["user"]["name"],
                        "source": "unsplash",
                        "download_url": p["links"].get("download_location", p["urls"]["regular"]),
                    }
                    for p in r.json().get("results", [])
                ]
        except Exception:
            return []

    async def _search_pexels(self, query: str, per_page: int) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": query, "per_page": per_page},
                    headers={"Authorization": settings.PEXELS_API_KEY},
                )
                r.raise_for_status()
                return [
                    {
                        "url": p["src"]["large"],
                        "thumb": p["src"]["medium"],
                        "author": p["photographer"],
                        "source": "pexels",
                        "download_url": p["src"]["original"],
                    }
                    for p in r.json().get("photos", [])
                ]
        except Exception:
            return []
