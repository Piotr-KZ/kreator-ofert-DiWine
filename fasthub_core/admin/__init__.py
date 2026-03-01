"""
Admin package
Super Admin dashboard — routes, service, schemas
"""

from fasthub_core.admin.routes import router as admin_router
from fasthub_core.admin.service import AdminService

__all__ = ["admin_router", "AdminService"]
