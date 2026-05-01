"""
Offer photo endpoints — default photos, picker, scrape, library, upload.
"""

import os
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel as PydanticBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.offer_photo import OfferPhoto


class ScrapeRequest(PydanticBase):
    website_url: str = "https://diwine.pl"
    dry_run: bool = True

router = APIRouter(prefix="/offers/photos", tags=["offer-photos"])


@router.get("/default")
async def default_photo(category: str, db: AsyncSession = Depends(get_db)):
    """Get default photo for category (used by builder)."""
    from app.services.offer.photo_library import get_default_photo
    photo = await get_default_photo(db, category)
    if not photo:
        raise HTTPException(status_code=404, detail=f"Brak zdjęć w kategorii '{category}'. Sprawdź UNSPLASH_ACCESS_KEY w .env i zrestartuj serwer.")
    return photo


@router.get("/picker")
async def photo_picker(category: str, limit: int = 12, db: AsyncSession = Depends(get_db)):
    """Get photos for picker — user wybiera inne niż domyślne."""
    from app.services.offer.photo_library import get_photos_for_picker
    return await get_photos_for_picker(db, category, limit)


@router.post("/scrape-products")
async def scrape_products(req: ScrapeRequest, db: AsyncSession = Depends(get_db)):
    """Scrape product photos from DiWine website. dry_run=true previews without saving."""
    from app.services.offer.photo_library import scrape_diwine_products
    return await scrape_diwine_products(db, dry_run=req.dry_run)


@router.get("/gallery", response_class=HTMLResponse)
async def photo_gallery(db: AsyncSession = Depends(get_db)):
    """Visual gallery of all photos in the library."""
    import json as _json
    result = await db.execute(
        select(OfferPhoto).where(OfferPhoto.is_active == True).order_by(OfferPhoto.category, OfferPhoto.source)
    )
    photos = result.scalars().all()

    cards = ""
    for p in photos:
        tags = _json.loads(p.tags_json) if p.tags_json else []
        tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
        default = ' <b style="color:#4ade80">DEFAULT</b>' if p.is_default else ""
        cards += f'''<div class="card">
            <img src="{p.url}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22160%22><rect fill=%22%23333%22 width=%22200%22 height=%22160%22/><text x=%2250%%22 y=%2250%%22 fill=%22%23666%22 text-anchor=%22middle%22 dy=%22.3em%22>404</text></svg>'">
            <div class="info">
                <span class="src">{p.source}</span> · <b>{p.category}</b>{default}<br>
                <span class="name">{p.query or ''}</span><br>
                {tag_html}
            </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Photo Library — {len(photos)} zdjęć</title>
<style>
body {{ background:#111; margin:0; padding:16px; font-family:'Outfit',system-ui,sans-serif; color:#ccc }}
h1 {{ color:#fff; font-size:18px; margin:0 0 4px }}
.stats {{ font-size:12px; color:#888; margin-bottom:16px }}
.grid {{ display:flex; flex-wrap:wrap; gap:10px }}
.card {{ background:#1a1a1a; border-radius:10px; overflow:hidden; width:230px; border:1px solid #333 }}
.card img {{ width:100%; height:170px; object-fit:cover }}
.card .info {{ padding:8px; font-size:11px; line-height:1.5 }}
.tag {{ display:inline-block; background:#2a2a2a; border-radius:4px; padding:1px 6px; margin:1px; font-size:9px; color:#999 }}
.src {{ color:#60a5fa; font-weight:600 }}
.name {{ color:#aaa; font-size:10px }}
</style></head>
<body>
<h1>Photo Library</h1>
<div class="stats">{len(photos)} zdjęć · {len(set(p.category for p in photos))} kategorii · źródła: {', '.join(sorted(set(p.source for p in photos)))}</div>
<div class="grid">{cards}</div>
</body></html>'''
    return HTMLResponse(content=html)


@router.get("/library")
async def photo_library(
    category: str | None = None,
    source: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List photos for OfferSettings gallery."""
    import json as _json
    query = select(OfferPhoto).where(OfferPhoto.is_active == True)
    if category:
        query = query.where(OfferPhoto.category == category)
    if source:
        query = query.where(OfferPhoto.source == source)
    query = query.order_by(OfferPhoto.category, OfferPhoto.created_at).limit(limit)
    result = await db.execute(query)
    return [
        {
            "id": p.id, "url": p.url,
            "thumbnail_url": p.thumbnail_url or p.url,
            "category": p.category, "source": p.source,
            "is_default": p.is_default,
            "tags": _json.loads(p.tags_json) if p.tags_json else [],
            "photographer_name": p.photographer_name,
        }
        for p in result.scalars().all()
    ]


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    category: str = Query(default="custom"),
    db: AsyncSession = Depends(get_db),
):
    """Upload a custom photo/logo."""
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/svg+xml"):
        raise HTTPException(status_code=400, detail="Dozwolone formaty: JPG, PNG, WebP, SVG")

    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{_uuid.uuid4()}.{ext}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Plik za duży (max 10 MB)")

    with open(save_path, "wb") as f:
        f.write(content)

    public_url = f"/uploads/{filename}"
    photo = OfferPhoto(
        url=public_url, thumbnail_url=public_url,
        category=category, source="upload",
        is_default=False, is_active=True,
    )
    db.add(photo)
    await db.flush()

    return {"id": photo.id, "url": public_url, "category": category}
