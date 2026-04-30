"""
HTML template for offer PDF.
Renders complete styled HTML from offer data — ready for weasyprint conversion.
"""

from datetime import datetime
from typing import Optional


def _format_price(price: float) -> str:
    """Format price as Polish currency string."""
    return f"{price:,.2f}".replace(",", " ").replace(".", ",")


def _color_hex(color_code: Optional[str], colors: list[dict]) -> str:
    """Get hex value for color code."""
    if not color_code:
        return "#6B7280"
    for c in colors:
        if c["code"] == color_code:
            return c["hex_value"]
    return "#6B7280"


def _wine_color_hex(wine_color: Optional[str]) -> str:
    """Get background hex for wine type."""
    return {
        "czerwone": "#991B1B",
        "białe": "#FEF9E7",
        "różowe": "#FBCFE8",
        "pomarańczowe": "#EA580C",
    }.get(wine_color or "", "#6B7280")


def _wine_text_color(wine_color: Optional[str]) -> str:
    """Get text color for wine background."""
    return {
        "czerwone": "#ffffff",
        "białe": "#78350F",
        "różowe": "#831843",
        "pomarańczowe": "#ffffff",
    }.get(wine_color or "", "#ffffff")


def render_offer_pdf_html(
    offer: dict,
    client: dict,
    sets: list[dict],
    products: dict,       # {product_id: product_dict}
    packagings: dict,     # {packaging_id: packaging_dict}
    colors: list[dict],
    occasion_name: str,
    wine_discount_percent: float,
) -> str:
    """
    Render complete HTML for offer PDF.

    Args:
        offer: offer data dict
        client: client data dict
        sets: list of set dicts with items
        products: lookup dict by product_id
        packagings: lookup dict by packaging_id
        colors: list of color dicts
        occasion_name: display name of occasion
        wine_discount_percent: current wine discount %

    Returns: Complete HTML string ready for weasyprint
    """

    now = datetime.utcnow()
    date_str = now.strftime("%d.%m.%Y")

    # Build sets HTML
    sets_html = ""
    for i, s in enumerate(sets):
        pkg = packagings.get(s.get("packaging_id", ""), {})
        items_rows = ""

        # Packaging row
        if pkg:
            items_rows += f"""
            <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:#6366F1;margin-right:8px;"></span>
                    {pkg.get("name", "")}
                </td>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;">Opakowanie</td>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;text-align:right;font-weight:600;">{_format_price(pkg.get("price", 0))} zł</td>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;text-align:right;color:#6B7280;">{_format_price(pkg.get("price", 0) * offer.get("quantity", 1))} zł</td>
            </tr>"""

        # Items
        for item in s.get("items", []):
            prod = products.get(item.get("product_id", ""), {})
            prod_name = prod.get("name", "Produkt")
            item_type = item.get("item_type", "")
            color_code = item.get("color_code", "")
            color_name = ""
            color_dot = ""

            # Type label
            type_labels = {"wine": "Wino", "sweet": "Słodycze", "decoration": "Dodatek", "personalization": "Personalizacja"}
            type_label = type_labels.get(item_type, item_type)

            # Color dot
            if color_code:
                hex_val = _color_hex(color_code, colors)
                if item_type == "wine":
                    hex_val = _wine_color_hex(color_code)
                for c in colors:
                    if c["code"] == color_code:
                        color_name = f" ({c['name']})"
                color_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{hex_val};margin-right:8px;"></span>'
            else:
                color_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:#6366F1;margin-right:8px;"></span>'

            unit_price = item.get("unit_price", 0)
            total = unit_price * offer.get("quantity", 1)

            items_rows += f"""
            <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;">
                    {color_dot}{prod_name}{color_name}
                </td>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;">{type_label}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;text-align:right;font-weight:600;">{_format_price(unit_price)} zł</td>
                <td style="padding:8px 12px;border-bottom:1px solid #E5E7EB;text-align:right;color:#6B7280;">{_format_price(total)} zł</td>
            </tr>"""

        # Budget info
        budget = s.get("budget_per_unit")
        budget_html = ""
        if budget:
            unit_p = s.get("unit_price", 0)
            if unit_p <= budget:
                budget_html = f'<span style="color:#16A34A;font-size:12px;margin-left:12px;">W budżecie ({_format_price(budget)} zł)</span>'
            else:
                budget_html = f'<span style="color:#DC2626;font-size:12px;margin-left:12px;">Ponad budżet ({_format_price(budget)} zł)</span>'

        sets_html += f"""
        <div style="margin-bottom:32px;page-break-inside:avoid;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <h3 style="font-size:18px;font-weight:700;color:#1F2937;margin:0;">
                    {s.get("name", f"Zestaw {i+1}")}{budget_html}
                </h3>
                <div style="text-align:right;">
                    <div style="font-size:20px;font-weight:700;color:#4F46E5;">{_format_price(s.get("unit_price", 0))} zł<span style="font-size:12px;color:#6B7280;font-weight:400;"> / szt.</span></div>
                    <div style="font-size:13px;color:#6B7280;">{_format_price(s.get("total_price", 0))} zł razem</div>
                </div>
            </div>

            <table style="width:100%;border-collapse:collapse;font-size:14px;">
                <thead>
                    <tr style="background:#F9FAFB;">
                        <th style="padding:8px 12px;text-align:left;font-weight:600;color:#6B7280;font-size:12px;border-bottom:2px solid #E5E7EB;">Pozycja</th>
                        <th style="padding:8px 12px;text-align:left;font-weight:600;color:#6B7280;font-size:12px;border-bottom:2px solid #E5E7EB;">Typ</th>
                        <th style="padding:8px 12px;text-align:right;font-weight:600;color:#6B7280;font-size:12px;border-bottom:2px solid #E5E7EB;">Cena / szt.</th>
                        <th style="padding:8px 12px;text-align:right;font-weight:600;color:#6B7280;font-size:12px;border-bottom:2px solid #E5E7EB;">× {offer.get("quantity", 1)}</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows}
                </tbody>
                <tfoot>
                    <tr style="background:#EEF2FF;">
                        <td colspan="2" style="padding:10px 12px;font-weight:700;color:#1F2937;">RAZEM</td>
                        <td style="padding:10px 12px;text-align:right;font-weight:700;color:#4F46E5;font-size:16px;">{_format_price(s.get("unit_price", 0))} zł</td>
                        <td style="padding:10px 12px;text-align:right;font-weight:700;color:#4F46E5;">{_format_price(s.get("total_price", 0))} zł</td>
                    </tr>
                </tfoot>
            </table>
        </div>"""

    # Grand total across all sets
    grand_total = sum(s.get("total_price", 0) for s in sets)

    # Full HTML
    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 20mm 18mm 25mm 18mm;
            @bottom-center {{
                content: "Strona " counter(page) " z " counter(pages);
                font-size: 10px;
                color: #9CA3AF;
            }}
        }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #1F2937;
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>

    <!-- HEADER -->
    <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:20px;border-bottom:3px solid #4F46E5;margin-bottom:32px;">
        <div>
            <div style="font-size:28px;font-weight:700;color:#4F46E5;">OFERTA</div>
            <div style="font-size:13px;color:#6B7280;margin-top:4px;">{offer.get("offer_number", "")}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:13px;color:#6B7280;">Data wystawienia: {date_str}</div>
            <div style="font-size:13px;color:#6B7280;">Ważna do: {offer.get("expires_at", "—")}</div>
        </div>
    </div>

    <!-- CLIENT + PARAMS -->
    <div style="display:flex;gap:32px;margin-bottom:32px;">
        <div style="flex:1;background:#F9FAFB;border-radius:8px;padding:16px;">
            <div style="font-size:12px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">Klient</div>
            <div style="font-size:16px;font-weight:700;color:#1F2937;">{client.get("company_name", "")}</div>
            {f'<div style="font-size:13px;color:#6B7280;">NIP: {client.get("nip", "")}</div>' if client.get("nip") else ""}
            {f'<div style="font-size:13px;color:#6B7280;">{client.get("contact_person", "")}</div>' if client.get("contact_person") else ""}
            {f'<div style="font-size:13px;color:#6B7280;">{client.get("contact_role", "")}</div>' if client.get("contact_role") else ""}
            {f'<div style="font-size:13px;color:#6B7280;">{client.get("email", "")}</div>' if client.get("email") else ""}
            {f'<div style="font-size:13px;color:#6B7280;">{client.get("phone", "")}</div>' if client.get("phone") else ""}
        </div>
        <div style="flex:1;background:#F9FAFB;border-radius:8px;padding:16px;">
            <div style="font-size:12px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">Parametry</div>
            <div style="font-size:14px;color:#1F2937;"><strong>Ilość prezentów:</strong> {offer.get("quantity", 0)} szt.</div>
            <div style="font-size:14px;color:#1F2937;"><strong>Okazja:</strong> {occasion_name}</div>
            {f'<div style="font-size:14px;color:#1F2937;"><strong>Termin:</strong> {offer.get("deadline", "")}</div>' if offer.get("deadline") else ""}
            {f'<div style="font-size:14px;color:#1F2937;"><strong>Dostawa:</strong> {offer.get("delivery_address", "")}</div>' if offer.get("delivery_address") else ""}
            <div style="font-size:14px;color:#1F2937;"><strong>Rabat na wino:</strong> {wine_discount_percent}%</div>
            <div style="font-size:14px;color:#1F2937;"><strong>Wariantów:</strong> {len(sets)}</div>
        </div>
    </div>

    <!-- SETS -->
    <div style="margin-bottom:24px;">
        <h2 style="font-size:20px;font-weight:700;color:#1F2937;margin:0 0 16px 0;padding-bottom:8px;border-bottom:1px solid #E5E7EB;">
            Zestawy prezentowe
        </h2>
        {sets_html}
    </div>

    <!-- GRAND TOTAL -->
    <div style="background:#4F46E5;color:#ffffff;border-radius:8px;padding:16px;display:flex;align-items:center;justify-content:space-between;margin-bottom:32px;">
        <div style="font-size:14px;font-weight:600;">Suma wszystkich wariantów</div>
        <div style="font-size:22px;font-weight:700;">{_format_price(grand_total)} zł netto</div>
    </div>

    <!-- FOOTER NOTE -->
    <div style="font-size:12px;color:#9CA3AF;border-top:1px solid #E5E7EB;padding-top:16px;">
        <p>Wszystkie ceny podane w PLN netto (bez VAT). Oferta ważna 14 dni od daty wystawienia.</p>
        <p>Dokument wygenerowany automatycznie przez OfferCreator.</p>
    </div>

</body>
</html>"""

    return html
