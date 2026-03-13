"""
Pydantic schemas for WebCreator endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Project
# ============================================================================

class ProjectCreate(BaseModel):
    model_config = {"strict": True}

    name: str = Field(..., min_length=1, max_length=255)
    site_type: Optional[str] = None


class ProjectUpdate(BaseModel):
    model_config = {"strict": True}

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    current_step: Optional[int] = None
    brief_json: Optional[dict] = None
    style_json: Optional[dict] = None
    config_json: Optional[dict] = None
    check_json: Optional[dict] = None


class ProjectResponse(BaseModel):
    id: UUID
    organization_id: UUID
    created_by: UUID
    name: str
    site_type: Optional[str] = None
    status: str
    current_step: int
    brief_json: Optional[dict] = None
    materials_meta: Optional[dict] = None
    style_json: Optional[dict] = None
    validation_json: Optional[dict] = None
    config_json: Optional[dict] = None
    check_json: Optional[dict] = None
    domain: Optional[str] = None
    custom_domain: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListItem(BaseModel):
    id: UUID
    name: str
    site_type: Optional[str] = None
    status: str
    current_step: int
    domain: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Brief (step 1)
# ============================================================================

class BriefData(BaseModel):
    site_type: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    b2b_b2c: Optional[str] = None
    usp: Optional[list[str]] = None
    brand_positioning: Optional[str] = None
    communication_style: Optional[str] = None
    site_goal: Optional[str] = None
    desired_impressions: Optional[dict] = None
    pages: Optional[list[str]] = None
    content_sections: Optional[list[str]] = None
    custom_wishes: Optional[str] = None


# ============================================================================
# Style (step 3)
# ============================================================================

class StyleData(BaseModel):
    palette_preset: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    color_accent: Optional[str] = None
    heading_font: Optional[str] = None
    body_font: Optional[str] = None
    font_sizes: Optional[dict] = None
    section_themes: Optional[dict] = None
    border_radius: Optional[str] = None


# ============================================================================
# Materials (step 2)
# ============================================================================

class LinkMaterial(BaseModel):
    model_config = {"strict": True}

    url: str
    type: str  # link, inspiration, competitor
    description: Optional[str] = None


class MaterialResponse(BaseModel):
    id: UUID
    project_id: UUID
    type: str
    file_url: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    external_url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Sections (steps 5-6)
# ============================================================================

class SectionCreate(BaseModel):
    model_config = {"strict": True}

    block_code: str
    position: Optional[int] = None
    variant: Optional[str] = "A"
    slots_json: Optional[dict] = None
    variant_config: Optional[dict] = None


class SectionUpdate(BaseModel):
    model_config = {"strict": True}

    block_code: Optional[str] = None
    position: Optional[int] = None
    variant: Optional[str] = None
    slots_json: Optional[dict] = None
    variant_config: Optional[dict] = None
    is_visible: Optional[bool] = None


class SectionResponse(BaseModel):
    id: UUID
    project_id: UUID
    block_code: str
    position: int
    variant: str
    slots_json: Optional[dict] = None
    variant_config: Optional[dict] = None
    is_visible: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReorderData(BaseModel):
    order: list[UUID]


# ============================================================================
# Block Templates
# ============================================================================

class BlockMatchRequest(BaseModel):
    block_type: Optional[str] = None
    media_type: Optional[str] = None
    layout_type: Optional[str] = None
    photo_shape: Optional[str] = None
    text_style: Optional[str] = None


class BlockCategoryResponse(BaseModel):
    id: UUID
    code: str
    name: str
    icon: Optional[str] = None
    order: int

    model_config = ConfigDict(from_attributes=True)


class BlockTemplateResponse(BaseModel):
    id: UUID
    code: str
    category_code: str
    name: Optional[str] = None
    description: Optional[str] = None
    html_template: str
    css: Optional[str] = None
    slots_definition: list | dict
    media_type: Optional[str] = None
    layout_type: Optional[str] = None
    photo_shape: Optional[str] = None
    text_style: Optional[str] = None
    variants: Optional[dict] = None
    size: str
    responsive: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
