"""
Seed data for offer module — suppliers, products, packagings, colors, occasions, discounts.
Run via: seed_offer_data(db)
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Supplier, Product, Packaging, Color, Occasion, DiscountRule


async def seed_offer_data(db: AsyncSession) -> dict:
    """Seed all offer reference data. Returns counts."""
    counts = {}

    # ─── SUPPLIERS ───
    suppliers_data = [
        {"name": "Manufaktura Saska", "contact_email": "zamowienia@saska.pl", "contact_phone": "+48 22 345 67 89",
         "delivery_days": 5, "address_street": "Francuska", "address_number": "12",
         "address_postal_code": "03-906", "address_city": "Warszawa",
         "nip": "5213456789", "www": "https://manufakturasaska.pl"},
        {"name": "Stroiki Jan", "contact_email": "jan@stroiki.pl", "contact_phone": "+48 601 234 567",
         "delivery_days": 3, "address_street": "Kwiatowa", "address_number": "5A",
         "address_postal_code": "05-077", "address_city": "Piaseczno",
         "nip": "1231234567", "www": "https://stroikijan.pl"},
    ]
    sup_map = {}
    for s in suppliers_data:
        existing = (await db.execute(select(Supplier).where(Supplier.name == s["name"]))).scalar_one_or_none()
        if not existing:
            obj = Supplier(**s)
            db.add(obj)
            await db.flush()
            sup_map[s["name"]] = obj.id
        else:
            sup_map[s["name"]] = existing.id
    counts["suppliers"] = len(suppliers_data)

    # ─── COLORS ───
    colors_data = [
        {"code": "red", "name": "Czerwony", "hex_value": "#DC2626"},
        {"code": "gold", "name": "Złoty", "hex_value": "#D97706"},
        {"code": "green", "name": "Zielony", "hex_value": "#16A34A"},
        {"code": "blue", "name": "Niebieski", "hex_value": "#2563EB"},
        {"code": "yellow", "name": "Żółty", "hex_value": "#EAB308"},
        {"code": "pastel", "name": "Pastelowy", "hex_value": "#F9A8D4"},
        {"code": "craft", "name": "Kraftowy", "hex_value": "#8B5E3C"},
        {"code": "silver", "name": "Srebrny", "hex_value": "#9CA3AF"},
    ]
    for c in colors_data:
        existing = (await db.execute(select(Color).where(Color.code == c["code"]))).scalar_one_or_none()
        if not existing:
            db.add(Color(**c))
    counts["colors"] = len(colors_data)

    # ─── OCCASIONS ───
    occasions_data = [
        {"code": "christmas", "name": "Boże Narodzenie", "allowed_colors_json": ["red", "gold", "green", "blue", "craft"]},
        {"code": "easter", "name": "Wielkanoc", "allowed_colors_json": ["yellow", "pastel", "green", "gold"]},
        {"code": "universal", "name": "Uniwersalny", "allowed_colors_json": None},
        {"code": "birthday", "name": "Urodziny", "allowed_colors_json": None},
        {"code": "other", "name": "Inna okazja", "allowed_colors_json": None},
    ]
    for o in occasions_data:
        existing = (await db.execute(select(Occasion).where(Occasion.code == o["code"]))).scalar_one_or_none()
        if not existing:
            db.add(Occasion(**o))
    counts["occasions"] = len(occasions_data)

    # ─── PRODUCTS: WINA ───
    wines_data = [
        {"name": "Jagoda Kamczacka z czarną porzeczką", "base_price": 80.50, "wine_color": "czerwone", "wine_type": "półsłodkie", "stock_quantity": 320},
        {"name": "Polski Owoc — Czerwona Porzeczka", "base_price": 62.00, "wine_color": "czerwone", "wine_type": "półsłodkie", "stock_quantity": 150},
        {"name": "Śliwka z nutą cynamonu", "base_price": 74.00, "wine_color": "czerwone", "wine_type": "półwytrawne", "stock_quantity": 85},
        {"name": "Wiśnia z miodem", "base_price": 89.00, "wine_color": "różowe", "wine_type": "półsłodkie", "stock_quantity": 200},
        {"name": "Cabernet Sauvignon Premium", "base_price": 112.00, "wine_color": "czerwone", "wine_type": "wytrawne", "stock_quantity": 45},
        {"name": "Muscat Białe Lekkie", "base_price": 68.00, "wine_color": "białe", "wine_type": "półsłodkie", "stock_quantity": 0, "restock_days": 7},
        {"name": "Merlot Toskański", "base_price": 95.00, "wine_color": "czerwone", "wine_type": "wytrawne", "stock_quantity": 70},
        {"name": "Jabłkowe z miodem", "base_price": 55.00, "wine_color": "białe", "wine_type": "słodkie", "stock_quantity": 400},
        {"name": "Owocowe Musujące", "base_price": 72.00, "wine_color": "białe", "wine_type": "półsłodkie", "stock_quantity": 120},
        {"name": "Cuvée Polskie", "base_price": 88.00, "wine_color": "czerwone", "wine_type": "wytrawne", "stock_quantity": 90},
    ]
    for w in wines_data:
        existing = (await db.execute(select(Product).where(Product.name == w["name"], Product.category == "wine"))).scalar_one_or_none()
        if not existing:
            db.add(Product(category="wine", slot_size=0, **w))
    counts["wines"] = len(wines_data)

    # ─── PRODUCTS: SŁODYCZE ───
    sweets_data = [
        {"name": "Pierniczek świąteczny", "base_price": 8.50, "slot_size": 1, "supplier_id": sup_map.get("Stroiki Jan"), "stock_quantity": 500, "available_colors_json": ["red", "gold", "green", "pastel"]},
        {"name": "Śliwka w czekoladzie", "base_price": 12.00, "slot_size": 1, "supplier_id": sup_map.get("Manufaktura Saska"), "stock_quantity": 800, "available_colors_json": ["red", "gold", "yellow", "green"]},
        {"name": "Migdały w czekoladzie", "base_price": 14.00, "slot_size": 1, "supplier_id": sup_map.get("Manufaktura Saska"), "stock_quantity": 350, "available_colors_json": ["gold", "yellow"]},
        {"name": "Czekolada 60g", "base_price": 9.50, "slot_size": 1, "supplier_id": sup_map.get("Manufaktura Saska"), "stock_quantity": 1200, "available_colors_json": ["red", "gold", "pastel"]},
        {"name": "Czekolada 100g", "base_price": 15.00, "slot_size": 2, "supplier_id": sup_map.get("Manufaktura Saska"), "stock_quantity": 600, "available_colors_json": ["red", "gold"]},
        {"name": "Orzeszki w karmelu", "base_price": 11.00, "slot_size": 1, "supplier_id": sup_map.get("Manufaktura Saska"), "stock_quantity": 420, "available_colors_json": ["craft"]},
    ]
    for s in sweets_data:
        existing = (await db.execute(select(Product).where(Product.name == s["name"], Product.category == "sweet"))).scalar_one_or_none()
        if not existing:
            db.add(Product(category="sweet", **s))
    counts["sweets"] = len(sweets_data)

    # ─── PRODUCTS: DEKORACJE ───
    deco_data = [
        {"name": "Gałązka dekoracyjna", "base_price": 6.50, "slot_size": 1, "supplier_id": sup_map.get("Stroiki Jan"), "stock_quantity": 700, "available_colors_json": ["red", "gold", "green", "pastel"]},
        {"name": "Bombka ozdobna", "base_price": 7.00, "slot_size": 1, "supplier_id": sup_map.get("Stroiki Jan"), "stock_quantity": 300, "available_colors_json": ["red", "blue", "gold"]},
        {"name": "Herbatka premium", "base_price": 10.00, "slot_size": 1, "supplier_id": sup_map.get("Stroiki Jan"), "stock_quantity": 200, "available_colors_json": ["craft"]},
        {"name": "Sopelek czekoladowy", "base_price": 5.00, "slot_size": 1, "supplier_id": sup_map.get("Stroiki Jan"), "stock_quantity": 600, "available_colors_json": ["red", "gold", "blue"]},
    ]
    for d in deco_data:
        existing = (await db.execute(select(Product).where(Product.name == d["name"], Product.category == "decoration"))).scalar_one_or_none()
        if not existing:
            db.add(Product(category="decoration", **d))
    counts["decorations"] = len(deco_data)

    # ─── PRODUCTS: PERSONALIZACJA ───
    pers_data = [
        {"name": "Nadruk logo na opakowaniu", "base_price": 15.00, "stock_quantity": 99999},
        {"name": "Grawerunek na ekokorku", "base_price": 8.00, "stock_quantity": 99999},
    ]
    for p in pers_data:
        existing = (await db.execute(select(Product).where(Product.name == p["name"], Product.category == "personalization"))).scalar_one_or_none()
        if not existing:
            db.add(Product(category="personalization", slot_size=0, **p))
    counts["personalization"] = len(pers_data)

    # ─── PACKAGINGS ───
    pkg_data = [
        {"name": "Pudełko czarne Premium", "packaging_type": "pudełko_czarne", "bottles": 1, "sweet_slots": 5, "price": 26.00, "stock_quantity": 400},
        {"name": "Pudełko czarne na 2 butelki", "packaging_type": "pudełko_czarne", "bottles": 2, "sweet_slots": 6, "price": 38.00, "stock_quantity": 100},
        {"name": "Pudełko kraft ekologiczne", "packaging_type": "kraft", "bottles": 1, "sweet_slots": 4, "price": 18.00, "stock_quantity": 250},
        {"name": "Pudełko kraft na 2 butelki", "packaging_type": "kraft", "bottles": 2, "sweet_slots": 5, "price": 28.00, "stock_quantity": 80},
        {"name": "Skrzynka drewniana 1 butelka", "packaging_type": "skrzynka", "bottles": 1, "sweet_slots": 7, "price": 42.00, "stock_quantity": 60},
        {"name": "Skrzynka drewniana 2 butelki", "packaging_type": "skrzynka", "bottles": 2, "sweet_slots": 9, "price": 56.00, "stock_quantity": 40},
        {"name": "Skrzynka drewniana 4 butelki", "packaging_type": "skrzynka", "bottles": 4, "sweet_slots": 12, "price": 78.00, "stock_quantity": 20},
        {"name": "Tuba elegancka", "packaging_type": "tuba", "bottles": 1, "sweet_slots": 2, "price": 22.00, "stock_quantity": 180},
        {"name": "Box prezentowy XL", "packaging_type": "box_xl", "bottles": 4, "sweet_slots": 14, "price": 68.00, "stock_quantity": 30},
    ]
    for p in pkg_data:
        existing = (await db.execute(select(Packaging).where(Packaging.name == p["name"]))).scalar_one_or_none()
        if not existing:
            db.add(Packaging(**p))
    counts["packagings"] = len(pkg_data)

    # ─── DISCOUNT RULES: WINO ───
    wine_discounts = [
        {"rule_type": "wine", "min_quantity": 1, "max_quantity": 99, "discount_percent": 0},
        {"rule_type": "wine", "min_quantity": 100, "max_quantity": 199, "discount_percent": 5},
        {"rule_type": "wine", "min_quantity": 200, "max_quantity": 299, "discount_percent": 10},
        {"rule_type": "wine", "min_quantity": 300, "max_quantity": 99999, "discount_percent": 20},
    ]
    for d in wine_discounts:
        existing = (await db.execute(
            select(DiscountRule).where(
                DiscountRule.rule_type == d["rule_type"],
                DiscountRule.min_quantity == d["min_quantity"],
            )
        )).scalar_one_or_none()
        if not existing:
            db.add(DiscountRule(**d))

    # ─── DISCOUNT RULES: PERSONALIZACJA (ceny stałe per próg ilościowy, per produkt) ───
    # Logo na opakowaniu: 15/12/9 zł
    # Grawerunek na ekokorku: 8/6/4.50 zł
    await db.flush()  # ensure products are visible for SELECT below
    logo_product = (await db.execute(select(Product).where(Product.name == "Nadruk logo na opakowaniu"))).scalar_one_or_none()
    cork_product = (await db.execute(select(Product).where(Product.name == "Grawerunek na ekokorku"))).scalar_one_or_none()

    pers_discounts = []
    if logo_product:
        pers_discounts += [
            {"rule_type": "personalization", "product_id": logo_product.id, "min_quantity": 1, "max_quantity": 99, "fixed_price": 15.00},
            {"rule_type": "personalization", "product_id": logo_product.id, "min_quantity": 100, "max_quantity": 199, "fixed_price": 12.00},
            {"rule_type": "personalization", "product_id": logo_product.id, "min_quantity": 200, "max_quantity": 99999, "fixed_price": 9.00},
        ]
    if cork_product:
        pers_discounts += [
            {"rule_type": "personalization", "product_id": cork_product.id, "min_quantity": 1, "max_quantity": 99, "fixed_price": 8.00},
            {"rule_type": "personalization", "product_id": cork_product.id, "min_quantity": 100, "max_quantity": 199, "fixed_price": 6.00},
            {"rule_type": "personalization", "product_id": cork_product.id, "min_quantity": 200, "max_quantity": 99999, "fixed_price": 4.50},
        ]
    for d in pers_discounts:
        existing = (await db.execute(
            select(DiscountRule).where(
                DiscountRule.rule_type == d["rule_type"],
                DiscountRule.product_id == d["product_id"],
                DiscountRule.min_quantity == d["min_quantity"],
            )
        )).scalar_one_or_none()
        if not existing:
            db.add(DiscountRule(**d))
    counts["discount_rules"] = len(wine_discounts) + len(pers_discounts)

    await db.commit()
    return counts
