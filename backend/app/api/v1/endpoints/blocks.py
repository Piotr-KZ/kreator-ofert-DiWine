"""
Block library endpoints — categories and templates.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.block_template import BlockCategory, BlockTemplate
from app.services.creator.site_structure import SITE_TYPES

router = APIRouter()


@router.get("/blocks/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BlockCategory).order_by(BlockCategory.order)
    )
    cats = result.scalars().all()
    return [
        {"code": c.code, "name": c.name, "icon": c.icon, "order": c.order}
        for c in cats
    ]


@router.get("/blocks")
async def list_blocks(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(BlockTemplate).where(BlockTemplate.is_active == True)
    if category:
        query = query.where(BlockTemplate.category_code == category)
    result = await db.execute(query.order_by(BlockTemplate.code))
    blocks = result.scalars().all()
    return [
        {
            "code": b.code,
            "category_code": b.category_code,
            "name": b.name,
            "description": b.description,
            "media_type": b.media_type,
            "layout_type": b.layout_type,
            "size": b.size,
            "slots_definition": b.slots_definition,
        }
        for b in blocks
    ]


@router.get("/site-types")
async def list_site_types():
    return SITE_TYPES
