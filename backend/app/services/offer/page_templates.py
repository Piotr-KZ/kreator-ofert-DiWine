"""
Offer page templates — predefined block structures for offer pages.
Each template = list of blocks with slot mapping instructions.

User picks template → system creates Project → fills slots from offer data.
"""

# slot_source tells auto-builder where to get data:
#   "offer.X" = from offer dict
#   "client.X" = from client dict
#   "set" = repeated per offer set
#   "text:block_type:occasion" = from OfferTextTemplate
#   "static:value" = hardcoded value
#   "unsplash:query" = photo from Unsplash

TEMPLATES = {
    "standard": {
        "name": "Standard",
        "description": "Klasyczna oferta: nagłówek, powitanie, zestawy, dlaczego my, zakończenie, CTA.",
        "blocks": [
            {
                "block_code": "NO1",
                "slots_map": {
                    "offer_number": "offer.offer_number",
                    "date": "offer.date",
                    "expires": "offer.expires_at",
                    "client_name": "client.company_name",
                    "client_logo_url": "client.logo_url",
                    "occasion_name": "offer.occasion_name",
                    "bg_photo_url": "unsplash:wine gift elegant christmas",
                },
            },
            {
                "block_code": "DW3",
                "slots_map": {
                    "heading": "static:",
                    "body": "text:greeting:occasion",
                },
            },
            {
                "block_code": "DW1",
                "repeat": "sets",
            },
            {
                "block_code": "DW4",
                "slots_map": {
                    "heading": "static:Dlaczego my",
                    "body": "text:why_us",
                },
            },
            {
                "block_code": "DW3",
                "slots_map": {
                    "heading": "static:",
                    "body": "text:closing",
                },
            },
            {
                "block_code": "CTA1",
                "slots_map": {
                    "heading": "static:Zainteresowany?",
                    "body": "static:Skontaktuj się z nami — chętnie dopasujemy ofertę do Twoich potrzeb.",
                    "cta_text": "static:Akceptuję ofertę",
                    "cta_url": "offer.accept_url",
                    "contact_name": "offer.contact_name",
                    "contact_email": "offer.contact_email",
                    "contact_phone": "offer.contact_phone",
                },
            },
        ],
    },

    "premium": {
        "name": "Premium",
        "description": "Rozbudowana oferta z ciekawostkami i większą ilością treści.",
        "blocks": [
            {"block_code": "NO2", "slots_map": {
                "offer_number": "offer.offer_number", "date": "offer.date",
                "client_name": "client.company_name", "client_logo_url": "client.logo_url",
                "occasion_name": "offer.occasion_name",
                "bg_photo_url": "unsplash:luxury wine gift box premium",
            }},
            {"block_code": "DW3", "slots_map": {"heading": "static:", "body": "text:greeting:occasion"}},
            {"block_code": "DW5", "slots_map": {"heading": "static:Czy wiesz, że...", "body": "text:fun_fact"}},
            {"block_code": "DW2", "repeat": "sets"},
            {"block_code": "DW4", "slots_map": {"heading": "static:Dlaczego my", "body": "text:why_us"}},
            {"block_code": "DW5", "slots_map": {"heading": "static:Ciekawostka", "body": "text:fun_fact"}},
            {"block_code": "DW3", "slots_map": {"heading": "static:", "body": "text:closing"}},
            {"block_code": "CTA1", "slots_map": {
                "heading": "static:Gotowy na wyjątkowe prezenty?",
                "body": "static:Zaakceptuj ofertę lub skontaktuj się — dostosujemy wszystko do Twoich potrzeb.",
                "cta_text": "static:Akceptuję ofertę",
                "cta_url": "offer.accept_url",
                "contact_name": "offer.contact_name",
                "contact_email": "offer.contact_email",
                "contact_phone": "offer.contact_phone",
            }},
        ],
    },

    "quick": {
        "name": "Szybka wycena",
        "description": "Minimum treści — same zestawy z cenami i CTA.",
        "blocks": [
            {"block_code": "NO1", "slots_map": {
                "offer_number": "offer.offer_number", "date": "offer.date",
                "client_name": "client.company_name", "occasion_name": "offer.occasion_name",
                "bg_photo_url": "unsplash:wine gift box",
            }},
            {"block_code": "DW1", "repeat": "sets"},
            {"block_code": "DW3", "slots_map": {"heading": "static:", "body": "text:closing"}},
            {"block_code": "CTA1", "slots_map": {
                "heading": "static:Zainteresowany?",
                "cta_text": "static:Akceptuję ofertę",
                "cta_url": "offer.accept_url",
                "contact_email": "offer.contact_email",
                "contact_phone": "offer.contact_phone",
            }},
        ],
    },

    "presentation": {
        "name": "Prezentacyjna",
        "description": "Na spotkanie lub wydruk — duże zdjęcia, pełne opisy.",
        "blocks": [
            {"block_code": "NO2", "slots_map": {
                "offer_number": "offer.offer_number", "date": "offer.date",
                "client_name": "client.company_name", "client_logo_url": "client.logo_url",
                "occasion_name": "offer.occasion_name",
                "bg_photo_url": "unsplash:premium wine tasting elegant",
            }},
            {"block_code": "DW3", "slots_map": {"heading": "static:", "body": "text:greeting:occasion"}},
            {"block_code": "DW4", "slots_map": {"heading": "static:O nas", "body": "text:why_us"}},
            {"block_code": "DW5", "slots_map": {"heading": "static:Czy wiesz, że...", "body": "text:fun_fact"}},
            {"block_code": "DW2", "repeat": "sets"},
            {"block_code": "DW5", "slots_map": {"heading": "static:Ciekawostka", "body": "text:fun_fact"}},
            {"block_code": "DW3", "slots_map": {"heading": "static:", "body": "text:closing"}},
            {"block_code": "CTA1", "slots_map": {
                "heading": "static:Następny krok",
                "body": "static:Zaakceptuj ofertę online lub umów się na prezentację próbek.",
                "cta_text": "static:Akceptuję ofertę",
                "cta_url": "offer.accept_url",
                "contact_name": "offer.contact_name",
                "contact_email": "offer.contact_email",
                "contact_phone": "offer.contact_phone",
            }},
        ],
    },
}


def get_template(template_id: str) -> dict | None:
    return TEMPLATES.get(template_id)

def list_templates() -> list[dict]:
    return [
        {"id": k, "name": v["name"], "description": v["description"],
         "block_count": len(v["blocks"])}
        for k, v in TEMPLATES.items()
    ]
