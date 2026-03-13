"""
Block service — seed data, layout tags, and matching helpers.
Brief 33: LAYOUT_TAGS configurator mapping.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockCategory, BlockTemplate

BLOCK_CATEGORIES = [
    {"code": "NA", "name": "Nawigacja", "icon": "menu", "order": -1},
    {"code": "HE", "name": "Hero", "icon": "layout-dashboard", "order": 0},
    {"code": "FI", "name": "O firmie", "icon": "building-2", "order": 1},
    {"code": "OF", "name": "Oferta", "icon": "shopping-bag", "order": 2},
    {"code": "CE", "name": "Cennik", "icon": "tag", "order": 3},
    {"code": "ZE", "name": "Zesp\u00f3\u0142", "icon": "users", "order": 4},
    {"code": "OP", "name": "Opinie", "icon": "message-circle", "order": 5},
    {"code": "FA", "name": "FAQ", "icon": "help-circle", "order": 6},
    {"code": "CT", "name": "CTA", "icon": "zap", "order": 7},
    {"code": "KO", "name": "Kontakt", "icon": "mail", "order": 8},
    {"code": "FO", "name": "Stopka", "icon": "minus", "order": 9},
    {"code": "GA", "name": "Galeria", "icon": "image", "order": 10},
    {"code": "RE", "name": "Realizacje", "icon": "briefcase", "order": 11},
    {"code": "PR", "name": "Proces", "icon": "git-branch", "order": 12},
    {"code": "PB", "name": "Problem", "icon": "alert-triangle", "order": 13},
    {"code": "RO", "name": "Rozwi\u0105zanie", "icon": "check-circle", "order": 14},
    {"code": "KR", "name": "Korzy\u015bci", "icon": "star", "order": 15},
    {"code": "CF", "name": "Cechy", "icon": "list", "order": 16},
    {"code": "OB", "name": "Obiekcje", "icon": "shield", "order": 17},
    {"code": "LO", "name": "Loga klient\u00f3w", "icon": "award", "order": 18},
    {"code": "ST", "name": "Statystyki", "icon": "bar-chart", "order": 19},
]

# Mapping: block type name -> category code
BLOCK_TYPE_TO_CATEGORY = {
    "Nawigacja": "NA",
    "O firmie": "FI",
    "Oferta": "OF",
    "Opinie": "OP",
    "Galeria": "GA",
    "Proces": "PR",
    "FAQ": "FA",
    "Cennik": "CE",
    "Zespol": "ZE",
    "Realizacje": "RE",
    "CTA": "CT",
    "Kontakt": "KO",
    "Problem": "PB",
    "Rozwiazanie": "RO",
    "Korzysci": "KR",
    "Obiekcje": "OB",
    "Statystyki": "ST",
    "Loga": "LO",
    "Stopka": "FO",
}

# Configurator layout tags — from konfigurator-komplet2.jsx
LAYOUT_TAGS = {
    # Photo
    "photo-top-1": {"media": "photo", "position": "top", "columns": 1},
    "photo-top-2": {"media": "photo", "position": "top", "columns": 2},
    "photo-top-3": {"media": "photo", "position": "top", "columns": 3},
    "photo-top-4": {"media": "photo", "position": "top", "columns": 4},
    "photo-bottom-1": {"media": "photo", "position": "bottom", "columns": 1},
    "photo-bottom-2": {"media": "photo", "position": "bottom", "columns": 2},
    "photo-bottom-3": {"media": "photo", "position": "bottom", "columns": 3},
    "photo-bottom-4": {"media": "photo", "position": "bottom", "columns": 4},
    "photo-full-1": {"media": "photo", "position": "full", "columns": 1},
    "photo-full-2": {"media": "photo", "position": "full", "columns": 2},
    "photo-full-3": {"media": "photo", "position": "full", "columns": 3},
    "photo-full-4": {"media": "photo", "position": "full", "columns": 4},
    # Video
    "vid-full": {"media": "video", "layout": "full"},
    "vid-top": {"media": "video", "layout": "top"},
    "vid-left": {"media": "video", "layout": "left"},
    "vid-right": {"media": "video", "layout": "right"},
    # Infographic
    "info-title-2": {"media": "infographic", "variant": "title", "columns": 2},
    "info-title-3": {"media": "infographic", "variant": "title", "columns": 3},
    "info-title-4": {"media": "infographic", "variant": "title", "columns": 4},
    "info-title-text-2": {"media": "infographic", "variant": "title-text", "columns": 2},
    "info-title-text-3": {"media": "infographic", "variant": "title-text", "columns": 3},
    "info-title-text-4": {"media": "infographic", "variant": "title-text", "columns": 4},
    # Table
    "tbl-full": {"media": "table", "layout": "full"},
    "tbl-img-l": {"media": "table", "layout": "image-left"},
    "tbl-img-r": {"media": "table", "layout": "image-right"},
    "tbl-txt-l": {"media": "table", "layout": "text-left"},
    "tbl-txt-r": {"media": "table", "layout": "text-right"},
    # Chart
    "chart-full": {"media": "chart", "layout": "full"},
    "chart-left": {"media": "chart", "layout": "left"},
    "chart-right": {"media": "chart", "layout": "right"},
    # Opinions
    "opin-top-1": {"media": "opinion", "position": "top", "columns": 1},
    "opin-top-2": {"media": "opinion", "position": "top", "columns": 2},
    "opin-top-3": {"media": "opinion", "position": "top", "columns": 3},
    "opin-top-4": {"media": "opinion", "position": "top", "columns": 4},
    "opin-bottom-1": {"media": "opinion", "position": "bottom", "columns": 1},
    "opin-bottom-2": {"media": "opinion", "position": "bottom", "columns": 2},
    "opin-bottom-3": {"media": "opinion", "position": "bottom", "columns": 3},
    "opin-bottom-4": {"media": "opinion", "position": "bottom", "columns": 4},
    # Logos
    "logo-1": {"media": "logo", "rows": 1},
    "logo-2": {"media": "logo", "rows": 2},
    "logo-3": {"media": "logo", "rows": 3},
    # No media
    "text-only": {"media": "none"},
}


async def seed_block_categories(db: AsyncSession) -> int:
    """Seed block categories (idempotent). Returns number of categories created."""
    created = 0
    for cat in BLOCK_CATEGORIES:
        result = await db.execute(
            select(BlockCategory).where(BlockCategory.code == cat["code"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            db.add(BlockCategory(**cat))
            created += 1
        else:
            # Update existing
            for k, v in cat.items():
                setattr(existing, k, v)
    await db.commit()
    return created


async def find_matching_blocks(
    db: AsyncSession,
    category_code: str | None = None,
    media_type: str | None = None,
    layout_type: str | None = None,
    photo_shape: str | None = None,
    text_style: str | None = None,
) -> list[BlockTemplate]:
    """Configurator: criteria → matching blocks."""
    query = select(BlockTemplate).where(BlockTemplate.is_active == True)

    if category_code:
        query = query.where(BlockTemplate.category_code == category_code)
    if media_type:
        query = query.where(BlockTemplate.media_type == media_type)
    if layout_type:
        query = query.where(BlockTemplate.layout_type == layout_type)
    if photo_shape:
        query = query.where(BlockTemplate.photo_shape == photo_shape)
    if text_style:
        query = query.where(BlockTemplate.text_style == text_style)

    result = await db.execute(query.order_by(BlockTemplate.code))
    return list(result.scalars().all())
