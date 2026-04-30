"""
Offer calculator — price computation, discounts, capacity validation.
Pure business logic, no DB queries (gets data as arguments).
"""

from typing import Optional


def get_wine_discount_percent(quantity: int, discount_rules: list[dict]) -> float:
    """Get wine discount % based on quantity from discount_rules table."""
    for rule in discount_rules:
        if rule["rule_type"] == "wine" and rule["min_quantity"] <= quantity <= rule["max_quantity"]:
            return rule.get("discount_percent", 0) or 0
    return 0


def get_personalization_price(product_id: str, quantity: int, discount_rules: list[dict]) -> float:
    """Get personalization fixed price for given quantity from discount_rules table."""
    for rule in discount_rules:
        if (
            rule["rule_type"] == "personalization"
            and rule.get("product_id") == product_id
            and rule["min_quantity"] <= quantity <= rule["max_quantity"]
        ):
            return rule.get("fixed_price", 0) or 0
    return 0


def calc_wine_price(base_price: float, discount_percent: float) -> float:
    """Calculate wine price after discount."""
    return round(base_price * (1 - discount_percent / 100), 2)


def calc_set_price(
    items: list[dict],
    packaging_price: float,
    quantity: int,
    discount_rules: list[dict],
) -> dict:
    """
    Calculate full set price.

    items: list of {item_type, base_price, product_id}
    Returns: {packaging, wines, sweets, personalization, unit_total, grand_total, items_detail}
    """
    wine_discount = get_wine_discount_percent(quantity, discount_rules)

    wines_total = 0.0
    sweets_total = 0.0
    pers_total = 0.0
    items_detail = []

    for item in items:
        item_type = item["item_type"]
        base_price = item["base_price"]
        product_id = item.get("product_id")

        if item_type == "wine":
            final_price = calc_wine_price(base_price, wine_discount)
            wines_total += final_price
            items_detail.append({**item, "final_price": final_price, "discount": f"{wine_discount}%"})

        elif item_type == "personalization":
            final_price = get_personalization_price(product_id, quantity, discount_rules)
            if final_price == 0:
                final_price = base_price  # fallback to base
            pers_total += final_price
            items_detail.append({**item, "final_price": final_price})

        else:  # sweet, decoration
            sweets_total += base_price
            items_detail.append({**item, "final_price": base_price})

    unit_total = round(packaging_price + wines_total + sweets_total + pers_total, 2)
    grand_total = round(unit_total * quantity, 2)

    return {
        "packaging": packaging_price,
        "wines": round(wines_total, 2),
        "sweets": round(sweets_total, 2),
        "personalization": round(pers_total, 2),
        "unit_total": unit_total,
        "grand_total": grand_total,
        "wine_discount_percent": wine_discount,
        "items_detail": items_detail,
    }


def validate_set_capacity(
    packaging_bottles: int,
    packaging_sweet_slots: int,
    wines_count: int,
    sweets_slot_sum: int,
) -> list[str]:
    """
    Validate that set contents fit in packaging.
    Returns list of warning messages (empty = OK).
    """
    warnings = []
    if wines_count > packaging_bottles:
        warnings.append(
            f"Za dużo win: {wines_count}/{packaging_bottles} butelek. "
            f"Usuń {wines_count - packaging_bottles} butelkę/i."
        )
    if sweets_slot_sum > packaging_sweet_slots:
        warnings.append(
            f"Za dużo dodatków: {sweets_slot_sum}/{packaging_sweet_slots} slotów. "
            f"Usuń {sweets_slot_sum - packaging_sweet_slots} slot/ów."
        )
    return warnings


def generate_offer_number(year: int, month: int, sequence: int) -> str:
    """Generate offer number in format OF/YYYY/MM/NNNN."""
    return f"OF/{year}/{month:02d}/{sequence:04d}"
