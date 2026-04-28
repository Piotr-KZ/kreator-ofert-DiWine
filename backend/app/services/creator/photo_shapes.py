"""
Photo shape presets for Lab Creator.
12 presets — each returns CSS string to apply to <img> or wrapper.
AI selects in Visual Concept, user changes in toolbar dropdown.
"""

PHOTO_SHAPES: dict[str, dict] = {
    "rect": {
        "label": "Prostokąt",
        "css": "border-radius:0;",
        "lock_ratio": False,
    },
    "rounded_sm": {
        "label": "Lekko zaokrąglony",
        "css": "border-radius:8px;",
        "lock_ratio": False,
    },
    "rounded_lg": {
        "label": "Mocno zaokrąglony",
        "css": "border-radius:20px;",
        "lock_ratio": False,
    },
    "circle": {
        "label": "Koło",
        "css": "border-radius:50%;",
        "lock_ratio": True,
    },
    "blob_1": {
        "label": "Blob organiczny 1",
        "css": "border-radius:30% 70% 70% 30% / 30% 30% 70% 70%;",
        "lock_ratio": False,
    },
    "blob_2": {
        "label": "Blob organiczny 2",
        "css": "border-radius:50% 30% 60% 40% / 40% 60% 30% 50%;",
        "lock_ratio": False,
    },
    "blob_3": {
        "label": "Blob organiczny 3",
        "css": "border-radius:60% 40% 30% 70% / 60% 30% 70% 40%;",
        "lock_ratio": False,
    },
    "hexagon": {
        "label": "Sześciokąt",
        "css": "clip-path:polygon(25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%);",
        "lock_ratio": True,
    },
    "diamond": {
        "label": "Romb",
        "css": "clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%);",
        "lock_ratio": True,
    },
    "slant_right": {
        "label": "Ukośny",
        "css": "clip-path:polygon(8% 0%,100% 0%,92% 100%,0% 100%);",
        "lock_ratio": False,
    },
    "arch_top": {
        "label": "Łuk górny",
        "css": "border-radius:50% 50% 8px 8px;",
        "lock_ratio": False,
    },
    "rounded_corners": {
        "label": "Ścięte rogi",
        "css": "border-radius:var(--photo-corner-radius, 8px);",
        "lock_ratio": False,
    },
}


def get_photo_shape_css(shape_id: str) -> str:
    """Return CSS string for a photo shape preset."""
    shape = PHOTO_SHAPES.get(shape_id)
    if not shape:
        return PHOTO_SHAPES["rounded_sm"]["css"]
    return shape["css"]


def get_photo_shape_info(shape_id: str) -> dict | None:
    """Return full shape info (label, css, lock_ratio)."""
    return PHOTO_SHAPES.get(shape_id)


def get_available_photo_shapes() -> list[dict]:
    """Return all shapes as list with id included."""
    return [{"id": k, **v} for k, v in PHOTO_SHAPES.items()]
