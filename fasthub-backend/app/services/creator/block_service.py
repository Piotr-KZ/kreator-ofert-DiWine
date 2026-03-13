"""
Block service — seed data and helpers for block categories/templates.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockCategory

BLOCK_CATEGORIES = [
    {"code": "HE", "name": "Hero", "icon": "layout-dashboard", "order": 0},
    {"code": "FI", "name": "O firmie", "icon": "building-2", "order": 1},
    {"code": "OF", "name": "Oferta", "icon": "shopping-bag", "order": 2},
    {"code": "CE", "name": "Cennik", "icon": "tag", "order": 3},
    {"code": "ZE", "name": "Zesp\u00f3\u0142", "icon": "users", "order": 4},
    {"code": "OP", "name": "Opinie", "icon": "message-circle", "order": 5},
    {"code": "FA", "name": "FAQ", "icon": "help-circle", "order": 6},
    {"code": "CT", "name": "CTA", "icon": "zap", "order": 7},
    {"code": "KO", "name": "Kontakt", "icon": "mail", "order": 8},
    {"code": "ST", "name": "Stopka", "icon": "minus", "order": 9},
    {"code": "GA", "name": "Galeria", "icon": "image", "order": 10},
    {"code": "RE", "name": "Realizacje", "icon": "briefcase", "order": 11},
    {"code": "PR", "name": "Proces", "icon": "git-branch", "order": 12},
    {"code": "PB", "name": "Problem", "icon": "alert-triangle", "order": 13},
    {"code": "RO", "name": "Rozwi\u0105zanie", "icon": "check-circle", "order": 14},
    {"code": "KR", "name": "Korzy\u015bci", "icon": "star", "order": 15},
    {"code": "CF", "name": "Cechy", "icon": "list", "order": 16},
    {"code": "OB", "name": "Obiekcje", "icon": "shield", "order": 17},
    {"code": "LO", "name": "Loga klient\u00f3w", "icon": "award", "order": 18},
    {"code": "ST2", "name": "Statystyki", "icon": "bar-chart", "order": 19},
]

# Mapping: block type name -> category code
BLOCK_TYPE_TO_CATEGORY = {
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
    "Statystyki": "ST2",
    "Loga": "LO",
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
    if created:
        await db.commit()
    return created
