"""
Creator: Stock photo search + download endpoints.
Brief 34: image search for block slots.
"""

import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.project_section import ProjectSection
from app.models.user import User
from app.services.creator.image_service import process_image
from app.services.creator.project_service import ProjectService
from app.services.creator.stock_photos import StockPhotoService

router = APIRouter()


class StockPhotoDownload(BaseModel):
    url: str
    slot_id: str
    section_id: str
    aspect_ratio: str = "auto"


@router.get("/stock-photos")
async def search_stock_photos(
    query: str,
    per_page: int = 12,
    current_user: User = Depends(get_current_active_user),
):
    """Search stock photos (Unsplash + Pexels)."""
    service = StockPhotoService()
    results = await service.search(query, per_page)
    return results


@router.post("/projects/{project_id}/stock-photos/download")
async def download_stock_photo(
    project_id: str,
    data: StockPhotoDownload,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Download stock photo, crop to aspect ratio, save to section slot."""
    svc = ProjectService(db)
    section = await svc.get_section_or_404(data.section_id, project_id, org.id)

    # Download image
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(data.url)
            r.raise_for_status()
            img_bytes = r.content
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to download image",
        )

    # Process image (crop + resize + WebP)
    processed = process_image(img_bytes, data.aspect_ratio)

    # Save to local storage (simplified — in production use S3)
    import os
    upload_dir = os.path.join("uploads", "projects", str(project_id), "photos")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.webp"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(processed)

    file_url = f"/uploads/projects/{project_id}/photos/{filename}"

    # Update section slot
    slots = section.slots_json or {}
    slots[data.slot_id] = file_url
    section.slots_json = slots
    await db.commit()

    return {"file_url": file_url}
