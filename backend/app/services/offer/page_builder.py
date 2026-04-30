"""
Auto-builder — creates Project from Offer + page template.
Fills block slots with offer data, client data, text templates.
"""

import logging
from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_section import ProjectSection
from app.models.offer import Offer, OfferSet, Product, Packaging, Color, Occasion
from app.models.offer_text import OfferTextTemplate
from app.services.offer.page_templates import get_template

logger = logging.getLogger(__name__)


async def build_offer_page(
    db: AsyncSession,
    offer: Offer,
    template_id: str = "standard",
) -> Optional[str]:
    """
    Create a Project (page) from Offer using a page template.
    Returns project_id or None on error.
    """
    tpl = get_template(template_id)
    if not tpl:
        logger.error("Unknown template: %s", template_id)
        return None

    # ─── Gather context ───
    client = offer.client
    occasion = None
    if offer.occasion_code:
        result = await db.execute(select(Occasion).where(Occasion.code == offer.occasion_code))
        occasion = result.scalar_one_or_none()

    occasion_name = occasion.name if occasion else "Prezenty firmowe"
    now = datetime.utcnow()

    # Products lookup
    product_ids = set()
    for s in offer.sets:
        for item in s.items:
            if item.product_id:
                product_ids.add(item.product_id)
    products = {}
    if product_ids:
        result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        for p in result.scalars().all():
            products[p.id] = p

    # Colors lookup
    result = await db.execute(select(Color))
    colors = {c.code: c.name for c in result.scalars().all()}

    # Packagings lookup
    pkg_ids = {s.packaging_id for s in offer.sets if s.packaging_id}
    packagings = {}
    if pkg_ids:
        result = await db.execute(select(Packaging).where(Packaging.id.in_(pkg_ids)))
        for p in result.scalars().all():
            packagings[p.id] = p

    # Text templates (first matching variant for each type)
    text_cache = {}

    async def get_text(block_type: str, occ_code: Optional[str] = None) -> str:
        key = f"{block_type}:{occ_code}"
        if key not in text_cache:
            from sqlalchemy import or_
            query = select(OfferTextTemplate).where(
                OfferTextTemplate.block_type == block_type,
                OfferTextTemplate.is_active == True,
            )
            if occ_code:
                query = query.where(or_(
                    OfferTextTemplate.occasion_code == occ_code,
                    OfferTextTemplate.occasion_code.is_(None),
                ))
            query = query.order_by(OfferTextTemplate.order, OfferTextTemplate.variant).limit(1)
            result = await db.execute(query)
            t = result.scalar_one_or_none()
            if t:
                # Simple placeholder fill
                text = t.template_text.format(
                    company_name=client.company_name if client else "",
                    contact_person=client.contact_person if client else "Szanowni Państwo",
                    contact_role=client.contact_role if client else "",
                    quantity=offer.quantity,
                    occasion_name=occasion_name,
                )
                text_cache[key] = text
            else:
                text_cache[key] = ""
        return text_cache[key]

    # ─── Create Project ───
    project = Project(
        id=str(uuid4()),
        name=f"Oferta {offer.offer_number} — {client.company_name if client else ''}",
        site_type="offer",
        status="draft",
        current_step=5,
        brief_json={
            "offer_id": offer.id,
            "offer_number": offer.offer_number,
            "template_id": template_id,
        },
    )
    db.add(project)
    await db.flush()

    # ─── Build sections ───
    position = 0
    used_fun_facts = 0

    for block_def in tpl["blocks"]:
        code = block_def["block_code"]

        # Handle repeated blocks (sets)
        if block_def.get("repeat") == "sets":
            for s in sorted(offer.sets, key=lambda x: x.position):
                slots = _build_set_slots(s, products, packagings, colors, offer.quantity)
                section = ProjectSection(
                    id=str(uuid4()),
                    project_id=project.id,
                    block_code=code,
                    position=position,
                    slots_json=slots,
                )
                db.add(section)
                position += 1
            continue

        # Build slots from map
        slots_map = block_def.get("slots_map", {})
        slots = {}

        for slot_key, source in slots_map.items():
            if source.startswith("static:"):
                slots[slot_key] = source[7:]
            elif source.startswith("offer."):
                field = source[6:]
                if field == "offer_number":
                    slots[slot_key] = offer.offer_number
                elif field == "date":
                    slots[slot_key] = now.strftime("%d.%m.%Y")
                elif field == "expires_at":
                    slots[slot_key] = offer.expires_at or ""
                elif field == "occasion_name":
                    slots[slot_key] = occasion_name
                elif field == "accept_url":
                    slots[slot_key] = f"/public/offers/{offer.public_token}/accept" if offer.public_token else "#"
                elif field == "contact_name":
                    slots[slot_key] = ""  # TODO: from seller config
                elif field == "contact_email":
                    slots[slot_key] = ""
                elif field == "contact_phone":
                    slots[slot_key] = ""
            elif source.startswith("client."):
                field = source[7:]
                if client:
                    slots[slot_key] = getattr(client, field, "") or ""
                else:
                    slots[slot_key] = ""
            elif source.startswith("text:"):
                parts = source[5:].split(":")
                block_type = parts[0]
                occ = offer.occasion_code if len(parts) > 1 and parts[1] == "occasion" else None
                # For fun_facts, get different variants
                if block_type == "fun_fact":
                    used_fun_facts += 1
                    all_facts = await _get_all_texts(db, "fun_fact", occ)
                    idx = min(used_fun_facts - 1, len(all_facts) - 1)
                    slots[slot_key] = all_facts[idx] if all_facts else ""
                else:
                    slots[slot_key] = await get_text(block_type, occ)
            elif source.startswith("unsplash:"):
                slots[slot_key] = ""  # TODO: resolve via Unsplash service

        section = ProjectSection(
            id=str(uuid4()),
            project_id=project.id,
            block_code=code,
            position=position,
            slots_json=slots,
        )
        db.add(section)
        position += 1

    # Link offer to project
    offer.project_id = project.id
    await db.flush()

    logger.info("Built offer page: project=%s, sections=%d, template=%s", project.id, position, template_id)
    return project.id


def _build_set_slots(
    offer_set: OfferSet, products: dict, packagings: dict,
    colors: dict, quantity: int,
) -> dict:
    """Build slots_json for OZ1/OZ2 block from offer set data."""
    pkg = packagings.get(offer_set.packaging_id) if offer_set.packaging_id else None
    type_labels = {"wine": "Wino", "sweet": "Słodycze", "decoration": "Dodatek", "personalization": "Personalizacja"}

    items = []
    for item in sorted(offer_set.items, key=lambda x: x.created_at):
        prod = products.get(item.product_id)
        items.append({
            "name": prod.name if prod else "?",
            "type_label": type_labels.get(item.item_type, item.item_type),
            "color_name": colors.get(item.color_code, "") if item.color_code else "",
            "price": f"{item.unit_price:.2f}",
        })

    return {
        "set_name": offer_set.name,
        "set_description": "",
        "unit_price": f"{offer_set.unit_price:.2f}",
        "total_price": f"{offer_set.total_price:.2f}",
        "quantity": str(quantity),
        "packaging_name": pkg.name if pkg else "",
        "packaging_price": f"{pkg.price:.2f}" if pkg else "0",
        "items": items,
    }


async def _get_all_texts(db: AsyncSession, block_type: str, occ_code: Optional[str]) -> list[str]:
    """Get all text variants for fun_facts rotation."""
    from sqlalchemy import or_
    query = select(OfferTextTemplate).where(
        OfferTextTemplate.block_type == block_type,
        OfferTextTemplate.is_active == True,
    )
    if occ_code:
        query = query.where(or_(
            OfferTextTemplate.occasion_code == occ_code,
            OfferTextTemplate.occasion_code.is_(None),
        ))
    result = await db.execute(query.order_by(OfferTextTemplate.order, OfferTextTemplate.variant))
    return [t.template_text for t in result.scalars().all()]
