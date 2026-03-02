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
    EventBusContract,
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

# Infrastructure (Brief 10)
from fasthub_core.infrastructure.redis import get_redis, set_cache, get_cache

# Events (Brief 10)
from fasthub_core.events.bus import event_bus, Event, EventBus

# Security (Brief 10)
from fasthub_core.security.encryption import encrypt_credentials, decrypt_credentials

# Production infrastructure (Brief 13)
from fasthub_core.logging import configure_logging, get_logger
from fasthub_core.monitoring import init_monitoring, capture_exception
from fasthub_core.rate_limiting import create_limiter, RateLimits
from fasthub_core.health import health_router, HealthChecker, get_health_checker
from fasthub_core.billing.subscription_check import SubscriptionChecker, require_active_subscription

# File Storage + Feature Flags (Brief 14)
from fasthub_core.storage import StorageService, FileUpload, get_storage_service
from fasthub_core.billing.feature_flags import check_feature, require_feature, get_plan_features

# Social Login (Brief 18)
from fasthub_core.auth.social_login import SocialLoginService, get_social_login_service
from fasthub_core.auth.social_routes import router as social_login_router
from fasthub_core.auth.social_providers import SUPPORTED_PROVIDERS

__all__ = [
    "__version__",
    "AuthContract", "UserContract", "PermissionContract",
    "BillingContract", "AuditContract", "NotificationContract",
    "EventBusContract", "DatabaseContract",
    "Settings", "get_settings", "get_db", "get_engine",
    "admin_router",
    "rbac_router", "RBACService", "require_permission",
    "audit_router", "AuditService", "get_request_context",
    "notifications_router", "NotificationService",
    "ConnectionManager", "get_connection_manager", "ws_router", "realtime_status_router",
    "SecurityHeadersMiddleware", "RequestIDMiddleware",
    # Brief 10 modules
    "get_redis", "set_cache", "get_cache",
    "event_bus", "Event", "EventBus",
    "encrypt_credentials", "decrypt_credentials",
    # Brief 13 modules
    "configure_logging", "get_logger",
    "init_monitoring", "capture_exception",
    "create_limiter", "RateLimits",
    "health_router", "HealthChecker", "get_health_checker",
    "SubscriptionChecker", "require_active_subscription",
    # Brief 14 modules
    "StorageService", "FileUpload", "get_storage_service",
    "check_feature", "require_feature", "get_plan_features",
    # Brief 18 — Social Login
    "SocialLoginService", "get_social_login_service",
    "social_login_router", "SUPPORTED_PROVIDERS",
]
