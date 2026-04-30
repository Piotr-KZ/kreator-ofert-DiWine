"""
Offer API endpoints — products catalog, clients, offers, sets, calculator.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.offer import (
    Client, Color, DiscountRule, Occasion, Offer, OfferSet,
    OfferSetItem, Packaging, Product, Supplier,
)
from app.schemas.offer import (
    ClientCreate, ClientOut, OfferCreate, OfferSetCreate,
    OfferOut, OfferSetOut,
)
from app.services.offer.calculator import (
    calc_set_price, generate_offer_number, validate_set_capacity,
)

router = APIRouter(prefix="/offers", tags=["offers"])


# ════════════════════════════════════════════════════════════
# CATALOG — read-only (products, packagings, colors, occasions, discounts)
# ════════════════════════════════════════════════════════════

@router.get("/catalog/products")
async def list_products(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List products. Optional filter by category: wine, sweet, decoration, personalization."""
    query = select(Product).where(Product.is_active == True)
    if category:
        query = query.where(Product.category == category)
    result = await db.execute(query.order_by(Product.category, Product.name))
    products = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "base_price": p.base_price,
            "wine_color": p.wine_color,
            "wine_type": p.wine_type,
            "slot_size": p.slot_size,
            "available_colors_json": p.available_colors_json,
            "stock_quantity": p.stock_quantity,
            "restock_days": p.restock_days,
            "supplier_id": p.supplier_id,
            "image_url": p.image_url,
            "description": p.description,
        }
        for p in products
    ]


@router.get("/catalog/packagings")
async def list_packagings(
    packaging_type: str | None = None,
    bottles: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List packagings. Optional filter by type and/or bottle count."""
    query = select(Packaging).where(Packaging.is_active == True)
    if packaging_type:
        query = query.where(Packaging.packaging_type == packaging_type)
    if bottles is not None:
        query = query.where(Packaging.bottles == bottles)
    result = await db.execute(query.order_by(Packaging.packaging_type, Packaging.bottles))
    pkgs = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "packaging_type": p.packaging_type,
            "bottles": p.bottles,
            "sweet_slots": p.sweet_slots,
            "price": p.price,
            "stock_quantity": p.stock_quantity,
        }
        for p in pkgs
    ]


@router.get("/catalog/colors")
async def list_colors(db: AsyncSession = Depends(get_db)):
    """List all available colors."""
    result = await db.execute(select(Color).order_by(Color.name))
    return [{"code": c.code, "name": c.name, "hex_value": c.hex_value} for c in result.scalars().all()]


@router.get("/catalog/occasions")
async def list_occasions(db: AsyncSession = Depends(get_db)):
    """List all occasions with allowed colors."""
    result = await db.execute(select(Occasion).where(Occasion.is_active == True).order_by(Occasion.name))
    return [
        {"code": o.code, "name": o.name, "allowed_colors_json": o.allowed_colors_json}
        for o in result.scalars().all()
    ]


@router.get("/catalog/discounts")
async def list_discounts(db: AsyncSession = Depends(get_db)):
    """List all discount rules."""
    result = await db.execute(select(DiscountRule).order_by(DiscountRule.rule_type, DiscountRule.min_quantity))
    return [
        {
            "id": d.id,
            "rule_type": d.rule_type,
            "product_id": d.product_id,
            "min_quantity": d.min_quantity,
            "max_quantity": d.max_quantity,
            "discount_percent": d.discount_percent,
            "fixed_price": d.fixed_price,
        }
        for d in result.scalars().all()
    ]


@router.get("/catalog/suppliers")
async def list_suppliers(db: AsyncSession = Depends(get_db)):
    """List all suppliers."""
    result = await db.execute(select(Supplier).order_by(Supplier.name))
    return [
        {"id": s.id, "name": s.name, "contact_email": s.contact_email, "delivery_days": s.delivery_days}
        for s in result.scalars().all()
    ]


# ════════════════════════════════════════════════════════════
# CLIENTS
# ════════════════════════════════════════════════════════════

@router.post("/clients")
async def create_client(data: ClientCreate, db: AsyncSession = Depends(get_db)):
    """Create a new client."""
    client = Client(id=str(uuid4()), **data.model_dump())
    db.add(client)
    await db.flush()
    return {"id": client.id, "company_name": client.company_name}


@router.get("/clients")
async def list_clients(db: AsyncSession = Depends(get_db)):
    """List all clients."""
    result = await db.execute(select(Client).order_by(Client.company_name))
    clients = result.scalars().all()
    return [
        {
            "id": c.id,
            "company_name": c.company_name,
            "nip": c.nip,
            "contact_person": c.contact_person,
            "contact_role": c.contact_role,
            "email": c.email,
            "phone": c.phone,
        }
        for c in clients
    ]


@router.get("/clients/{client_id}")
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)):
    """Get client details."""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")
    return {
        "id": client.id,
        "company_name": client.company_name,
        "nip": client.nip,
        "regon": client.regon,
        "contact_person": client.contact_person,
        "contact_role": client.contact_role,
        "email": client.email,
        "phone": client.phone,
        "address": client.address,
        "delivery_address": client.delivery_address,
        "vip_discount_percent": client.vip_discount_percent,
        "fakturownia_id": client.fakturownia_id,
    }


# ════════════════════════════════════════════════════════════
# OFFERS
# ════════════════════════════════════════════════════════════

async def _get_offer_full(offer_id: str, db: AsyncSession) -> Offer:
    """Load offer with sets and items."""
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


async def _get_discount_rules(db: AsyncSession) -> list[dict]:
    """Get all discount rules as dicts for calculator."""
    result = await db.execute(select(DiscountRule))
    return [
        {
            "rule_type": r.rule_type,
            "product_id": r.product_id,
            "min_quantity": r.min_quantity,
            "max_quantity": r.max_quantity,
            "discount_percent": r.discount_percent,
            "fixed_price": r.fixed_price,
        }
        for r in result.scalars().all()
    ]


async def _next_offer_number(db: AsyncSession) -> str:
    """Generate next offer number for current month."""
    now = datetime.utcnow()
    prefix = f"OF/{now.year}/{now.month:02d}/"
    result = await db.execute(
        select(func.count(Offer.id)).where(Offer.offer_number.startswith(prefix))
    )
    count = result.scalar() or 0
    return generate_offer_number(now.year, now.month, count + 1)


def _serialize_offer(offer: Offer) -> dict:
    """Serialize offer with sets and items."""
    return {
        "id": offer.id,
        "offer_number": offer.offer_number,
        "client_id": offer.client_id,
        "client_name": offer.client.company_name if offer.client else None,
        "status": offer.status,
        "occasion_code": offer.occasion_code,
        "quantity": offer.quantity,
        "deadline": offer.deadline,
        "delivery_address": offer.delivery_address,
        "created_at": offer.created_at.isoformat() if offer.created_at else None,
        "sets": [
            {
                "id": s.id,
                "name": s.name,
                "position": s.position,
                "budget_per_unit": s.budget_per_unit,
                "packaging_id": s.packaging_id,
                "unit_price": s.unit_price,
                "total_price": s.total_price,
                "items": [
                    {
                        "id": it.id,
                        "product_id": it.product_id,
                        "item_type": it.item_type,
                        "color_code": it.color_code,
                        "quantity": it.quantity,
                        "unit_price": it.unit_price,
                    }
                    for it in sorted(s.items, key=lambda x: x.created_at)
                ],
            }
            for s in sorted(offer.sets, key=lambda x: x.position)
        ],
    }


@router.post("")
async def create_offer(data: OfferCreate, db: AsyncSession = Depends(get_db)):
    """Create a new offer."""
    # Verify client exists
    client = (await db.execute(select(Client).where(Client.id == data.client_id))).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Klient nie znaleziony")

    offer_number = await _next_offer_number(db)

    offer = Offer(
        id=str(uuid4()),
        offer_number=offer_number,
        client_id=data.client_id,
        occasion_code=data.occasion_code,
        quantity=data.quantity,
        deadline=data.deadline,
        delivery_address=data.delivery_address or client.delivery_address,
        source_email=data.source_email,
    )
    db.add(offer)
    await db.flush()

    return {"id": offer.id, "offer_number": offer.offer_number}


@router.get("")
async def list_offers(db: AsyncSession = Depends(get_db)):
    """List all offers with basic info."""
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.client))
        .order_by(Offer.created_at.desc())
    )
    offers = result.scalars().all()
    return [
        {
            "id": o.id,
            "offer_number": o.offer_number,
            "client_name": o.client.company_name if o.client else None,
            "status": o.status,
            "quantity": o.quantity,
            "occasion_code": o.occasion_code,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in offers
    ]


@router.get("/{offer_id}")
async def get_offer(offer_id: str, db: AsyncSession = Depends(get_db)):
    """Get full offer with sets and items."""
    offer = await _get_offer_full(offer_id, db)
    return _serialize_offer(offer)


@router.delete("/{offer_id}")
async def delete_offer(offer_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an offer."""
    offer = await _get_offer_full(offer_id, db)
    await db.delete(offer)
    return {"ok": True}


# ════════════════════════════════════════════════════════════
# OFFER SETS (zestawy prezentowe)
# ════════════════════════════════════════════════════════════

@router.post("/{offer_id}/sets")
async def add_set(offer_id: str, data: OfferSetCreate, db: AsyncSession = Depends(get_db)):
    """Add a new set to offer."""
    offer = await _get_offer_full(offer_id, db)
    discount_rules = await _get_discount_rules(db)

    # Resolve packaging
    packaging_price = 0.0
    pkg_bottles = 0
    pkg_sweet_slots = 0
    if data.packaging_id:
        pkg = (await db.execute(select(Packaging).where(Packaging.id == data.packaging_id))).scalar_one_or_none()
        if pkg:
            packaging_price = pkg.price
            pkg_bottles = pkg.bottles
            pkg_sweet_slots = pkg.sweet_slots

    # Create set
    position = len(offer.sets)
    offer_set = OfferSet(
        id=str(uuid4()),
        offer_id=offer_id,
        name=data.name,
        position=position,
        budget_per_unit=data.budget_per_unit,
        packaging_id=data.packaging_id,
    )
    db.add(offer_set)
    await db.flush()

    # Add items
    calc_items = []
    for item_data in data.items:
        item = OfferSetItem(
            id=str(uuid4()),
            offer_set_id=offer_set.id,
            product_id=item_data.product_id,
            item_type=item_data.item_type,
            color_code=item_data.color_code,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
        )
        db.add(item)
        calc_items.append({
            "item_type": item_data.item_type,
            "base_price": item_data.unit_price,
            "product_id": item_data.product_id,
        })

    # Calculate prices
    if calc_items:
        prices = calc_set_price(calc_items, packaging_price, offer.quantity, discount_rules)
        offer_set.unit_price = prices["unit_total"]
        offer_set.total_price = prices["grand_total"]

    await db.flush()
    return {"id": offer_set.id, "name": offer_set.name, "unit_price": offer_set.unit_price}


@router.delete("/{offer_id}/sets/{set_id}")
async def remove_set(offer_id: str, set_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a set from offer."""
    result = await db.execute(
        select(OfferSet).where(OfferSet.id == set_id, OfferSet.offer_id == offer_id)
    )
    offer_set = result.scalar_one_or_none()
    if not offer_set:
        raise HTTPException(status_code=404, detail="Zestaw nie znaleziony")
    await db.delete(offer_set)
    return {"ok": True}


# ════════════════════════════════════════════════════════════
# SET ITEMS (pozycje w zestawie)
# ════════════════════════════════════════════════════════════

@router.post("/{offer_id}/sets/{set_id}/items")
async def add_item_to_set(
    offer_id: str,
    set_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Add item to set. Body: {product_id, item_type, color_code?}
    Price calculated automatically from product + discount rules.
    """
    # Get offer for quantity
    offer = (await db.execute(select(Offer).where(Offer.id == offer_id))).scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta nie znaleziona")

    # Get set with items
    result = await db.execute(
        select(OfferSet)
        .options(selectinload(OfferSet.items))
        .where(OfferSet.id == set_id, OfferSet.offer_id == offer_id)
    )
    offer_set = result.scalar_one_or_none()
    if not offer_set:
        raise HTTPException(status_code=404, detail="Zestaw nie znaleziony")

    # Get product
    product_id = data.get("product_id")
    product = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nie znaleziony")

    # Get packaging for capacity check
    pkg = None
    if offer_set.packaging_id:
        pkg = (await db.execute(select(Packaging).where(Packaging.id == offer_set.packaging_id))).scalar_one_or_none()

    # Capacity check
    if pkg:
        if product.category == "wine":
            current_wines = sum(1 for i in offer_set.items if i.item_type == "wine")
            if current_wines >= pkg.bottles:
                raise HTTPException(status_code=400, detail=f"Brak wolnych slotów na wino ({current_wines}/{pkg.bottles}). Usuń butelkę z koszyka.")
        elif product.category in ("sweet", "decoration"):
            # Sum slot_size for all existing sweet/deco items
            existing_slot_sum = 0
            for existing_item in offer_set.items:
                if existing_item.item_type in ("sweet", "decoration") and existing_item.product_id:
                    ep = (await db.execute(select(Product).where(Product.id == existing_item.product_id))).scalar_one_or_none()
                    if ep:
                        existing_slot_sum += ep.slot_size
            if existing_slot_sum + product.slot_size > pkg.sweet_slots:
                raise HTTPException(status_code=400, detail=f"Brak wolnych slotów na dodatki ({existing_slot_sum}/{pkg.sweet_slots}). Usuń coś z koszyka.")

    # Calculate price
    discount_rules = await _get_discount_rules(db)
    item_type = data.get("item_type", product.category)

    if item_type == "wine":
        from app.services.offer.calculator import get_wine_discount_percent, calc_wine_price
        disc = get_wine_discount_percent(offer.quantity, discount_rules)
        unit_price = calc_wine_price(product.base_price, disc)
    elif item_type == "personalization":
        from app.services.offer.calculator import get_personalization_price
        unit_price = get_personalization_price(product.id, offer.quantity, discount_rules)
        if unit_price == 0:
            unit_price = product.base_price
    else:
        unit_price = product.base_price

    # Create item
    item = OfferSetItem(
        id=str(uuid4()),
        offer_set_id=set_id,
        product_id=product_id,
        item_type=item_type,
        color_code=data.get("color_code"),
        quantity=1,
        unit_price=unit_price,
    )
    db.add(item)

    # Recalculate set totals
    await db.flush()
    await _recalculate_set(offer_set, offer.quantity, db)

    return {"id": item.id, "unit_price": item.unit_price, "set_unit_price": offer_set.unit_price}


@router.delete("/{offer_id}/sets/{set_id}/items/{item_id}")
async def remove_item_from_set(
    offer_id: str,
    set_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove item from set and recalculate prices."""
    offer = (await db.execute(select(Offer).where(Offer.id == offer_id))).scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta nie znaleziona")

    result = await db.execute(
        select(OfferSetItem).where(OfferSetItem.id == item_id, OfferSetItem.offer_set_id == set_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pozycja nie znaleziona")

    await db.delete(item)
    await db.flush()

    # Recalculate
    result = await db.execute(
        select(OfferSet).options(selectinload(OfferSet.items)).where(OfferSet.id == set_id)
    )
    offer_set = result.scalar_one_or_none()
    if offer_set:
        await _recalculate_set(offer_set, offer.quantity, db)

    return {"ok": True, "set_unit_price": offer_set.unit_price if offer_set else 0}


async def _recalculate_set(offer_set: OfferSet, quantity: int, db: AsyncSession):
    """Recalculate set unit_price and total_price from items."""
    discount_rules = await _get_discount_rules(db)

    packaging_price = 0.0
    if offer_set.packaging_id:
        pkg = (await db.execute(select(Packaging).where(Packaging.id == offer_set.packaging_id))).scalar_one_or_none()
        if pkg:
            packaging_price = pkg.price

    calc_items = []
    for item in offer_set.items:
        product = None
        if item.product_id:
            product = (await db.execute(select(Product).where(Product.id == item.product_id))).scalar_one_or_none()
        calc_items.append({
            "item_type": item.item_type,
            "base_price": product.base_price if product else item.unit_price,
            "product_id": item.product_id,
        })

    if calc_items:
        prices = calc_set_price(calc_items, packaging_price, quantity, discount_rules)
        offer_set.unit_price = prices["unit_total"]
        offer_set.total_price = prices["grand_total"]

        # Update individual item prices (may have changed due to quantity)
        for item in offer_set.items:
            for detail in prices["items_detail"]:
                if detail.get("product_id") == item.product_id and detail.get("item_type") == item.item_type:
                    item.unit_price = detail["final_price"]
                    break
    else:
        offer_set.unit_price = packaging_price
        offer_set.total_price = round(packaging_price * quantity, 2)

    await db.flush()


# ════════════════════════════════════════════════════════════
# CALCULATOR (standalone price check without saving)
# ════════════════════════════════════════════════════════════

@router.post("/calculate")
async def calculate_price(data: dict, db: AsyncSession = Depends(get_db)):
    """
    Calculate set price without saving. For frontend live preview.
    Body: {quantity, packaging_id, items: [{product_id, item_type}]}
    """
    quantity = data.get("quantity", 100)
    packaging_id = data.get("packaging_id")
    items_input = data.get("items", [])

    discount_rules = await _get_discount_rules(db)

    # Resolve packaging
    packaging_price = 0.0
    pkg_bottles = 0
    pkg_sweet_slots = 0
    if packaging_id:
        pkg = (await db.execute(select(Packaging).where(Packaging.id == packaging_id))).scalar_one_or_none()
        if pkg:
            packaging_price = pkg.price
            pkg_bottles = pkg.bottles
            pkg_sweet_slots = pkg.sweet_slots

    # Resolve products
    calc_items = []
    wines_count = 0
    sweets_slot_sum = 0

    for item_input in items_input:
        product_id = item_input.get("product_id")
        item_type = item_input.get("item_type")

        product = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
        if not product:
            continue

        calc_items.append({
            "item_type": item_type or product.category,
            "base_price": product.base_price,
            "product_id": product.id,
        })

        if product.category == "wine":
            wines_count += 1
        elif product.category in ("sweet", "decoration"):
            sweets_slot_sum += product.slot_size

    # Calculate
    prices = calc_set_price(calc_items, packaging_price, quantity, discount_rules)

    # Validate capacity
    warnings = validate_set_capacity(pkg_bottles, pkg_sweet_slots, wines_count, sweets_slot_sum)

    return {
        **prices,
        "quantity": quantity,
        "warnings": warnings,
    }
