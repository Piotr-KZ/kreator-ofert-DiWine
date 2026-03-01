"""
FastHub Core — uniwersalny fundament SaaS.
Instalacja: pip install fasthub-core
Użycie: from fasthub_core.auth import create_access_token
"""

__version__ = "2.0.0-alpha"

# Kontrakty (interfejsy)
from fasthub_core.contracts import (
    AuthContract,
    UserContract,
    PermissionContract,
    BillingContract,
    AuditContract,
    NotificationContract,
    DatabaseContract,
)

# Implementacje
from fasthub_core.config import Settings, get_settings

# Database
from fasthub_core.db.session import get_db, get_engine

# Admin
from fasthub_core.admin import admin_router

# RBAC
from fasthub_core.rbac import rbac_router, RBACService, require_permission

# Audit
from fasthub_core.audit import audit_router, AuditService, get_request_context

# Notifications
from fasthub_core.notifications import notifications_router, NotificationService

# Realtime
from fasthub_core.realtime import ConnectionManager, get_connection_manager, ws_router, realtime_status_router

# Middleware
from fasthub_core.middleware import SecurityHeadersMiddleware, RequestIDMiddleware

__all__ = [
    "__version__",
    "AuthContract", "UserContract", "PermissionContract",
    "BillingContract", "AuditContract", "NotificationContract",
    "DatabaseContract",
    "Settings", "get_settings", "get_db", "get_engine",
    "admin_router",
    "rbac_router", "RBACService", "require_permission",
    "audit_router", "AuditService", "get_request_context",
    "notifications_router", "NotificationService",
    "ConnectionManager", "get_connection_manager", "ws_router", "realtime_status_router",
    "SecurityHeadersMiddleware", "RequestIDMiddleware",
]
