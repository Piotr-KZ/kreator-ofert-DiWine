"""
Background Tasks — przełączalny task queue.

Publiczne API:
    from fasthub_core.tasks import enqueue_task, enqueue_email

    await enqueue_email(to="jan@firma.pl", subject="Witaj", body="...")
    await enqueue_task("my_app.tasks.process", data_id=123)

Config:
    TASK_BACKEND=arq       <- produkcja
    TASK_BACKEND=celery    <- przyszłość
    TASK_BACKEND=sync      <- development
"""

from fasthub_core.tasks.base import TaskQueueBackend
from fasthub_core.tasks.manager import (
    get_task_manager, set_task_manager, close_task_manager, create_backend,
)
from fasthub_core.tasks.enqueue import enqueue_task, enqueue_email
from fasthub_core.tasks.worker import BaseWorkerSettings, get_redis_settings
from fasthub_core.tasks.email_tasks import send_email_task
from fasthub_core.tasks.maintenance_tasks import (
    cleanup_expired_tokens, reset_monthly_usage,
    cleanup_old_audit_entries, cleanup_old_notifications,
)

__all__ = [
    # Contract
    "TaskQueueBackend",
    # Manager
    "get_task_manager", "set_task_manager", "close_task_manager", "create_backend",
    # Public API
    "enqueue_task", "enqueue_email",
    # Worker
    "BaseWorkerSettings", "get_redis_settings",
    # Tasks
    "send_email_task",
    "cleanup_expired_tokens", "reset_monthly_usage",
    "cleanup_old_audit_entries", "cleanup_old_notifications",
]
