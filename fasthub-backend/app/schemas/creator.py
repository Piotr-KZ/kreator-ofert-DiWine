"""
Pydantic schemas for WebCreator endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("Only http/https URLs allowed")
        return v


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

# ============================================================================
# Config (step 7)
# ============================================================================

class FormsConfig(BaseModel):
    contact_email: Optional[str] = None
    thank_you_message: Optional[str] = None
    thank_you_url: Optional[str] = None
    send_email_notification: bool = True
    fields: Optional[list[dict]] = None


class SocialConfig(BaseModel):
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None


class TrackingConfig(BaseModel):
    ga4_id: Optional[str] = Field(None, max_length=30, pattern=r'^[a-zA-Z0-9_-]+$')
    gtm_id: Optional[str] = Field(None, max_length=30, pattern=r'^[a-zA-Z0-9_-]+$')
    fb_pixel_id: Optional[str] = Field(None, max_length=30, pattern=r'^[a-zA-Z0-9_-]+$')
    hotjar_id: Optional[str] = Field(None, max_length=30, pattern=r'^[a-zA-Z0-9_-]+$')
    linkedin_id: Optional[str] = Field(None, max_length=30, pattern=r'^[a-zA-Z0-9_-]+$')
    gsc_verification: Optional[str] = Field(None, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    custom_head: Optional[str] = Field(None, max_length=5000)
    custom_body: Optional[str] = Field(None, max_length=5000)


class SeoConfig(BaseModel):
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
    tracking: Optional[TrackingConfig] = None


class CookieBanner(BaseModel):
    enabled: bool = False
    style: str = "bar"  # bar, modal, corner
    text: Optional[str] = None


class RodoClause(BaseModel):
    enabled: bool = False
    text: Optional[str] = None


class LegalSource(BaseModel):
    source: str = "none"  # ai, own, none
    html: Optional[str] = None


class LegalConfig(BaseModel):
    privacy_policy: Optional[LegalSource] = None
    terms: Optional[LegalSource] = None
    cookie_banner: Optional[CookieBanner] = None
    rodo: Optional[RodoClause] = None


class FtpConfig(BaseModel):
    host: Optional[str] = None
    port: int = 21
    username: Optional[str] = None
    password: Optional[str] = None
    path: Optional[str] = None


class HostingConfig(BaseModel):
    domain_type: str = "subdomain"  # subdomain, custom
    subdomain: Optional[str] = None
    custom_domain: Optional[str] = None
    deploy_method: str = "auto"  # auto, ftp, zip
    ftp: Optional[FtpConfig] = None


class ConfigData(BaseModel):
    forms: Optional[FormsConfig] = None
    social: Optional[SocialConfig] = None
    seo: Optional[SeoConfig] = None
    legal: Optional[LegalConfig] = None
    hosting: Optional[HostingConfig] = None


# ============================================================================
# Readiness (step 8)
# ============================================================================

class CheckItem(BaseModel):
    key: str
    status: str  # pass, warn, error
    message: str
    suggestion: Optional[str] = None
    fix_tab: Optional[str] = None


class ReadinessResponse(BaseModel):
    checks: list[CheckItem]
    can_publish: bool
    score: int


# ============================================================================
# Publishing (step 9)
# ============================================================================

class PublishResponse(BaseModel):
    subdomain: str
    url: str
    status: str
    published_at: datetime


class PublishedSiteResponse(BaseModel):
    id: UUID
    project_id: UUID
    subdomain: Optional[str] = None
    custom_domain: Optional[str] = None
    is_active: bool
    published_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Form Submissions
# ============================================================================

class FormSubmissionResponse(BaseModel):
    id: UUID
    site_id: UUID
    data_json: dict
    ip: Optional[str] = None
    read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


# ============================================================================
# Dashboard: Site Integrations
# ============================================================================


class SiteIntegrationCreate(BaseModel):
    provider: str = Field(..., max_length=50)
    config_json: Optional[dict] = None


class SiteIntegrationResponse(BaseModel):
    id: UUID
    site_id: UUID
    provider: str
    status: str
    config_json: Optional[dict] = None
    connected_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Dashboard: Project Stats
# ============================================================================


class DailyVisitors(BaseModel):
    date: str
    count: int


class TrafficSource(BaseModel):
    source: str
    percentage: float


class ProjectStatsResponse(BaseModel):
    period: str
    visitors: int = 0
    leads: int = 0
    bounce_rate: Optional[float] = None
    avg_time_on_site: Optional[float] = None
    published_at: Optional[datetime] = None
    daily_visitors: list[DailyVisitors] = Field(default_factory=list)
    traffic_sources: list[TrafficSource] = Field(default_factory=list)


# ============================================================================
# Dashboard: Form submission update
# ============================================================================


class FormSubmissionUpdate(BaseModel):
    read: Optional[bool] = None
    status: Optional[str] = None  # new, read, answered
