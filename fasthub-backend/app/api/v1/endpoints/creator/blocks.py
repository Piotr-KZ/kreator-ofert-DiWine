"""
Creator: Block templates catalog endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.block_template import BlockCategory, BlockTemplate
from app.schemas.creator import (
    BlockCategoryResponse,
    BlockMatchRequest,
    BlockTemplateResponse,
)
from app.services.creator.block_service import BLOCK_TYPE_TO_CATEGORY

router = APIRouter()


@router.get("/blocks/categories", response_model=list[BlockCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """List block categories."""
    result = await db.execute(select(BlockCategory).order_by(BlockCategory.order))
    return result.scalars().all()


@router.get("/blocks", response_model=list[BlockTemplateResponse])
async def list_blocks(
    category: str | None = None,
    media_type: str | None = None,
    layout_type: str | None = None,
    site_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List block templates with optional filters. site_type filters by allowed categories."""
    query = select(BlockTemplate).where(BlockTemplate.is_active == True)

    # Brief 42: filter by site type's allowed categories
    if site_type:
        from app.services.creator.site_type_config import get_site_type_config
        config = get_site_type_config(site_type)
        if config.allowed_block_categories:
            query = query.where(BlockTemplate.category_code.in_(config.allowed_block_categories))

    if category:
        query = query.where(BlockTemplate.category_code == category)
    if media_type:
        query = query.where(BlockTemplate.media_type == media_type)
    if layout_type:
        query = query.where(BlockTemplate.layout_type == layout_type)
    result = await db.execute(query.order_by(BlockTemplate.code))
    return result.scalars().all()


@router.get("/blocks/{code}", response_model=BlockTemplateResponse)
async def get_block(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get block template details (HTML, slots, variants)."""
    result = await db.execute(select(BlockTemplate).where(BlockTemplate.code == code))
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    return block


@router.post("/blocks/match", response_model=list[BlockTemplateResponse])
async def match_blocks(
    data: BlockMatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Find matching blocks by configurator criteria."""
    query = select(BlockTemplate).where(BlockTemplate.is_active == True)
    if data.media_type:
        query = query.where(BlockTemplate.media_type == data.media_type)
    if data.layout_type:
        query = query.where(BlockTemplate.layout_type == data.layout_type)
    if data.photo_shape:
        query = query.where(BlockTemplate.photo_shape == data.photo_shape)
    if data.text_style:
        query = query.where(BlockTemplate.text_style == data.text_style)
    if data.block_type:
        cat_code = BLOCK_TYPE_TO_CATEGORY.get(data.block_type)
        if cat_code:
            query = query.where(BlockTemplate.category_code == cat_code)
    result = await db.execute(query)
    return result.scalars().all()
