"""
Photo library — lifestyle photos for offer pages.
Auto-downloads from Unsplash on first startup. Default photo per template category.
"""

import json as _json
import logging
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer_photo import OfferPhoto
from app.services.media.unsplash import UnsplashService

logger = logging.getLogger(__name__)

# Queries grouped by category — each category = one type of offer header
PHOTO_QUERIES = [
    # Christmas
    {"query": "christmas wine gift elegant", "category": "christmas", "count": 3, "default": True,
     "tags": ["święta", "wino", "prezent", "choinka", "ciepły", "elegancki"]},
    {"query": "christmas table setting candles wine", "category": "christmas", "count": 2,
     "tags": ["święta", "stół", "świece", "wino", "kolacja", "rodzinny"]},

    # Easter
    {"query": "easter spring table celebration wine", "category": "easter", "count": 2, "default": True,
     "tags": ["wielkanoc", "wiosna", "stół", "kwiaty", "pastelowy", "jasny"]},
    {"query": "easter pastel flowers wine", "category": "easter", "count": 1,
     "tags": ["wielkanoc", "kwiaty", "pastelowy", "delikatny"]},

    # Lifestyle
    {"query": "business wine tasting professional", "category": "lifestyle", "count": 2, "default": True,
     "tags": ["biznes", "tasting", "profesjonalny", "formalny", "spotkanie"]},
    {"query": "people wine toast elegant dinner", "category": "lifestyle", "count": 2,
     "tags": ["toast", "ludzie", "kolacja", "elegancki", "wieczór"]},
    {"query": "friends wine celebration", "category": "lifestyle", "count": 2,
     "tags": ["przyjaciele", "zabawa", "casual", "radość", "grupa"]},

    # Wine
    {"query": "wine bottle elegant dark background", "category": "wine", "count": 2, "default": True,
     "tags": ["butelka", "ciemne_tło", "produkt", "elegancki", "minimalistyczny"]},
    {"query": "red wine glass closeup", "category": "wine", "count": 2,
     "tags": ["kieliszek", "czerwone", "zbliżenie", "detale"]},

    # Gift
    {"query": "luxury gift box premium packaging", "category": "gift", "count": 2, "default": True,
     "tags": ["pudełko", "luksus", "opakowanie", "wstążka", "premium"]},
    {"query": "corporate gift elegant ribbon", "category": "gift", "count": 2,
     "tags": ["firmowy", "elegancki", "wstążka", "prezent", "korporacyjny"]},

    # Universal
    {"query": "wine cheese board elegant table", "category": "universal", "count": 2, "default": True,
     "tags": ["ser", "deska", "wino", "przekąski", "uniwersalny"]},
    {"query": "wine vineyard sunset", "category": "universal", "count": 2,
     "tags": ["winnica", "zachód", "natura", "krajobraz", "ciepły"]},
]


async def seed_lifestyle_photos(db: AsyncSession) -> dict:
    """
    Download lifestyle photos from Unsplash on startup.
    Idempotent — skips if photos already exist in category.
    Called from main.py lifespan, same as seed_offer_data.
    """
    # Check if already seeded
    existing = await db.scalar(select(func.count(OfferPhoto.id)))
    if existing and existing > 10:
        logger.info("Photo library already has %d photos, skipping download", existing)
        return {"skipped": existing}

    unsplash = UnsplashService()
    if not unsplash.enabled:
        logger.warning("UNSPLASH_ACCESS_KEY not set — photo library empty. Set key in .env and restart.")
        return {"error": "No Unsplash key", "downloaded": 0}

    stats = {"downloaded": 0, "errors": 0}

    for q in PHOTO_QUERIES:
        try:
            photos = await unsplash.search_photos_batch(
                query=q["query"], count=q["count"],
                orientation="landscape", width=1200,
            )
            for i, photo in enumerate(photos):
                if not photo or not photo.get("url"):
                    continue
                # Check duplicate
                exists = await db.scalar(
                    select(func.count(OfferPhoto.id)).where(OfferPhoto.url == photo["url"])
                )
                if exists:
                    continue

                offer_photo = OfferPhoto(
                    url=photo["url"],
                    thumbnail_url=photo.get("url"),
                    query=q["query"],
                    category=q["category"],
                    photographer_name=photo.get("photographer_name"),
                    photographer_url=photo.get("photographer_url"),
                    source="unsplash",
                    is_default=(q.get("default", False) and i == 0),
                    tags_json=_json.dumps(q.get("tags", []), ensure_ascii=False),
                    orientation="landscape",
                    width=1200, height=800,
                )
                db.add(offer_photo)
                stats["downloaded"] += 1

        except Exception as e:
            logger.error("Photo download failed for '%s': %s", q["query"], e)
            stats["errors"] += 1

    await db.commit()
    logger.info("Photo library seeded: %s", stats)
    return stats


async def get_default_photo(db: AsyncSession, category: str) -> Optional[dict]:
    """
    Get default photo for category. Used by page_builder.
    Returns the one marked is_default=True, or first available.
    """
    # Try default first
    result = await db.execute(
        select(OfferPhoto).where(
            OfferPhoto.category == category,
            OfferPhoto.is_default == True,
            OfferPhoto.is_active == True,
        ).limit(1)
    )
    photo = result.scalar_one_or_none()

    # Fallback: any from category
    if not photo:
        result = await db.execute(
            select(OfferPhoto).where(
                OfferPhoto.category == category,
                OfferPhoto.is_active == True,
            ).limit(1)
        )
        photo = result.scalar_one_or_none()

    # Last fallback: any photo at all
    if not photo:
        result = await db.execute(
            select(OfferPhoto).where(OfferPhoto.is_active == True).limit(1)
        )
        photo = result.scalar_one_or_none()

    if photo:
        return {"id": photo.id, "url": photo.url, "category": photo.category}
    return None


async def scrape_diwine_products(db: AsyncSession, dry_run: bool = True) -> dict:
    """
    Scrape product photos from diwine.pl and store as OfferPhoto.
    dry_run=True: only return found images without saving.
    """
    import httpx
    import re

    stats = {"found": 0, "saved": 0, "skipped": 0, "errors": 0}
    found_images: list[dict] = []

    PAGES = [
        ("https://diwine.pl/kategoria-produktu/wino/", "wine"),
        ("https://diwine.pl/kategoria-produktu/prezenty/", "gift"),
    ]

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for page_url, category in PAGES:
            try:
                resp = await client.get(page_url)
                html = resp.text

                # Extract product images from WooCommerce structure
                # Pattern: <img ... src="https://diwine.pl/wp-content/uploads/..." ...>
                img_pattern = r'<img[^>]+src=["\']?(https://diwine\.pl/wp-content/uploads/[^"\'>\s]+\.(?:png|jpg|jpeg|webp))["\']?'
                urls = re.findall(img_pattern, html, re.IGNORECASE)

                # Extract product names from links
                name_pattern = r'<a[^>]+href="https://diwine\.pl/produkt/[^"]*"[^>]*>\s*(?:<[^>]*>)*\s*([^<]+)'
                names = re.findall(name_pattern, html)

                seen = set()
                for url in urls:
                    # Skip duplicates, tiny icons, placeholder images
                    if url in seen:
                        continue
                    if any(skip in url.lower() for skip in ['icon', 'logo', 'placeholder', 'woocommerce', '-150x', '-100x', '-50x']):
                        continue
                    seen.add(url)
                    stats["found"] += 1

                    # Guess product name from URL
                    filename = url.split('/')[-1].rsplit('.', 1)[0]
                    name = filename.replace('-', ' ').replace('_', ' ').title()

                    tags = ["diwine", "produkt", category]
                    if category == "wine":
                        tags.extend(["wino", "butelka"])
                    elif category == "gift":
                        tags.extend(["prezent", "zestaw"])

                    found_images.append({
                        "url": url,
                        "name": name,
                        "category": category,
                        "tags": tags,
                    })

            except Exception as e:
                logger.error("Scrape error for %s: %s", page_url, e)
                stats["errors"] += 1

    if dry_run:
        return {"dry_run": True, "found": stats["found"], "images": found_images}

    # Save to DB
    for img in found_images:
        exists = await db.scalar(
            select(func.count(OfferPhoto.id)).where(OfferPhoto.url == img["url"])
        )
        if exists:
            stats["skipped"] += 1
            continue

        photo = OfferPhoto(
            url=img["url"],
            thumbnail_url=img["url"],
            query=img["name"],
            category=img["category"],
            photographer_name="DiWine",
            photographer_url="https://diwine.pl",
            source="diwine",
            is_default=False,
            tags_json=_json.dumps(img["tags"], ensure_ascii=False),
            orientation="portrait",
            width=800, height=1000,
        )
        db.add(photo)
        stats["saved"] += 1

    await db.commit()
    logger.info("DiWine scrape: %s", stats)
    return {"dry_run": False, **stats, "images": found_images}


async def get_photos_for_picker(db: AsyncSession, category: str, limit: int = 12) -> list[dict]:
    """
    Get all photos in category for picker UI.
    User sees these when they want to change the default.
    """
    result = await db.execute(
        select(OfferPhoto)
        .where(OfferPhoto.category == category, OfferPhoto.is_active == True)
        .order_by(OfferPhoto.is_default.desc())  # default first
        .limit(limit)
    )
    return [
        {"id": p.id, "url": p.url, "thumbnail_url": p.thumbnail_url,
         "category": p.category, "is_default": p.is_default,
         "tags": _json.loads(p.tags_json) if p.tags_json else []}
        for p in result.scalars().all()
    ]
