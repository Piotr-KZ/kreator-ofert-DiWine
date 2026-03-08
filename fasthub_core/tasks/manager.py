"""
Task Manager — singleton zarządzający task queue.

Factory pattern: tworzy backend z konfiguracji.
Singleton: jeden backend na cały proces.

Config:
    TASK_BACKEND=arq       -> ARQBackend (produkcja)
    TASK_BACKEND=celery    -> CeleryBackend (przyszłość)
    TASK_BACKEND=sync      -> SyncBackend (dev, testy)

Użycie:
    from fasthub_core.tasks.manager import get_task_manager

    manager = get_task_manager()
    await manager.enqueue("my_app.tasks.do_work", data_id=123)

    # Albo przez helpery:
    from fasthub_core.tasks import enqueue_task, enqueue_email
    await enqueue_email(to="user@test.com", subject="Hej", body="<p>Cześć</p>")
"""

import logging
from typing import Optional

from fasthub_core.tasks.base import TaskQueueBackend

logger = logging.getLogger(__name__)

# Singleton
_manager: Optional[TaskQueueBackend] = None


def create_backend(backend_type: str = None) -> TaskQueueBackend:
    """
    Factory — stwórz backend z nazwy.

    Args:
        backend_type: "arq", "celery", "sync". None = z config.

    Returns:
        TaskQueueBackend implementacja
    """
    if backend_type is None:
        try:
            from fasthub_core.config import get_settings
            backend_type = getattr(get_settings(), "TASK_BACKEND", "arq")
        except Exception:
            backend_type = "sync"

    backend_type = backend_type.lower().strip()

    if backend_type == "arq":
        try:
            from fasthub_core.tasks.backends.arq_backend import ARQBackend
            logger.info("Task queue backend: ARQ")
            return ARQBackend()
        except ImportError:
            logger.warning("ARQ not installed, falling back to sync")
            backend_type = "sync"

    if backend_type == "celery":
        # Przyszła implementacja
        try:
            from fasthub_core.tasks.backends.celery_backend import CeleryBackend
            logger.info("Task queue backend: Celery")
            return CeleryBackend()
        except ImportError:
            logger.warning("Celery backend not available, falling back to sync")
            backend_type = "sync"

    # Fallback — zawsze działa
    from fasthub_core.tasks.backends.sync_backend import SyncBackend
    logger.info("Task queue backend: Sync (immediate execution)")
    return SyncBackend()


def get_task_manager() -> TaskQueueBackend:
    """
    Zwróć singleton backend.

    Pierwszy call tworzy backend z config.
    Kolejne zwracają ten sam obiekt.
    """
    global _manager
    if _manager is None:
        _manager = create_backend()
    return _manager


def set_task_manager(backend: TaskQueueBackend) -> None:
    """
    Ustaw custom backend (np. w testach).

    Użycie w testach:
        from fasthub_core.tasks.manager import set_task_manager
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        set_task_manager(SyncBackend())
    """
    global _manager
    _manager = backend


async def close_task_manager() -> None:
    """Zamknij backend (shutdown hook)."""
    global _manager
    if _manager:
        await _manager.close()
        _manager = None
