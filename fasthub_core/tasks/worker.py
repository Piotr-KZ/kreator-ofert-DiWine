"""
ARQ Worker — bazowa konfiguracja.

Aplikacja dziedziczy i dodaje swoje taski:

    # my_app/worker.py
    from fasthub_core.tasks.worker import BaseWorkerSettings
    from arq import cron

    class WorkerSettings(BaseWorkerSettings):
        functions = BaseWorkerSettings.functions + [
            "my_app.tasks.execute_process_task",
        ]
        cron_jobs = BaseWorkerSettings.cron_jobs + [
            cron("my_app.tasks.my_hourly_task", hour=None, minute=0),
        ]

Uruchomienie:
    arq my_app.worker.WorkerSettings
"""

import os
import logging
from datetime import timedelta

from arq import cron
from arq.connections import RedisSettings

logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    """Parse REDIS_URL -> ARQ RedisSettings."""
    url = os.getenv("ARQ_REDIS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")

    from urllib.parse import urlparse
    parsed = urlparse(url)

    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
        password=parsed.password,
    )


async def _startup(ctx):
    """Worker startup — DB init."""
    try:
        from fasthub_core.db.session import init_db
        await init_db()
        logger.info("Worker started — DB connected")
    except ImportError:
        logger.info("Worker started — no DB init available")
    except Exception as e:
        logger.error(f"Worker startup error: {e}")


async def _shutdown(ctx):
    """Worker shutdown — cleanup."""
    try:
        from fasthub_core.tasks.manager import close_task_manager
        await close_task_manager()
    except Exception:
        pass
    try:
        from fasthub_core.db.session import close_db
        await close_db()
    except Exception:
        pass
    logger.info("Worker shutdown complete")


class BaseWorkerSettings:
    """
    Bazowa konfiguracja ARQ workera.

    Zawiera:
    - Core tasks: email sending
    - Maintenance cron: token cleanup, usage reset, audit cleanup, notification cleanup

    Aplikacja rozszerza:
        class WorkerSettings(BaseWorkerSettings):
            functions = BaseWorkerSettings.functions + ["my.task"]
            cron_jobs = BaseWorkerSettings.cron_jobs + [cron("my.cron", ...)]
    """

    redis_settings = get_redis_settings()

    max_jobs = int(os.getenv("ARQ_MAX_JOBS", "10"))
    job_timeout = int(os.getenv("ARQ_JOB_TIMEOUT", "120"))
    max_tries = 3
    retry_delay = timedelta(seconds=30)

    on_startup = _startup
    on_shutdown = _shutdown

    # === CORE TASKS ===
    functions = [
        "fasthub_core.tasks.email_tasks.send_email_task",
        "fasthub_core.tasks.maintenance_tasks.cleanup_expired_tokens",
        "fasthub_core.tasks.maintenance_tasks.reset_monthly_usage",
        "fasthub_core.tasks.maintenance_tasks.cleanup_old_audit_entries",
        "fasthub_core.tasks.maintenance_tasks.cleanup_old_notifications",
    ]

    # === CRON JOBS ===
    cron_jobs = [
        # Co godzinę: wygasłe tokeny
        cron(
            "fasthub_core.tasks.maintenance_tasks.cleanup_expired_tokens",
            hour=None, minute=15, unique=True,
        ),
        # 1-szy miesiąca 0:05: reset monthly usage
        cron(
            "fasthub_core.tasks.maintenance_tasks.reset_monthly_usage",
            day=1, hour=0, minute=5, unique=True,
        ),
        # Niedziela 3:00: stare audit entries
        cron(
            "fasthub_core.tasks.maintenance_tasks.cleanup_old_audit_entries",
            weekday=6, hour=3, minute=0, unique=True,
        ),
        # Niedziela 4:00: stare powiadomienia
        cron(
            "fasthub_core.tasks.maintenance_tasks.cleanup_old_notifications",
            weekday=6, hour=4, minute=0, unique=True,
        ),
    ]
