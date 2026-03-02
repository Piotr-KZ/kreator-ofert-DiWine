"""
Testy File Storage + Feature Flags.
"""

import pytest
import os
import tempfile
from pathlib import Path


# ============================================================================
# FILE UPLOAD MODEL
# ============================================================================

class TestFileUploadModel:

    def test_model_exists(self):
        from fasthub_core.storage.models import FileUpload
        assert FileUpload is not None

    def test_model_fields(self):
        from fasthub_core.storage.models import FileUpload
        required_fields = [
            "id", "organization_id", "uploaded_by",
            "original_filename", "stored_filename", "mime_type",
            "file_size_bytes", "file_size_mb",
            "storage_backend", "storage_path",
            "entity_type", "entity_id",
            "is_public", "is_deleted",
            "created_at",
        ]
        for field in required_fields:
            assert hasattr(FileUpload, field), f"Missing field: {field}"

    def test_model_tablename(self):
        from fasthub_core.storage.models import FileUpload
        assert FileUpload.__tablename__ == "file_uploads"


# ============================================================================
# LOCAL BACKEND
# ============================================================================

class TestLocalBackend:

    def test_create_local_backend(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)
            assert backend.base_dir == Path(tmpdir)

    @pytest.mark.asyncio
    async def test_save_and_get(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)

            data = b"Hello, FastHub storage!"
            path = await backend.save(data, "test.txt", organization_id="org-123")

            assert path  # Nie pusty
            assert "org-123" in path
            assert "test.txt" in path

            retrieved = await backend.get(path)
            assert retrieved == data

    @pytest.mark.asyncio
    async def test_delete(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)
            path = await backend.save(b"delete me", "del.txt")

            assert await backend.exists(path) == True
            result = await backend.delete(path)
            assert result == True
            assert await backend.exists(path) == False

    @pytest.mark.asyncio
    async def test_exists_false(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)
            assert await backend.exists("nonexistent/file.txt") == False

    @pytest.mark.asyncio
    async def test_get_url(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)
            path = await backend.save(b"test", "url_test.txt")
            url = await backend.get_url(path)
            assert url.startswith("/api/files/")

    @pytest.mark.asyncio
    async def test_path_generation_unique(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)
            path1 = await backend.save(b"a", "same.txt", organization_id="org-1")
            path2 = await backend.save(b"b", "same.txt", organization_id="org-1")
            assert path1 != path2  # Unikalne ścieżki

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self):
        from fasthub_core.storage.backends import LocalBackend
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = LocalBackend(base_dir=tmpdir)
            with pytest.raises(FileNotFoundError):
                await backend.get("does/not/exist.txt")


# ============================================================================
# S3 BACKEND
# ============================================================================

class TestS3Backend:

    def test_s3_requires_bucket(self):
        from fasthub_core.storage.backends import S3Backend
        with pytest.raises(ValueError, match="bucket"):
            S3Backend(bucket=None)

    def test_s3_constructor(self):
        from fasthub_core.storage.backends import S3Backend
        backend = S3Backend(bucket="test-bucket", region="eu-west-1")
        assert backend.bucket == "test-bucket"
        assert backend.region == "eu-west-1"


# ============================================================================
# CREATE BACKEND FACTORY
# ============================================================================

class TestCreateBackend:

    def test_create_backend_default_local(self):
        from fasthub_core.storage.backends import create_backend, LocalBackend
        backend = create_backend()
        assert isinstance(backend, LocalBackend)


# ============================================================================
# STORAGE SERVICE
# ============================================================================

class TestStorageService:

    def test_service_class(self):
        from fasthub_core.storage.service import StorageService
        assert hasattr(StorageService, "upload")
        assert hasattr(StorageService, "download")
        assert hasattr(StorageService, "delete")
        assert hasattr(StorageService, "list_files")
        assert hasattr(StorageService, "get_download_url")
        assert hasattr(StorageService, "get_storage_used_mb")

    def test_blocked_mime_types(self):
        from fasthub_core.storage.service import BLOCKED_MIME_TYPES
        assert "application/x-executable" in BLOCKED_MIME_TYPES
        assert "application/x-msdownload" in BLOCKED_MIME_TYPES

    def test_get_storage_service_factory(self):
        from fasthub_core.storage import get_storage_service
        assert callable(get_storage_service)


# ============================================================================
# FEATURE FLAGS
# ============================================================================

class TestFeatureFlags:

    def test_check_feature_function(self):
        from fasthub_core.billing.feature_flags import check_feature
        assert callable(check_feature)

    def test_get_plan_features_function(self):
        from fasthub_core.billing.feature_flags import get_plan_features
        assert callable(get_plan_features)

    def test_require_feature_returns_dependency(self):
        from fasthub_core.billing.feature_flags import require_feature
        dep = require_feature("webhooks")
        assert callable(dep)

    def test_require_feature_with_custom_message(self):
        from fasthub_core.billing.feature_flags import require_feature
        dep = require_feature("api_access", error_message="API wymaga planu Pro")
        assert callable(dep)

    def test_feature_flags_exported_from_billing(self):
        from fasthub_core.billing import check_feature, require_feature, get_plan_features
        assert callable(check_feature)
        assert callable(require_feature)
        assert callable(get_plan_features)


# ============================================================================
# CONFIG
# ============================================================================

class TestStorageConfig:

    @pytest.fixture(autouse=True)
    def _ensure_secret_key(self):
        """Ensure SECRET_KEY is set for Settings to load."""
        import fasthub_core.config as cfg
        cfg._settings = None  # Reset singleton
        os.environ.setdefault("SECRET_KEY", "test-secret-key-for-storage-tests")
        yield
        cfg._settings = None

    def test_config_has_storage_settings(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert hasattr(settings, "STORAGE_BACKEND")
        assert hasattr(settings, "STORAGE_LOCAL_DIR")
        assert hasattr(settings, "STORAGE_MAX_FILE_SIZE_MB")

    def test_config_has_s3_settings(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert hasattr(settings, "AWS_S3_BUCKET")
        assert hasattr(settings, "AWS_S3_REGION")

    def test_default_backend_local(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert settings.STORAGE_BACKEND == "local"

    def test_default_max_size_50mb(self):
        from fasthub_core.config import get_settings
        settings = get_settings()
        assert settings.STORAGE_MAX_FILE_SIZE_MB == 50.0


# ============================================================================
# INIT EXPORTS
# ============================================================================

class TestExports:

    def test_storage_init(self):
        from fasthub_core.storage import FileUpload, StorageService, get_storage_service
        assert FileUpload is not None
        assert StorageService is not None
        assert callable(get_storage_service)

    def test_storage_backends_init(self):
        from fasthub_core.storage import LocalBackend, S3Backend
        assert LocalBackend is not None
        assert S3Backend is not None
