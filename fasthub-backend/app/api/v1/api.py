"""
API v1 router aggregator
Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    admin_webcreator,
    api_tokens,
    auth,
    dunning,
    gus,
    health,
    invoices,
    members,
    organizations,
    payments,
    sessions,
    subscription_status,
    token_admin,
    two_factor,
    users,
    webhook_config,
)
from app.api.v1.endpoints.creator import ai as creator_ai
from app.api.v1.endpoints.creator import config as creator_config
from app.api.v1.endpoints.creator import publishing as creator_publishing
from app.api.v1.endpoints.creator import forms as creator_forms
from app.api.v1.endpoints.creator import integrations as creator_integrations
from app.api.v1.endpoints.creator import stats as creator_stats
from app.api.v1.endpoints.creator import blocks as creator_blocks
from app.api.v1.endpoints.creator import stock_photos as creator_stock_photos
from app.api.v1.endpoints.creator import briefs as creator_briefs
from app.api.v1.endpoints.creator import materials as creator_materials
from app.api.v1.endpoints.creator import projects as creator_projects
from app.api.v1.endpoints.creator import sections as creator_sections
from app.api.v1.endpoints.creator import styles as creator_styles
from app.api.v1.endpoints.creator import tracking as creator_tracking
from app.api.v1.endpoints.creator import google_integrations as creator_google
from app.api.v1.endpoints.creator import site_type_config as creator_site_type_config
from fasthub_core.billing.api import router as billing_router
from fasthub_core.rbac import rbac_router

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(members.router, prefix="", tags=["Members"])  # No prefix, routes defined in endpoint
api_router.include_router(billing_router, prefix="", tags=["Billing"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(token_admin.router, prefix="/admin/tokens", tags=["Token Admin"])
api_router.include_router(api_tokens.router, prefix="/api-tokens", tags=["API Tokens"])
api_router.include_router(gus.router, prefix="", tags=["GUS"])
api_router.include_router(two_factor.router, prefix="/auth", tags=["2FA"])
api_router.include_router(sessions.router, prefix="/auth", tags=["Sessions"])
api_router.include_router(dunning.router, prefix="/admin", tags=["Dunning"])
api_router.include_router(admin_webcreator.router, prefix="/admin", tags=["Admin WebCreator"])
api_router.include_router(payments.router, prefix="/billing", tags=["Payments"])
api_router.include_router(webhook_config.router, prefix="", tags=["Webhooks"])
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(subscription_status.router, prefix="", tags=["Subscription Status"])
api_router.include_router(rbac_router, prefix="", tags=["RBAC"])

# WebCreator endpoints
api_router.include_router(creator_projects.router, prefix="/projects", tags=["Creator: Projects"])
api_router.include_router(creator_briefs.router, prefix="/projects", tags=["Creator: Briefs"])
api_router.include_router(creator_materials.router, prefix="/projects", tags=["Creator: Materials"])
api_router.include_router(creator_styles.router, prefix="/projects", tags=["Creator: Styles"])
api_router.include_router(creator_sections.router, prefix="/projects", tags=["Creator: Sections"])
api_router.include_router(creator_blocks.router, prefix="", tags=["Creator: Blocks"])
api_router.include_router(creator_ai.router, prefix="/projects", tags=["Creator: AI"])
api_router.include_router(creator_ai.usage_router, prefix="/admin", tags=["Creator: AI"])
api_router.include_router(creator_config.router, prefix="/projects", tags=["Creator: Config"])
api_router.include_router(creator_publishing.router, prefix="/projects", tags=["Creator: Publishing"])
api_router.include_router(creator_forms.public_router, prefix="", tags=["Creator: Forms"])
api_router.include_router(creator_forms.router, prefix="/projects", tags=["Creator: Forms"])
api_router.include_router(creator_stock_photos.router, prefix="", tags=["Creator: Stock Photos"])
api_router.include_router(creator_stats.router, prefix="/projects", tags=["Creator: Stats"])
api_router.include_router(creator_integrations.public_router, prefix="", tags=["Creator: Integrations"])
api_router.include_router(creator_integrations.router, prefix="/projects", tags=["Creator: Integrations"])
api_router.include_router(creator_tracking.public_router, prefix="", tags=["Creator: Tracking"])
api_router.include_router(creator_tracking.router, prefix="/projects", tags=["Creator: Tracking"])
api_router.include_router(creator_google.callback_router, prefix="", tags=["Creator: Google Integrations"])
api_router.include_router(creator_google.router, prefix="/projects", tags=["Creator: Google Integrations"])
api_router.include_router(creator_site_type_config.router, prefix="", tags=["Creator: Site Type Config"])
