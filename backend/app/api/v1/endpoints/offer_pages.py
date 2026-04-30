"""
Offer page endpoints — template selection, page building, public preview.
"""

import secrets
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.offer import Offer, OfferSet, OfferSetItem
from app.models.project import Project
from app.services.offer.page_templates import list_templates, get_template
from app.services.offer.page_builder import build_offer_page
from app.services.creator.renderer import PageRenderer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/offers", tags=["offer-pages"])


class BuildPageRequest(BaseModel):
    template_id: str = "standard"


@router.get("/page-templates")
async def get_page_templates():
    """List available offer page templates."""
    return list_templates()


@router.post("/{offer_id}/build-page")
async def build_page(
    offer_id: str,
    data: BuildPageRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Build offer page from template.
    Creates a Project with sections filled from offer data + text templates.
    """
    # Load offer with relations
    result = await db.execute(
        select(Offer)
        .options(
            selectinload(Offer.sets).selectinload(OfferSet.items),
            selectinload(Offer.client),
        )
        .where(Offer.id == offer_id)
    )
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta nie znaleziona")

    if not offer.sets:
        raise HTTPException(status_code=400, detail="Oferta nie ma zestawów — najpierw skompletuj zestawy")

    # Generate public token if missing
    if not offer.public_token:
        offer.public_token = secrets.token_urlsafe(32)
        await db.flush()

    # Build page
    project_id = await build_offer_page(db, offer, data.template_id)
    if not project_id:
        raise HTTPException(status_code=500, detail="Błąd budowania strony ofertowej")

    return {
        "project_id": project_id,
        "template_id": data.template_id,
        "public_url": f"/public/offers/{offer.public_token}",
        "editor_url": f"/lab/{project_id}/step/5",
    }


@router.get("/{offer_id}/page-preview")
async def preview_offer_page(
    offer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Preview offer page as HTML (for internal use, by offer_id)."""
    result = await db.execute(select(Offer).where(Offer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer or not offer.project_id:
        raise HTTPException(status_code=404, detail="Strona ofertowa nie wygenerowana")

    project = await _load_project(offer.project_id, db)
    html = await _render_project(project, db)
    return HTMLResponse(content=html)


# ─── Public router (no auth) ───

public_router = APIRouter(prefix="/public/offers", tags=["public-offers"])


@public_router.get("/{token}")
async def public_offer_page(token: str, db: AsyncSession = Depends(get_db)):
    """
    Public offer page — accessible by client via token link.
    No authentication required.
    """
    result = await db.execute(
        select(Offer).where(Offer.public_token == token)
    )
    offer = result.scalar_one_or_none()
    if not offer:
        return HTMLResponse(
            content="<h1>Oferta nie znaleziona</h1><p>Link jest nieprawidłowy lub oferta wygasła.</p>",
            status_code=404,
        )

    if not offer.project_id:
        return HTMLResponse(
            content="<h1>Strona ofertowa w przygotowaniu</h1><p>Oferta jest jeszcze opracowywana.</p>",
        )

    # Mark as viewed
    if offer.status == "sent":
        offer.status = "viewed"
        await db.flush()

    project = await _load_project(offer.project_id, db)
    html = await _render_project(project, db)
    return HTMLResponse(content=html)


@public_router.post("/{token}/accept")
async def accept_offer(token: str, db: AsyncSession = Depends(get_db)):
    """Client accepts offer via public link."""
    result = await db.execute(select(Offer).where(Offer.public_token == token))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta nie znaleziona")
    offer.status = "accepted"
    await db.flush()
    return {"ok": True, "status": "accepted", "offer_number": offer.offer_number}


# ─── Helpers ───

async def _load_project(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.sections), selectinload(Project.materials))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")
    return project


async def _render_project(project: Project, db: AsyncSession) -> str:
    """Render project to full HTML page."""
    renderer = PageRenderer()
    html_body, css = await renderer.render_project_html(db, project)
    name = project.name or "Oferta"
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>{css}</style>
</head>
<body>{html_body}</body>
</html>"""
