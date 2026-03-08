"""
Task Queue Contract — abstrakcyjny interfejs backendu kolejki.

Trzy implementacje:
- ARQBackend     — produkcja (async, Redis, lekki)
- CeleryBackend  — przyszłość (sync, Redis/RabbitMQ, monitoring Flower)
- SyncBackend    — development (bez Redisa, wykonanie natychmiastowe)

Aplikacja NIGDY nie importuje backendu bezpośrednio.
Używa: enqueue_task(), enqueue_email() — backend wybrany z config.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import timedelta


class TaskQueueBackend(ABC):
    """
    Kontrakt task queue — co każdy backend musi umieć.

    Metody:
    - enqueue: wrzuć task do kolejki
    - enqueue_at: wrzuć task z opóźnieniem
    - get_status: sprawdź status taska
    - close: zamknij połączenie
    """

    @abstractmethod
    async def enqueue(
        self,
        task_name: str,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Wrzuć task do kolejki.

        Args:
            task_name: pełna ścieżka taska ("fasthub_core.tasks.email_tasks.send_email_task")
            **kwargs: parametry taska

        Returns:
            job_id (str) lub None jeśli sync execution
        """
        ...

    @abstractmethod
    async def enqueue_at(
        self,
        task_name: str,
        defer_by: timedelta,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Wrzuć task z opóźnieniem.

        Args:
            task_name: ścieżka taska
            defer_by: opóźnienie (np. timedelta(minutes=5))
            **kwargs: parametry

        Returns:
            job_id lub None
        """
        ...

    @abstractmethod
    async def get_queue_stats(self) -> Dict[str, int]:
        """
        Statystyki kolejki.

        Returns:
            {"queued": 5, "active": 2, "complete": 100, "failed": 3}
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Zamknij połączenie z brokerem (Redis/RabbitMQ)."""
        ...

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Nazwa backendu: "arq", "celery", "sync"."""
        ...
