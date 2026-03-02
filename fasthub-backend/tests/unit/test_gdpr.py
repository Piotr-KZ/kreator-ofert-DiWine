"""
Tests for GDPR module — export, anonymize, deletion workflow.
~25 tests covering: registry, exporters, export service, anonymize, deletion.
"""

import json
import zipfile
import io
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fasthub_core.gdpr.export_registry import DataExporter, ExportRegistry
from fasthub_core.gdpr.export_service import ExportService
from fasthub_core.gdpr.anonymize_service import AnonymizeService
from fasthub_core.gdpr.deletion_service import DeletionService
from fasthub_core.gdpr.models import DeletionRequest


# ============================================================================
# ExportRegistry tests
# ============================================================================

class TestExportRegistry:

    def setup_method(self):
        ExportRegistry.clear()

    def test_register_exporter(self):
        class FakeExporter(DataExporter):
            async def export_user_data(self, user_id, db):
                return {}
            async def get_export_name(self):
                return "fake"

        ExportRegistry.register(FakeExporter())
        assert len(ExportRegistry.get_exporters()) == 1

    def test_register_duplicate_is_idempotent(self):
        class FakeExporter(DataExporter):
            async def export_user_data(self, user_id, db):
                return {}
            async def get_export_name(self):
                return "fake"

        ExportRegistry.register(FakeExporter())
        ExportRegistry.register(FakeExporter())
        assert len(ExportRegistry.get_exporters()) == 1

    def test_register_multiple_different_exporters(self):
        class ExporterA(DataExporter):
            async def export_user_data(self, user_id, db):
                return {}
            async def get_export_name(self):
                return "a"

        class ExporterB(DataExporter):
            async def export_user_data(self, user_id, db):
                return {}
            async def get_export_name(self):
                return "b"

        ExportRegistry.register(ExporterA())
        ExportRegistry.register(ExporterB())
        assert len(ExportRegistry.get_exporters()) == 2

    def test_clear_removes_all(self):
        class FakeExporter(DataExporter):
            async def export_user_data(self, user_id, db):
                return {}
            async def get_export_name(self):
                return "fake"

        ExportRegistry.register(FakeExporter())
        ExportRegistry.clear()
        assert len(ExportRegistry.get_exporters()) == 0

    def test_get_exporters_returns_copy(self):
        result = ExportRegistry.get_exporters()
        assert isinstance(result, list)


# ============================================================================
# ExportService tests (with mocked exporters)
# ============================================================================

class TestExportService:

    def setup_method(self):
        ExportRegistry.clear()

    @pytest.mark.asyncio
    async def test_export_user_data_collects_from_all(self):
        class FakeExporterA(DataExporter):
            async def export_user_data(self, user_id, db):
                return {"items": [1, 2]}
            async def get_export_name(self):
                return "module_a"

        class FakeExporterB(DataExporter):
            async def export_user_data(self, user_id, db):
                return {"records": ["x"]}
            async def get_export_name(self):
                return "module_b"

        ExportRegistry.register(FakeExporterA())
        ExportRegistry.register(FakeExporterB())

        svc = ExportService(db=None)
        data = await svc.export_user_data(uuid4())

        assert "module_a" in data
        assert "module_b" in data
        assert data["module_a"]["items"] == [1, 2]
        assert data["module_b"]["records"] == ["x"]

    @pytest.mark.asyncio
    async def test_export_empty_no_exporters(self):
        svc = ExportService(db=None)
        data = await svc.export_user_data(uuid4())
        assert data == {}

    @pytest.mark.asyncio
    async def test_generate_zip_valid(self):
        class FakeExporter(DataExporter):
            async def export_user_data(self, user_id, db):
                return {"name": "test"}
            async def get_export_name(self):
                return "test_data"

        ExportRegistry.register(FakeExporter())

        svc = ExportService(db=None)
        zip_bytes = await svc.generate_zip(uuid4(), user_email="jan@test.pl")

        # Verify it's a valid ZIP
        buf = io.BytesIO(zip_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
            assert any("test_data.json" in n for n in names)
            assert any("metadata.json" in n for n in names)

            # Verify metadata content
            meta_name = [n for n in names if "metadata.json" in n][0]
            meta = json.loads(zf.read(meta_name))
            assert meta["user_email"] == "jan@test.pl"
            assert "exported_at" in meta

    @pytest.mark.asyncio
    async def test_generate_zip_folder_name_from_email(self):
        svc = ExportService(db=None)
        zip_bytes = await svc.generate_zip(uuid4(), user_email="anna@firma.pl")

        buf = io.BytesIO(zip_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
            assert any("export_anna_" in n for n in names)


# ============================================================================
# Individual exporter tests (with mocked DB)
# ============================================================================

class TestUserExporter:

    @pytest.mark.asyncio
    async def test_export_nonexistent_user(self):
        from fasthub_core.gdpr.exporters.user_exporter import UserExporter

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        exporter = UserExporter()
        data = await exporter.export_user_data(uuid4(), mock_db)
        assert data == {}

    @pytest.mark.asyncio
    async def test_get_export_name(self):
        from fasthub_core.gdpr.exporters.user_exporter import UserExporter
        exporter = UserExporter()
        assert await exporter.get_export_name() == "user"


class TestBillingExporter:

    @pytest.mark.asyncio
    async def test_export_no_orgs(self):
        from fasthub_core.gdpr.exporters.billing_exporter import BillingExporter

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        exporter = BillingExporter()
        data = await exporter.export_user_data(uuid4(), mock_db)
        assert data == {"subscriptions": [], "invoices": []}

    @pytest.mark.asyncio
    async def test_get_export_name(self):
        from fasthub_core.gdpr.exporters.billing_exporter import BillingExporter
        exporter = BillingExporter()
        assert await exporter.get_export_name() == "billing"


class TestAuditExporter:

    @pytest.mark.asyncio
    async def test_export_no_entries(self):
        from fasthub_core.gdpr.exporters.audit_exporter import AuditExporter

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        exporter = AuditExporter()
        data = await exporter.export_user_data(uuid4(), mock_db)
        assert data == {"audit_entries": []}

    @pytest.mark.asyncio
    async def test_get_export_name(self):
        from fasthub_core.gdpr.exporters.audit_exporter import AuditExporter
        exporter = AuditExporter()
        assert await exporter.get_export_name() == "audit_log"


class TestNotificationExporter:

    @pytest.mark.asyncio
    async def test_export_no_notifications(self):
        from fasthub_core.gdpr.exporters.notification_exporter import NotificationExporter

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        exporter = NotificationExporter()
        data = await exporter.export_user_data(uuid4(), mock_db)
        assert data == {"notifications": []}

    @pytest.mark.asyncio
    async def test_get_export_name(self):
        from fasthub_core.gdpr.exporters.notification_exporter import NotificationExporter
        exporter = NotificationExporter()
        assert await exporter.get_export_name() == "notifications"


# ============================================================================
# AnonymizeService tests
# ============================================================================

class TestAnonymizeService:

    @pytest.mark.asyncio
    async def test_anonymize_user_not_found(self):
        mock_db = AsyncMock()

        # User query returns None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        svc = AnonymizeService(mock_db)
        result = await svc._anonymize_user_record(uuid4(), "anon@test.local", "Deleted")
        assert result["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_anonymize_user_record(self):
        mock_user = MagicMock()
        mock_user.id = uuid4()

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        svc = AnonymizeService(mock_db)
        result = await svc._anonymize_user_record(
            mock_user.id, "deleted_abc@anonymized.local", "Deleted User abc"
        )

        assert result["status"] == "anonymized"
        assert mock_user.email == "deleted_abc@anonymized.local"
        assert mock_user.full_name == "Deleted User abc"
        assert mock_user.hashed_password == "DELETED"
        assert mock_user.is_active is False
        assert mock_user.google_id is None
        assert mock_user.github_id is None
        assert mock_user.microsoft_id is None

    @pytest.mark.asyncio
    async def test_anonymize_audit_logs(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_db.execute.return_value = mock_result

        svc = AnonymizeService(mock_db)
        result = await svc._anonymize_audit_logs(uuid4(), "anon@test.local")
        assert result["rows_updated"] == 5

    @pytest.mark.asyncio
    async def test_anonymize_notifications(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_db.execute.return_value = mock_result

        svc = AnonymizeService(mock_db)
        result = await svc._anonymize_notifications(uuid4())
        assert result["rows_updated"] == 3

    def test_hash_token_deterministic(self):
        token1 = AnonymizeService._hash_token("abc")
        token2 = AnonymizeService._hash_token("abc")
        assert token1 == token2
        assert len(token1) == 6

    def test_hash_token_different_inputs(self):
        token1 = AnonymizeService._hash_token("user1")
        token2 = AnonymizeService._hash_token("user2")
        assert token1 != token2


# ============================================================================
# DeletionService tests
# ============================================================================

class TestDeletionService:

    @pytest.mark.asyncio
    async def test_create_request(self):
        mock_db = AsyncMock()

        # No existing pending request
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("fasthub_core.gdpr.deletion_service.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                GDPR_DELETION_GRACE_DAYS=14,
            )

            svc = DeletionService(mock_db)
            request = await svc.create_request(uuid4(), reason="Test")

            assert request.status == "pending"
            assert request.reason == "Test"
            assert request.execute_after > datetime.utcnow()
            mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_request_returns_existing(self):
        existing = DeletionRequest(
            user_id=uuid4(),
            status="pending",
            execute_after=datetime.utcnow() + timedelta(days=14),
        )

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = mock_result

        svc = DeletionService(mock_db)
        result = await svc.create_request(existing.user_id)

        assert result is existing
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_request(self):
        pending = DeletionRequest(
            user_id=uuid4(),
            status="pending",
            execute_after=datetime.utcnow() + timedelta(days=14),
        )

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = pending
        mock_db.execute.return_value = mock_result

        svc = DeletionService(mock_db)
        result = await svc.cancel_request(pending.user_id)

        assert result.status == "canceled"
        assert result.canceled_at is not None

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_returns_none(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        svc = DeletionService(mock_db)
        result = await svc.cancel_request(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_before_grace_raises(self):
        request = DeletionRequest(
            id=uuid4(),
            user_id=uuid4(),
            status="pending",
            execute_after=datetime.utcnow() + timedelta(days=10),
        )

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = request
        mock_db.execute.return_value = mock_result

        svc = DeletionService(mock_db)
        with pytest.raises(ValueError, match="Grace period not expired"):
            await svc.execute_request(request.id)


# ============================================================================
# DeletionRequest model tests
# ============================================================================

class TestDeletionRequestModel:

    def test_model_creation(self):
        uid = uuid4()
        req = DeletionRequest(
            user_id=uid,
            status="pending",
            execute_after=datetime.utcnow() + timedelta(days=14),
            reason="I want to delete my account",
        )
        assert req.user_id == uid
        assert req.status == "pending"
        assert req.reason == "I want to delete my account"
        assert req.executed_at is None
        assert req.canceled_at is None
        assert req.export_file_path is None

    def test_model_tablename(self):
        assert DeletionRequest.__tablename__ == "deletion_requests"
