"""
Testy Background Tasks — pluggable task queue (Brief 15).
"""

import os
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, patch, MagicMock


# ============================================================================
# TASK QUEUE CONTRACT (ABC)
# ============================================================================

class TestTaskQueueContract:

    def test_contract_is_abstract(self):
        from fasthub_core.tasks.base import TaskQueueBackend
        with pytest.raises(TypeError):
            TaskQueueBackend()

    def test_contract_has_enqueue(self):
        from fasthub_core.tasks.base import TaskQueueBackend
        assert hasattr(TaskQueueBackend, "enqueue")

    def test_contract_has_enqueue_at(self):
        from fasthub_core.tasks.base import TaskQueueBackend
        assert hasattr(TaskQueueBackend, "enqueue_at")

    def test_contract_has_get_queue_stats(self):
        from fasthub_core.tasks.base import TaskQueueBackend
        assert hasattr(TaskQueueBackend, "get_queue_stats")

    def test_contract_has_close(self):
        from fasthub_core.tasks.base import TaskQueueBackend
        assert hasattr(TaskQueueBackend, "close")

    def test_contract_has_backend_name(self):
        from fasthub_core.tasks.base import TaskQueueBackend
        assert hasattr(TaskQueueBackend, "backend_name")


# ============================================================================
# CONTRACTS.PY — TaskQueueContract
# ============================================================================

class TestTaskQueueContractInContracts:

    def test_contract_exists(self):
        from fasthub_core.contracts import TaskQueueContract
        assert TaskQueueContract is not None

    def test_contract_has_methods(self):
        from fasthub_core.contracts import TaskQueueContract
        assert hasattr(TaskQueueContract, "enqueue")
        assert hasattr(TaskQueueContract, "enqueue_at")
        assert hasattr(TaskQueueContract, "get_queue_stats")
        assert hasattr(TaskQueueContract, "close")


# ============================================================================
# SYNC BACKEND
# ============================================================================

class TestSyncBackend:

    def test_create_sync_backend(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        backend = SyncBackend()
        assert backend.backend_name == "sync"

    @pytest.mark.asyncio
    async def test_enqueue_executes_immediately(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        backend = SyncBackend()

        # Enqueue a real task — email_tasks.send_email_task will fail
        # but sync backend catches exceptions
        result = await backend.enqueue(
            "fasthub_core.tasks.email_tasks.send_email_task",
            to="test@test.com", subject="Test", body="Hi",
        )
        assert result is None  # Sync returns None (no job_id)

    @pytest.mark.asyncio
    async def test_enqueue_at_ignores_delay(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        backend = SyncBackend()

        result = await backend.enqueue_at(
            "fasthub_core.tasks.email_tasks.send_email_task",
            defer_by=timedelta(minutes=5),
            to="test@test.com", subject="Test", body="Body",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_queue_stats(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        backend = SyncBackend()
        stats = await backend.get_queue_stats()
        assert "queued" in stats
        assert "active" in stats
        assert "complete" in stats
        assert "failed" in stats
        assert stats["backend"] == "sync"

    @pytest.mark.asyncio
    async def test_close_does_nothing(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        backend = SyncBackend()
        await backend.close()  # Nie rzuca wyjątku

    @pytest.mark.asyncio
    async def test_stats_count_executions(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        backend = SyncBackend()

        # Execute a task that will fail (nonexistent module)
        await backend.enqueue("nonexistent.module.task")
        stats = await backend.get_queue_stats()
        assert stats["failed"] >= 1

    def test_sync_implements_contract(self):
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        from fasthub_core.tasks.base import TaskQueueBackend
        assert issubclass(SyncBackend, TaskQueueBackend)


# ============================================================================
# ARQ BACKEND
# ============================================================================

class TestARQBackend:

    def test_arq_implements_contract(self):
        from fasthub_core.tasks.backends.arq_backend import ARQBackend
        from fasthub_core.tasks.base import TaskQueueBackend
        assert issubclass(ARQBackend, TaskQueueBackend)

    def test_arq_backend_name(self):
        from fasthub_core.tasks.backends.arq_backend import ARQBackend
        backend = ARQBackend()
        assert backend.backend_name == "arq"

    def test_arq_lazy_pool(self):
        from fasthub_core.tasks.backends.arq_backend import ARQBackend
        backend = ARQBackend()
        assert backend._pool is None  # Lazy — nie łączy się od razu

    def test_arq_custom_redis_settings(self):
        from fasthub_core.tasks.backends.arq_backend import ARQBackend
        settings = MagicMock()
        backend = ARQBackend(redis_settings=settings)
        assert backend._redis_settings == settings


# ============================================================================
# TASK MANAGER (Singleton + Factory)
# ============================================================================

class TestTaskManager:

    def setup_method(self):
        """Reset singleton before each test."""
        import fasthub_core.tasks.manager as mgr
        mgr._manager = None

    def test_create_backend_sync(self):
        from fasthub_core.tasks.manager import create_backend
        backend = create_backend("sync")
        assert backend.backend_name == "sync"

    def test_create_backend_arq(self):
        from fasthub_core.tasks.manager import create_backend
        backend = create_backend("arq")
        assert backend.backend_name == "arq"

    def test_create_backend_unknown_falls_to_sync(self):
        from fasthub_core.tasks.manager import create_backend
        backend = create_backend("unknown_backend")
        assert backend.backend_name == "sync"

    def test_set_task_manager(self):
        from fasthub_core.tasks.manager import set_task_manager, get_task_manager
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        custom = SyncBackend()
        set_task_manager(custom)
        assert get_task_manager() is custom

    def test_get_task_manager_creates_singleton(self):
        from fasthub_core.tasks.manager import get_task_manager
        import fasthub_core.tasks.manager as mgr
        mgr._manager = None

        with patch.dict(os.environ, {"TASK_BACKEND": "sync", "SECRET_KEY": "test"}):
            import fasthub_core.config as cfg
            cfg._settings = None
            manager = get_task_manager()
            assert manager is not None
            assert manager.backend_name == "sync"
            cfg._settings = None

    @pytest.mark.asyncio
    async def test_close_task_manager(self):
        from fasthub_core.tasks.manager import set_task_manager, close_task_manager
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        set_task_manager(SyncBackend())
        await close_task_manager()
        import fasthub_core.tasks.manager as mgr
        assert mgr._manager is None


# ============================================================================
# ENQUEUE HELPERS
# ============================================================================

class TestEnqueueHelpers:

    def setup_method(self):
        import fasthub_core.tasks.manager as mgr
        from fasthub_core.tasks.backends.sync_backend import SyncBackend
        mgr._manager = SyncBackend()

    @pytest.mark.asyncio
    async def test_enqueue_task(self):
        from fasthub_core.tasks.enqueue import enqueue_task
        # Will try to execute sync — nonexistent task, falls back gracefully
        result = await enqueue_task("nonexistent.module.some_task", arg1="val")
        assert result is None  # Sync returns None

    @pytest.mark.asyncio
    async def test_enqueue_email(self):
        from fasthub_core.tasks.enqueue import enqueue_email
        result = await enqueue_email(
            to="user@example.com",
            subject="Test Subject",
            body="<h1>Hello</h1>",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_enqueue_task_with_defer(self):
        from fasthub_core.tasks.enqueue import enqueue_task
        result = await enqueue_task(
            "nonexistent.module.task",
            defer_by=60,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_enqueue_fallback_on_error(self):
        """Jeśli manager rzuci wyjątek, fallback na SyncBackend."""
        from fasthub_core.tasks.enqueue import enqueue_task
        import fasthub_core.tasks.manager as mgr

        # Ustaw mock, który rzuca wyjątek
        broken_manager = AsyncMock()
        broken_manager.enqueue = AsyncMock(side_effect=RuntimeError("Redis down"))
        mgr._manager = broken_manager

        # Nie rzuca — fallback na sync
        result = await enqueue_task("some.task.name")
        assert result is None  # Sync fallback zwraca None


# ============================================================================
# WORKER CONFIG
# ============================================================================

class TestWorkerConfig:

    def test_base_worker_settings_exists(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        assert BaseWorkerSettings is not None

    def test_worker_has_functions(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        assert isinstance(BaseWorkerSettings.functions, list)
        assert len(BaseWorkerSettings.functions) >= 5  # email + 4 maintenance

    def test_worker_has_cron_jobs(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        assert isinstance(BaseWorkerSettings.cron_jobs, list)
        assert len(BaseWorkerSettings.cron_jobs) >= 4

    def test_worker_has_email_task(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        task_names = BaseWorkerSettings.functions
        assert any("send_email_task" in t for t in task_names)

    def test_worker_has_maintenance_tasks(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        task_names = BaseWorkerSettings.functions
        assert any("cleanup_expired_tokens" in t for t in task_names)
        assert any("reset_monthly_usage" in t for t in task_names)
        assert any("cleanup_old_audit_entries" in t for t in task_names)
        assert any("cleanup_old_notifications" in t for t in task_names)

    def test_get_redis_settings(self):
        from fasthub_core.tasks.worker import get_redis_settings
        from arq.connections import RedisSettings
        settings = get_redis_settings()
        assert isinstance(settings, RedisSettings)

    def test_redis_settings_default_localhost(self):
        from fasthub_core.tasks.worker import get_redis_settings
        with patch.dict(os.environ, {}, clear=False):
            settings = get_redis_settings()
            assert settings.host == "localhost"
            assert settings.port == 6379

    def test_worker_max_tries(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        assert BaseWorkerSettings.max_tries == 3

    def test_worker_retry_delay(self):
        from fasthub_core.tasks.worker import BaseWorkerSettings
        assert BaseWorkerSettings.retry_delay == timedelta(seconds=30)


# ============================================================================
# EMAIL TASK
# ============================================================================

class TestEmailTask:

    def test_email_task_exists(self):
        from fasthub_core.tasks.email_tasks import send_email_task
        assert callable(send_email_task)

    @pytest.mark.asyncio
    async def test_email_task_calls_transport(self):
        from fasthub_core.tasks.email_tasks import send_email_task

        mock_transport = AsyncMock()
        mock_transport.send = AsyncMock(return_value=True)

        with patch(
            "fasthub_core.notifications.email_transport.create_email_transport",
            return_value=mock_transport,
        ):
            result = await send_email_task(
                ctx={},
                to="test@example.com",
                subject="Hello",
                body="<h1>Hi</h1>",
            )
            assert result["sent"] is True
            assert result["to"] == "test@example.com"
            mock_transport.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_email_task_raises_on_failure(self):
        from fasthub_core.tasks.email_tasks import send_email_task

        with patch(
            "fasthub_core.notifications.email_transport.create_email_transport",
            side_effect=RuntimeError("SMTP down"),
        ):
            with pytest.raises(RuntimeError, match="SMTP down"):
                await send_email_task(
                    ctx={}, to="x@x.com", subject="Fail", body="body",
                )


# ============================================================================
# MAINTENANCE TASKS
# ============================================================================

class TestMaintenanceTasks:

    def test_cleanup_expired_tokens_exists(self):
        from fasthub_core.tasks.maintenance_tasks import cleanup_expired_tokens
        assert callable(cleanup_expired_tokens)

    def test_reset_monthly_usage_exists(self):
        from fasthub_core.tasks.maintenance_tasks import reset_monthly_usage
        assert callable(reset_monthly_usage)

    def test_cleanup_old_audit_entries_exists(self):
        from fasthub_core.tasks.maintenance_tasks import cleanup_old_audit_entries
        assert callable(cleanup_old_audit_entries)

    def test_cleanup_old_notifications_exists(self):
        from fasthub_core.tasks.maintenance_tasks import cleanup_old_notifications
        assert callable(cleanup_old_notifications)

    @pytest.mark.asyncio
    async def test_maintenance_tasks_graceful_without_db(self):
        """Wszystkie maintenance taski działają bez bazy (ImportError -> skip)."""
        from fasthub_core.tasks.maintenance_tasks import (
            cleanup_expired_tokens,
            reset_monthly_usage,
            cleanup_old_audit_entries,
            cleanup_old_notifications,
        )

        # Bez bazy — ImportError -> graceful skip
        r1 = await cleanup_expired_tokens({})
        assert r1["deleted"] == 0

        r2 = await reset_monthly_usage({})
        assert r2["reset_count"] == 0

        r3 = await cleanup_old_audit_entries({})
        assert r3["deleted"] == 0
        assert r3["cutoff_days"] == 180

        r4 = await cleanup_old_notifications({})
        assert r4["deleted"] == 0
        assert r4["cutoff_days"] == 90


# ============================================================================
# CONFIG
# ============================================================================

class TestTaskConfig:

    @pytest.fixture(autouse=True)
    def _ensure_secret_key(self):
        import fasthub_core.config as cfg
        cfg._settings = None
        os.environ.setdefault("SECRET_KEY", "test-secret-key-for-task-tests")
        yield
        cfg._settings = None

    def test_config_has_task_backend(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert hasattr(settings, "TASK_BACKEND")
        assert settings.TASK_BACKEND == "arq"

    def test_config_has_arq_settings(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert hasattr(settings, "ARQ_REDIS_URL")
        assert hasattr(settings, "ARQ_MAX_JOBS")
        assert hasattr(settings, "ARQ_JOB_TIMEOUT")
        assert hasattr(settings, "ARQ_MAX_TRIES")

    def test_config_arq_defaults(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert settings.ARQ_MAX_JOBS == 10
        assert settings.ARQ_JOB_TIMEOUT == 120
        assert settings.ARQ_MAX_TRIES == 3

    def test_config_task_backend_default_arq(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert settings.TASK_BACKEND == "arq"


# ============================================================================
# EXPORTS
# ============================================================================

class TestExports:

    def test_tasks_init_exports(self):
        from fasthub_core.tasks import (
            TaskQueueBackend,
            get_task_manager, set_task_manager, close_task_manager, create_backend,
            enqueue_task, enqueue_email,
            BaseWorkerSettings, get_redis_settings,
            send_email_task,
            cleanup_expired_tokens, reset_monthly_usage,
            cleanup_old_audit_entries, cleanup_old_notifications,
        )
        assert TaskQueueBackend is not None
        assert callable(enqueue_task)
        assert callable(enqueue_email)
        assert callable(get_task_manager)
        assert callable(set_task_manager)
        assert callable(close_task_manager)
        assert callable(create_backend)
        assert BaseWorkerSettings is not None

    def test_backends_init_exports(self):
        from fasthub_core.tasks.backends import ARQBackend, SyncBackend
        assert ARQBackend is not None
        assert SyncBackend is not None

    def test_core_init_exports_tasks(self):
        from fasthub_core import (
            enqueue_task, enqueue_email,
            get_task_manager, set_task_manager, close_task_manager,
            TaskQueueBackend, BaseWorkerSettings,
            TaskQueueContract,
        )
        assert callable(enqueue_task)
        assert callable(enqueue_email)
        assert TaskQueueBackend is not None
        assert TaskQueueContract is not None
