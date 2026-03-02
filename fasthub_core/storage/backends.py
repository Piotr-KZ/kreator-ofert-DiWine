"""
Storage backends — Local i S3.

Każdy backend implementuje ten sam interfejs:
- save(file_data, filename) -> storage_path
- get(storage_path) -> bytes
- delete(storage_path) -> bool
- get_url(storage_path, expires) -> presigned URL

Wybór automatyczny:
- Jeśli AWS_S3_BUCKET jest ustawiony -> S3Backend
- W przeciwnym razie -> LocalBackend

Użycie:
    from fasthub_core.storage.backends import create_backend

    backend = create_backend()           # Auto-detect
    backend = LocalBackend("/uploads")   # Explicit local
    backend = S3Backend("my-bucket")     # Explicit S3
"""

import uuid
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO, Union

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Interfejs storage backend."""

    @abstractmethod
    async def save(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        content_type: str = "application/octet-stream",
        organization_id: str = "",
    ) -> str:
        """
        Zapisz plik. Zwraca storage_path (unikalna ścieżka w storage).

        Organizacja plików: {org_id}/{YYYY-MM}/{uuid}_{filename}
        """
        ...

    @abstractmethod
    async def get(self, storage_path: str) -> bytes:
        """Pobierz plik jako bytes."""
        ...

    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """Usuń plik. Zwraca True jeśli sukces."""
        ...

    @abstractmethod
    async def get_url(
        self, storage_path: str, expires_in: int = 3600
    ) -> str:
        """
        Zwróć URL do pliku.
        - S3: presigned URL (wygasa po expires_in sekund)
        - Local: ścieżka relatywna (aplikacja serwuje)
        """
        ...

    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """Sprawdź czy plik istnieje."""
        ...

    def _generate_path(
        self, filename: str, organization_id: str = ""
    ) -> str:
        """
        Generuj unikalną ścieżkę: {org_id}/{YYYY-MM}/{uuid}_{filename}

        Zapobiega kolizjom nazw i organizuje pliki chronologicznie.
        """
        from datetime import datetime

        safe_filename = filename.replace("/", "_").replace("\\", "_")
        # Ogranicz długość oryginalnej nazwy
        if len(safe_filename) > 100:
            ext = safe_filename.rsplit(".", 1)[-1] if "." in safe_filename else ""
            safe_filename = safe_filename[:90] + ("." + ext if ext else "")

        unique = uuid.uuid4().hex[:12]
        month_dir = datetime.utcnow().strftime("%Y-%m")

        parts = []
        if organization_id:
            parts.append(str(organization_id))
        parts.append(month_dir)
        parts.append(f"{unique}_{safe_filename}")

        return "/".join(parts)


class LocalBackend(StorageBackend):
    """
    Local filesystem storage — development i single-server.

    Pliki w: {base_dir}/{org_id}/{YYYY-MM}/{uuid}_{filename}
    """

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            try:
                from fasthub_core.config import get_settings
                base_dir = getattr(get_settings(), "STORAGE_LOCAL_DIR", "./uploads")
            except Exception:
                base_dir = "./uploads"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(
        self, file_data, filename, content_type="application/octet-stream",
        organization_id="",
    ) -> str:
        storage_path = self._generate_path(filename, organization_id)
        full_path = self.base_dir / storage_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        data = file_data if isinstance(file_data, bytes) else file_data.read()
        full_path.write_bytes(data)

        logger.info(f"File saved locally: {storage_path} ({len(data)} bytes)")
        return storage_path

    async def get(self, storage_path: str) -> bytes:
        full_path = self.base_dir / storage_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")
        return full_path.read_bytes()

    async def delete(self, storage_path: str) -> bool:
        full_path = self.base_dir / storage_path
        if full_path.exists():
            full_path.unlink()
            logger.info(f"File deleted: {storage_path}")
            return True
        return False

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        # Local — zwracamy ścieżkę, aplikacja serwuje przez endpoint
        return f"/api/files/{storage_path}"

    async def exists(self, storage_path: str) -> bool:
        return (self.base_dir / storage_path).exists()


class S3Backend(StorageBackend):
    """
    AWS S3 storage — produkcja, multi-server.

    Wymaga: boto3, AWS credentials (env vars lub IAM role).

    Env vars:
        AWS_S3_BUCKET=my-app-uploads
        AWS_S3_REGION=eu-central-1
        AWS_ACCESS_KEY_ID=xxx          (lub IAM role)
        AWS_SECRET_ACCESS_KEY=xxx      (lub IAM role)
        AWS_S3_ENDPOINT_URL=...        (opcjonalnie, dla MinIO/Wasabi)
    """

    def __init__(
        self,
        bucket: str = None,
        region: str = None,
        endpoint_url: str = None,
    ):
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            self.bucket = bucket or getattr(settings, "AWS_S3_BUCKET", None)
            self.region = region or getattr(settings, "AWS_S3_REGION", "eu-central-1")
            self.endpoint_url = endpoint_url or getattr(settings, "AWS_S3_ENDPOINT_URL", None)
        except Exception:
            self.bucket = bucket
            self.region = region or "eu-central-1"
            self.endpoint_url = endpoint_url

        if not self.bucket:
            raise ValueError("S3 bucket name required (AWS_S3_BUCKET)")

        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            kwargs = {"region_name": self.region}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client("s3", **kwargs)
        return self._client

    async def save(
        self, file_data, filename, content_type="application/octet-stream",
        organization_id="",
    ) -> str:
        storage_path = self._generate_path(filename, organization_id)
        data = file_data if isinstance(file_data, bytes) else file_data.read()

        client = self._get_client()
        client.put_object(
            Bucket=self.bucket,
            Key=storage_path,
            Body=data,
            ContentType=content_type,
        )
        logger.info(f"File saved to S3: s3://{self.bucket}/{storage_path} ({len(data)} bytes)")
        return storage_path

    async def get(self, storage_path: str) -> bytes:
        client = self._get_client()
        response = client.get_object(Bucket=self.bucket, Key=storage_path)
        return response["Body"].read()

    async def delete(self, storage_path: str) -> bool:
        try:
            client = self._get_client()
            client.delete_object(Bucket=self.bucket, Key=storage_path)
            logger.info(f"File deleted from S3: {storage_path}")
            return True
        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Presigned URL — wygasa po expires_in sekund."""
        client = self._get_client()
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": storage_path},
            ExpiresIn=expires_in,
        )
        return url

    async def exists(self, storage_path: str) -> bool:
        try:
            client = self._get_client()
            client.head_object(Bucket=self.bucket, Key=storage_path)
            return True
        except Exception:
            return False


def create_backend() -> StorageBackend:
    """
    Factory — auto-detect backend.

    S3 jeśli AWS_S3_BUCKET ustawiony, inaczej Local.
    """
    try:
        from fasthub_core.config import get_settings
        settings = get_settings()
        if getattr(settings, "AWS_S3_BUCKET", None):
            return S3Backend()
    except Exception:
        pass
    return LocalBackend()
