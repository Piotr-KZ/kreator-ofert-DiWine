"""
Site structure configuration per type — max sections, required, forbidden.
From Brief 42/43.
"""

STRUCTURE_CONFIG = {
    "company_card": {
        "label": "Wizytowka firmowa",
        "max_sections": 6,
        "required": ["NA", "HE", "KO"],
        "forbidden": ["FA", "ZE", "CE", "PB", "OB"],
        "allowed_categories": ["NA", "HE", "FI", "KO", "FO", "CT", "OF"],
    },
    "company": {
        "label": "Strona firmowa",
        "max_sections": 12,
        "required": ["NA", "HE", "OF", "KO", "FO"],
        "forbidden": [],
        "allowed_categories": [],  # all allowed
    },
    "lp_product": {
        "label": "Landing page (produkt)",
        "max_sections": 10,
        "required": ["NA", "HE", "OF", "CT", "KO"],
        "forbidden": ["ZE"],
        "allowed_categories": ["NA", "HE", "PB", "RO", "KR", "CF", "OB", "OF", "PR", "OP", "CT", "KO", "FO", "ST", "RE"],
    },
    "lp_service": {
        "label": "Landing page (usluga)",
        "max_sections": 10,
        "required": ["NA", "HE", "OF", "CT", "KO"],
        "forbidden": ["ZE"],
        "allowed_categories": ["NA", "HE", "PB", "RO", "KR", "CF", "OB", "OF", "PR", "OP", "CT", "KO", "FO", "ST", "RE"],
    },
    "expert": {
        "label": "Strona eksperta",
        "max_sections": 10,
        "required": ["NA", "HE", "OF", "KO"],
        "forbidden": [],
        "allowed_categories": [],  # all allowed
    },
}

SITE_TYPES = [
    {"value": k, "label": v["label"]}
    for k, v in STRUCTURE_CONFIG.items()
]


def get_structure_config(site_type: str) -> dict:
    return STRUCTURE_CONFIG.get(site_type, STRUCTURE_CONFIG["company"])
