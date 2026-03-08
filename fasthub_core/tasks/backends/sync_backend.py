"""
Sync Backend — wykonanie natychmiastowe bez kolejki.

Używane w:
- Development bez Redisa
- Testach jednostkowych
- Sytuacjach awaryjnych (Redis padł)

Task wykonywany natychmiast w bieżącym procesie.
Brak retry, brak opóźnień, brak kolejki — ale działa zawsze.
"""

import logging
import importlib
from datetime import timedelta
from typing import Any, Dict, Optional

from fasthub_core.tasks.base import TaskQueueBackend

logger = logging.getLogger(__name__)


class SyncBackend(TaskQueueBackend):
    """
    Synchronous fallback — uruchamia task natychmiast.
    """

    def __init__(self):
        self._executed_count = 0
        self._failed_count = 0

    async def enqueue(self, task_name: str, **kwargs: Any) -> Optional[str]:
        logger.info(f"[SYNC] executing immediately: {task_name}")
        try:
            module_path, func_name = task_name.rsplit(".", 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            await func({}, **kwargs)  # ctx={} placeholder
            self._executed_count += 1
            return None  # Brak job_id — synchroniczne
        except Exception as e:
            self._failed_count += 1
            logger.error(f"[SYNC] task failed: {task_name}: {e}")
            return None

    async def enqueue_at(
        self, task_name: str, defer_by: timedelta, **kwargs: Any
    ) -> Optional[str]:
        logger.warning(f"[SYNC] defer_by ignored (no queue): {task_name}")
        return await self.enqueue(task_name, **kwargs)

    async def get_queue_stats(self) -> Dict[str, int]:
        return {
            "queued": 0,
            "active": 0,
            "complete": self._executed_count,
            "failed": self._failed_count,
            "backend": "sync",
        }

    async def close(self) -> None:
        pass  # Nic do zamknięcia

    @property
    def backend_name(self) -> str:
        return "sync"
