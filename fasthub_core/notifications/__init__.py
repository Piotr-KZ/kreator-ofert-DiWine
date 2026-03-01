"""
Notifications package
In-app notifications, email transport, user preferences
"""

from fasthub_core.notifications.routes import router as notifications_router
from fasthub_core.notifications.service import NotificationService
from fasthub_core.notifications.email_transport import EmailTransport, create_email_transport

__all__ = [
    "notifications_router",
    "NotificationService",
    "EmailTransport",
    "create_email_transport",
]
