"""
Offer export endpoints — PDF generation and HTML preview.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.offer import (
    Client, Color, DiscountRule, Occasion, Offer, OfferSet,
    OfferSetItem, Packaging, Product,
)
from app.services.offer.calculator import get_wine_discount_percent
from app.services.offer.pdf_template import render_offer_pdf_html
from app.services.offer.pdf_generator import html_to_pdf

router = APIRouter(prefix="/offers", tags=["offer-export"])


async def _load_offer_full(offer_id: str, db: AsyncSession):
    """Load offer with all relations."""
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
    return offer


async def _build_render_context(offer, db: AsyncSession) -> dict:
    """Build all data needed for PDF/HTML rendering."""

    # Load products lookup
    product_ids = set()
    for s in offer.sets:
        for item in s.items:
            if item.product_id:
                product_ids.add(item.product_id)

    products_lookup = {}
    if product_ids:
        result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        for p in result.scalars().all():
            products_lookup[p.id] = {
                "id": p.id, "name": p.name, "category": p.category,
                "base_price": p.base_price, "wine_color": p.wine_color,
                "wine_type": p.wine_type,
            }

    # Load packagings lookup
    pkg_ids = {s.packaging_id for s in offer.sets if s.packaging_id}
    packagings_lookup = {}
    if pkg_ids:
        result = await db.execute(select(Packaging).where(Packaging.id.in_(pkg_ids)))
        for p in result.scalars().all():
            packagings_lookup[p.id] = {
                "id": p.id, "name": p.name, "price": p.price,
                "bottles": p.bottles, "sweet_slots": p.sweet_slots,
            }

    # Colors
    result = await db.execute(select(Color))
    colors = [{"code": c.code, "name": c.name, "hex_value": c.hex_value} for c in result.scalars().all()]

    # Occasion
    occasion_name = "Uniwersalny"
    if offer.occasion_code:
        result = await db.execute(select(Occasion).where(Occasion.code == offer.occasion_code))
        occ = result.scalar_one_or_none()
        if occ:
            occasion_name = occ.name

    # Discount
    result = await db.execute(select(DiscountRule))
    rules = [
        {"rule_type": r.rule_type, "min_quantity": r.min_quantity,
         "max_quantity": r.max_quantity, "discount_percent": r.discount_percent}
        for r in result.scalars().all()
    ]
    wine_disc = get_wine_discount_percent(offer.quantity, rules)

    # Client
    client_data = {
        "company_name": offer.client.company_name if offer.client else "",
        "nip": offer.client.nip if offer.client else "",
        "contact_person": offer.client.contact_person if offer.client else "",
        "contact_role": offer.client.contact_role if offer.client else "",
        "email": offer.client.email if offer.client else "",
        "phone": offer.client.phone if offer.client else "",
    }

    # Offer data
    offer_data = {
        "offer_number": offer.offer_number,
        "quantity": offer.quantity,
        "occasion_code": offer.occasion_code,
        "deadline": offer.deadline,
        "delivery_address": offer.delivery_address,
        "expires_at": offer.expires_at,
    }

    # Sets data
    sets_data = []
    for s in sorted(offer.sets, key=lambda x: x.position):
        set_dict = {
            "name": s.name,
            "packaging_id": s.packaging_id,
            "budget_per_unit": s.budget_per_unit,
            "unit_price": s.unit_price,
            "total_price": s.total_price,
            "items": [
                {
                    "product_id": item.product_id,
                    "item_type": item.item_type,
                    "color_code": item.color_code,
                    "unit_price": item.unit_price,
                }
                for item in sorted(s.items, key=lambda x: x.created_at)
            ],
        }
        sets_data.append(set_dict)

    return {
        "offer": offer_data,
        "client": client_data,
        "sets": sets_data,
        "products": products_lookup,
        "packagings": packagings_lookup,
        "colors": colors,
        "occasion_name": occasion_name,
        "wine_discount_percent": wine_disc,
    }


@router.get("/{offer_id}/preview")
async def preview_offer(offer_id: str, db: AsyncSession = Depends(get_db)):
    """Preview offer as HTML page (for browser viewing)."""
    offer = await _load_offer_full(offer_id, db)
    ctx = await _build_render_context(offer, db)

    html = render_offer_pdf_html(
        offer=ctx["offer"],
        client=ctx["client"],
        sets=ctx["sets"],
        products=ctx["products"],
        packagings=ctx["packagings"],
        colors=ctx["colors"],
        occasion_name=ctx["occasion_name"],
        wine_discount_percent=ctx["wine_discount_percent"],
    )

    return HTMLResponse(content=html)


@router.get("/{offer_id}/pdf")
async def export_offer_pdf(offer_id: str, db: AsyncSession = Depends(get_db)):
    """Download offer as PDF file."""
    offer = await _load_offer_full(offer_id, db)
    ctx = await _build_render_context(offer, db)

    html = render_offer_pdf_html(
        offer=ctx["offer"],
        client=ctx["client"],
        sets=ctx["sets"],
        products=ctx["products"],
        packagings=ctx["packagings"],
        colors=ctx["colors"],
        occasion_name=ctx["occasion_name"],
        wine_discount_percent=ctx["wine_discount_percent"],
    )

    pdf_bytes = html_to_pdf(html)

    filename = f"Oferta_{offer.offer_number.replace('/', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
