"""
API v1 router aggregator
Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    api_tokens,
    auth,
    health,
    invoices,
    members,
    organizations,
    subscription_status,
    token_admin,
    users,
)
from fasthub_core.billing.api import router as billing_router

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
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(subscription_status.router, prefix="", tags=["Subscription Status"])
