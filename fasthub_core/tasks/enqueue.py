"""
Enqueue Helpers — publiczne API task queue.

TO IMPORTUJE APLIKACJA:
    from fasthub_core.tasks import enqueue_task, enqueue_email

    await enqueue_task("my_app.tasks.process_data", data_id=123)
    await enqueue_email(to="jan@firma.pl", subject="Witaj", body="<h1>Cześć</h1>")

Pod spodem:
    enqueue_task() -> TaskManager -> wybrany backend (ARQ/Celery/Sync) -> Redis/natychmiast

Aplikacja NIE WIE jaki backend jest pod spodem. Config decyduje.
"""

import logging
from datetime import timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def enqueue_task(
    task_name: str,
    defer_by: Optional[int] = None,
    **kwargs: Any,
) -> Optional[str]:
    """
    Wrzuć task do kolejki.

    Args:
        task_name: pełna ścieżka ("fasthub_core.tasks.email_tasks.send_email_task")
        defer_by: opóźnienie w sekundach (opcjonalnie)
        **kwargs: parametry taska

    Returns:
        job_id (str) lub None (sync mode)
    """
    from fasthub_core.tasks.manager import get_task_manager
    manager = get_task_manager()

    try:
        if defer_by:
            return await manager.enqueue_at(
                task_name, timedelta(seconds=defer_by), **kwargs
            )
        return await manager.enqueue(task_name, **kwargs)
    except Exception as e:
        logger.error(f"Enqueue failed for {task_name}: {e}")
        # Awaryjny fallback na sync
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        fallback = SyncBackend()
        return await fallback.enqueue(task_name, **kwargs)


async def enqueue_email(
    to: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    is_html: bool = True,
    defer_by: Optional[int] = None,
) -> Optional[str]:
    """
    Shortcut: wyślij email w tle.

    Przykład:
        await enqueue_email(
            to="jan@firma.pl",
            subject="Twój proces zakończony",
            body="<h1>Sukces!</h1><p>Przetworzono 15 faktur.</p>",
        )
    """
    return await enqueue_task(
        "fasthub_core.tasks.email_tasks.send_email_task",
        defer_by=defer_by,
        to=to,
        subject=subject,
        body=body,
        from_email=from_email,
        is_html=is_html,
    )
