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

__all__ = [
    "__version__",
    "AuthContract", "UserContract", "PermissionContract",
    "BillingContract", "AuditContract", "NotificationContract",
    "DatabaseContract",
    "Settings", "get_settings", "get_db", "get_engine",
]
