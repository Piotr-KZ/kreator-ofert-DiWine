"""
API v1 router aggregator
Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
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
from app.api.v1.endpoints.creator import blocks as creator_blocks
from app.api.v1.endpoints.creator import briefs as creator_briefs
from app.api.v1.endpoints.creator import materials as creator_materials
from app.api.v1.endpoints.creator import projects as creator_projects
from app.api.v1.endpoints.creator import sections as creator_sections
from app.api.v1.endpoints.creator import styles as creator_styles
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
