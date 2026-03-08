"""
ARQ Backend — implementacja TaskQueueBackend na bazie ARQ.

ARQ = lekki, async-native task queue oparty na Redis.
Idealny dla FastAPI. Cron wbudowany, zero dodatkowych serwisów.

Wymagania:
- Redis (już w docker-compose)
- pip install arq
"""

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from fasthub_core.tasks.base import TaskQueueBackend

logger = logging.getLogger(__name__)


class ARQBackend(TaskQueueBackend):
    """
    ARQ implementation of TaskQueueBackend.

    Lazy connection — pool tworzony przy pierwszym enqueue().
    """

    def __init__(self, redis_settings=None):
        self._redis_settings = redis_settings
        self._pool = None

    async def _get_pool(self):
        if self._pool is None:
            from arq import create_pool
            if self._redis_settings is None:
                from fasthub_core.tasks.worker import get_redis_settings
                self._redis_settings = get_redis_settings()
            self._pool = await create_pool(self._redis_settings)
        return self._pool

    async def enqueue(self, task_name: str, **kwargs: Any) -> Optional[str]:
        pool = await self._get_pool()
        job = await pool.enqueue_job(task_name, **kwargs)
        logger.info(f"[ARQ] enqueued: {task_name} → job={job.job_id}")
        return job.job_id

    async def enqueue_at(
        self, task_name: str, defer_by: timedelta, **kwargs: Any
    ) -> Optional[str]:
        pool = await self._get_pool()
        job = await pool.enqueue_job(task_name, _defer_by=defer_by, **kwargs)
        logger.info(f"[ARQ] enqueued (defer {defer_by}): {task_name} → job={job.job_id}")
        return job.job_id

    async def get_queue_stats(self) -> Dict[str, int]:
        pool = await self._get_pool()
        try:
            queued = await pool.redis.zcard(b"arq:queue") or 0
            results = await pool.redis.keys("arq:result:*")
            return {
                "queued": queued,
                "active": 0,  # ARQ nie eksponuje tego natywnie
                "complete": len(results),
                "failed": 0,
                "backend": "arq",
            }
        except Exception as e:
            logger.warning(f"ARQ stats error: {e}")
            return {"queued": 0, "active": 0, "complete": 0, "failed": 0, "backend": "arq"}

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("[ARQ] pool closed")

    @property
    def backend_name(self) -> str:
        return "arq"
