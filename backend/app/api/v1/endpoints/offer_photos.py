"""
Offer photo endpoints — default photos, picker, scrape.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel as PydanticBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
