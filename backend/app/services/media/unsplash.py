"""
Unsplash API service — search stock photos for website sections.
Uses official Unsplash API (not deprecated source.unsplash.com).
Includes persistent file cache + rate-limit protection (50 req/hr free tier).
Fallback: Lorem Picsum (no auth, no rate limit) when Unsplash is exhausted.
"""

import asyncio
import json
import logging
from pathlib import Path

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

UNSPLASH_API = "https://api.unsplash.com"
UTM = "utm_source=lab_creator&utm_medium=referral"

# Delay between consecutive API calls to avoid bursts
_REQUEST_DELAY = 0.35  # seconds

# Persistent cache file — survives backend restarts
_CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "unsplash_cache.json"

# Picsum fallback seed range — produces deterministic photos
_PICSUM_BASE = "https://picsum.photos/seed"


def _load_cache() -> dict:
    """Load persistent cache from disk."""
    try:
        if _CACHE_FILE.exists():
            return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_cache(cache: dict) -> None:
    """Save persistent cache to disk."""
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning("Failed to save Unsplash cache: %s", e)


# Shared persistent cache across all UnsplashService instances
_persistent_cache: dict = _load_cache()


def _picsum_url(query: str, width: int = 1200, height: int = 800) -> str:
    """Generate a deterministic Picsum URL from query string (as seed)."""
    # Use hash of query as seed for consistent results
    seed = abs(hash(query)) % 1000000
    return f"{_PICSUM_BASE}/{seed}/{width}/{height}"


class UnsplashService:
    """Search stock photos from Unsplash API."""

    def __init__(self):
        self.api_key = settings.UNSPLASH_ACCESS_KEY
        self.enabled = bool(self.api_key)
        self._rate_limited = False
        self._call_count = 0
        self._remaining = 50  # Unsplash free tier

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=UNSPLASH_API,
            headers={"Authorization": f"Client-ID {self.api_key}"},
            timeout=10.0,
        )

    def _check_rate_headers(self, resp: httpx.Response) -> None:
        """Read X-Ratelimit-Remaining from response and update state."""
        remaining = resp.headers.get("X-Ratelimit-Remaining")
        if remaining is not None:
            try:
                self._remaining = int(remaining)
                if self._remaining <= 2:
                    logger.warning("Unsplash rate limit nearly exhausted: %d remaining", self._remaining)
                    self._rate_limited = True
            except ValueError:
                pass

    def _picsum_fallback(self, query: str, width: int, height: int) -> dict:
        """Generate a Picsum fallback photo dict."""
        return {
            "url": _picsum_url(query, width, height),
            "photo_id": f"picsum-{abs(hash(query)) % 1000000}",
            "photographer_name": "Lorem Picsum",
            "photographer_url": "https://picsum.photos",
            "photo_page_url": "https://picsum.photos",
        }

    async def search_photo(
        self,
        query: str,
        orientation: str = "landscape",
        width: int = 1200,
    ) -> dict | None:
        """Search for a photo and return full metadata.

        Returns dict with keys:
            url, photo_id, photographer_name, photographer_url, photo_page_url
        or None on failure. Falls back to Picsum if rate limited.
        """
        if not self.enabled and not self._rate_limited:
            return None

        # Check persistent cache first
        cache_key = f"{query}|{orientation}|{width}"
        if cache_key in _persistent_cache:
            cached = _persistent_cache[cache_key]
            return cached if cached else None

        # If rate limited, use Picsum fallback
        if self._rate_limited or not self.enabled:
            h = 800 if orientation == "landscape" else width
            result = self._picsum_fallback(query, width, h)
            _persistent_cache[cache_key] = result
            _save_cache(_persistent_cache)
            return result

        # Throttle: delay between calls
        if self._call_count > 0:
            await asyncio.sleep(_REQUEST_DELAY)
        self._call_count += 1

        try:
            async with self._client() as client:
                resp = await client.get("/search/photos", params={
                    "query": query,
                    "orientation": orientation,
                    "per_page": 1,
                    "content_filter": "high",
                })
                self._check_rate_headers(resp)

                if resp.status_code == 403:
                    logger.warning("Unsplash rate limit hit (403) after %d calls — falling back to Picsum", self._call_count)
                    self._rate_limited = True
                    h = 800 if orientation == "landscape" else width
                    result = self._picsum_fallback(query, width, h)
                    _persistent_cache[cache_key] = result
                    _save_cache(_persistent_cache)
                    return result

                resp.raise_for_status()
                data = resp.json()

                results = data.get("results", [])
                if not results:
                    _persistent_cache[cache_key] = None
                    _save_cache(_persistent_cache)
                    return None

                photo = results[0]
                raw_url = photo["urls"]["raw"]
                result = {
                    "url": f"{raw_url}&w={width}&fit=crop&auto=format",
                    "photo_id": photo["id"],
                    "photographer_name": photo["user"]["name"],
                    "photographer_url": f"{photo['user']['links']['html']}?{UTM}",
                    "photo_page_url": f"{photo['links']['html']}?{UTM}",
                }
                _persistent_cache[cache_key] = result
                _save_cache(_persistent_cache)
                logger.info("Unsplash: resolved '%s' → %s (remaining: %d)", query, photo["id"], self._remaining)
                return result

        except Exception as e:
            logger.warning("Unsplash search failed for '%s': %s — using Picsum fallback", query, e)
            h = 800 if orientation == "landscape" else width
            result = self._picsum_fallback(query, width, h)
            _persistent_cache[cache_key] = result
            _save_cache(_persistent_cache)
            return result

    async def trigger_download(self, photo_id: str) -> dict | None:
        """Trigger the required download event for a photo (Unsplash API requirement).

        Also fetches photographer attribution data.

        Returns dict with photographer_name, photographer_url or None on failure.
        """
        if not self.enabled or self._rate_limited:
            return None
        if photo_id.startswith("picsum-"):
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

    async def search_photos_batch(
        self,
        query: str,
        count: int = 5,
        orientation: str = "landscape",
        width: int = 800,
    ) -> list[dict]:
        """Fetch multiple distinct photos in a SINGLE API call.

        Used by resolve_media to get images for features/tiers/testimonials
        without making N separate requests.
        Returns list of photo dicts or empty list. Falls back to Picsum if rate limited.
        """
        cache_key = f"batch|{query}|{orientation}|{width}|{count}"
        if cache_key in _persistent_cache:
            return _persistent_cache[cache_key] or []

        # If rate limited or disabled, generate Picsum fallbacks
        if self._rate_limited or not self.enabled:
            photos = [
                self._picsum_fallback(f"{query} {i}", width, 600 if orientation == "landscape" else width)
                for i in range(count)
            ]
            _persistent_cache[cache_key] = photos
            _save_cache(_persistent_cache)
            return photos

        if self._call_count > 0:
            await asyncio.sleep(_REQUEST_DELAY)
        self._call_count += 1

        try:
            async with self._client() as client:
                resp = await client.get("/search/photos", params={
                    "query": query,
                    "orientation": orientation,
                    "per_page": min(count, 10),
                    "content_filter": "high",
                })
                self._check_rate_headers(resp)

                if resp.status_code == 403:
                    logger.warning("Unsplash rate limit (403) in batch — using Picsum fallback")
                    self._rate_limited = True
                    photos = [
                        self._picsum_fallback(f"{query} {i}", width, 600 if orientation == "landscape" else width)
                        for i in range(count)
                    ]
                    _persistent_cache[cache_key] = photos
                    _save_cache(_persistent_cache)
                    return photos

                resp.raise_for_status()
                results = resp.json().get("results", [])

                photos = [
                    {
                        "url": f"{p['urls']['raw']}&w={width}&fit=crop&auto=format",
                        "photo_id": p["id"],
                        "photographer_name": p["user"]["name"],
                        "photographer_url": f"{p['user']['links']['html']}?{UTM}",
                        "photo_page_url": f"{p['links']['html']}?{UTM}",
                    }
                    for p in results
                ]
                _persistent_cache[cache_key] = photos
                _save_cache(_persistent_cache)
                logger.info("Unsplash batch: '%s' → %d photos (remaining: %d)", query, len(photos), self._remaining)
                return photos

        except Exception as e:
            logger.warning("Unsplash batch search failed for '%s': %s — using Picsum", query, e)
            photos = [
                self._picsum_fallback(f"{query} {i}", width, 600 if orientation == "landscape" else width)
                for i in range(count)
            ]
            _persistent_cache[cache_key] = photos
            _save_cache(_persistent_cache)
            return photos

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
