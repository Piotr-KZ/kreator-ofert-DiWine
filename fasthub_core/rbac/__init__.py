"""
RBAC package — Role-Based Access Control
Elastyczny system ról i uprawnień.
"""

from fasthub_core.rbac.routes import router as rbac_router
from fasthub_core.rbac.service import RBACService
from fasthub_core.rbac.middleware import require_permission
from fasthub_core.rbac.defaults import CORE_PERMISSIONS, SYSTEM_ROLES

__all__ = [
    "rbac_router",
    "RBACService",
    "require_permission",
    "CORE_PERMISSIONS",
    "SYSTEM_ROLES",
]
