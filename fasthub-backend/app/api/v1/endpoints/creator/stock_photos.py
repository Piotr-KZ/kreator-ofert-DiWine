"""
Creator: Stock photo search + download endpoints.
Brief 34: image search for block slots.
"""

import ipaddress
import socket
import uuid
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
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


_ALLOWED_PHOTO_HOSTS = {
    "images.unsplash.com",
    "images.pexels.com",
    "cdn.pixabay.com",
}


def _is_private_ip(hostname: str, port: int | None = None) -> bool:
    """Check if hostname resolves to a private/internal IP."""
    try:
        results = socket.getaddrinfo(hostname, port or 443, proto=socket.IPPROTO_TCP)
        for _, _, _, _, sockaddr in results:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
        return False
    except Exception:
        return True


class StockPhotoDownload(BaseModel):
    url: str
    slot_id: str
    section_id: str
    aspect_ratio: str = "auto"

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only http/https URLs allowed")
        if not parsed.hostname:
            raise ValueError("Invalid URL")
        # Allow only known stock photo hosts
        if parsed.hostname not in _ALLOWED_PHOTO_HOSTS:
            raise ValueError(f"Domain not allowed: {parsed.hostname}")
        return v


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

    # SSRF check
    parsed_url = urlparse(data.url)
    if _is_private_ip(parsed_url.hostname or "", parsed_url.port):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL targets private/internal address",
        )

    # Download image
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            r = await client.get(data.url)
            r.raise_for_status()
            # Verify content is actually an image
            content_type = r.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="URL did not return an image",
                )
            # Limit size to 20MB
            if len(r.content) > 20 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image too large (max 20MB)",
                )
            img_bytes = r.content
    except HTTPException:
        raise
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
