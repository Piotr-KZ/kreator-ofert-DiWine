"""
StorageService — upload, download, delete z walidacją i billing tracking.

Łączy:
- Backend (local/S3) — fizyczny zapis
- Model FileUpload — metadane w bazie
- BillingService — tracking storage_used_mb

Walidacja:
- Max rozmiar pliku (default: 50 MB, konfigurowalny)
- Dozwolone MIME types (konfigurowalny)
- Sprawdzenie limitu storage z planu billing

Użycie:
    from fasthub_core.storage import StorageService, get_storage_service

    service = get_storage_service(db)

    file_record = await service.upload(
        file_data=file.file.read(),
        filename=file.filename,
        mime_type=file.content_type,
        organization_id=str(org.id),
        uploaded_by=str(user.id),
        entity_type="process_attachment",
        entity_id=str(process.id),
    )

    url = await service.get_download_url(file_record.id)
    await service.delete(file_record.id)
"""

import logging
from typing import Optional, List, BinaryIO, Union
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.storage.models import FileUpload
from fasthub_core.storage.backends import StorageBackend, create_backend

logger = logging.getLogger(__name__)


# Domyślne limity — aplikacja może nadpisać
DEFAULT_MAX_FILE_SIZE_MB: float = 50.0
DEFAULT_ALLOWED_MIME_TYPES: Optional[list] = None  # None = wszystkie dozwolone

# Niebezpieczne MIME types — zawsze blokowane
BLOCKED_MIME_TYPES = [
    "application/x-executable",
    "application/x-msdownload",
    "application/x-msdos-program",
]


class StorageService:
    """Serwis zarządzania plikami z walidacją i billing."""

    def __init__(
        self,
        db: AsyncSession,
        backend: StorageBackend = None,
        max_file_size_mb: float = DEFAULT_MAX_FILE_SIZE_MB,
        allowed_mime_types: Optional[list] = DEFAULT_ALLOWED_MIME_TYPES,
    ):
        self.db = db
        self.backend = backend or create_backend()
        self.max_file_size_mb = max_file_size_mb
        self.allowed_mime_types = allowed_mime_types

    # === UPLOAD ===

    async def upload(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        mime_type: str,
        organization_id: str,
        uploaded_by: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        description: Optional[str] = None,
        is_public: bool = False,
        check_billing_limit: bool = True,
    ) -> FileUpload:
        """
        Upload pliku z walidacją.

        1. Waliduj rozmiar i MIME type
        2. (Opcjonalnie) Sprawdź billing limit storage
        3. Zapisz w backend (local/S3)
        4. Stwórz rekord FileUpload w bazie
        5. Zaktualizuj billing storage_used_mb

        Returns:
            FileUpload record

        Raises:
            ValueError: Plik za duży lub niedozwolony typ
            PermissionError: Billing limit storage przekroczony
        """
        # 1. Pobierz dane jako bytes
        data = file_data if isinstance(file_data, bytes) else file_data.read()
        file_size_bytes = len(data)
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

        # 2. Walidacja rozmiaru
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(
                f"Plik za duży: {file_size_mb:.1f} MB (max: {self.max_file_size_mb:.0f} MB)"
            )

        # 3. Walidacja MIME type
        if mime_type in BLOCKED_MIME_TYPES:
            raise ValueError(f"Zablokowany typ pliku: {mime_type}")
        if self.allowed_mime_types and mime_type not in self.allowed_mime_types:
            raise ValueError(f"Niedozwolony typ pliku: {mime_type}")

        # 4. Billing limit check
        if check_billing_limit:
            await self._check_storage_limit(organization_id, file_size_mb)

        # 5. Zapisz w backend
        storage_path = await self.backend.save(
            file_data=data,
            filename=filename,
            content_type=mime_type,
            organization_id=organization_id,
        )

        # 6. Stwórz rekord w bazie
        backend_name = "s3" if hasattr(self.backend, "bucket") else "local"
        bucket_name = getattr(self.backend, "bucket", None)

        file_record = FileUpload(
            organization_id=UUID(organization_id),
            uploaded_by=UUID(uploaded_by),
            original_filename=filename,
            stored_filename=storage_path.split("/")[-1],
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            file_size_mb=file_size_mb,
            storage_backend=backend_name,
            storage_path=storage_path,
            storage_bucket=bucket_name,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            is_public=is_public,
        )
        self.db.add(file_record)
        await self.db.flush()

        # 7. Billing tracking
        await self._track_storage_usage(organization_id, file_size_mb)

        logger.info(
            f"File uploaded: {filename} ({file_size_mb:.1f} MB) "
            f"org={organization_id} entity={entity_type}:{entity_id}"
        )
        return file_record

    # === DOWNLOAD ===

    async def download(self, file_id: UUID) -> tuple:
        """
        Pobierz plik.

        Returns:
            (bytes, FileUpload) — dane pliku + metadane

        Raises:
            FileNotFoundError: Plik nie istnieje lub usunięty
        """
        record = await self._get_record(file_id)
        data = await self.backend.get(record.storage_path)
        return data, record

    async def get_download_url(
        self, file_id: UUID, expires_in: int = 3600
    ) -> str:
        """
        Zwróć URL do pobrania pliku.

        S3: presigned URL (tymczasowy, bezpieczny).
        Local: ścieżka serwowana przez endpoint.
        """
        record = await self._get_record(file_id)
        return await self.backend.get_url(record.storage_path, expires_in)

    # === DELETE ===

    async def delete(self, file_id: UUID, soft: bool = True) -> bool:
        """
        Usuń plik.

        soft=True (default): oznacz jako usunięty, nie kasuj fizycznie.
        soft=False: kasuj fizycznie z storage + z bazy.
        """
        record = await self._get_record(file_id)

        if soft:
            from datetime import datetime
            record.is_deleted = True
            record.deleted_at = datetime.utcnow()
        else:
            await self.backend.delete(record.storage_path)
            await self.db.delete(record)

        # Billing — zwolnij storage
        await self._track_storage_usage(
            str(record.organization_id), -record.file_size_mb
        )
        await self.db.flush()

        logger.info(f"File {'soft-' if soft else ''}deleted: {record.original_filename}")
        return True

    # === LIST ===

    async def list_files(
        self,
        organization_id: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FileUpload]:
        """Lista plików z filtrami."""
        query = select(FileUpload).where(
            FileUpload.organization_id == UUID(organization_id)
        )

        if not include_deleted:
            query = query.where(FileUpload.is_deleted == False)
        if entity_type:
            query = query.where(FileUpload.entity_type == entity_type)
        if entity_id:
            query = query.where(FileUpload.entity_id == entity_id)

        query = query.order_by(FileUpload.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # === STORAGE STATS ===

    async def get_storage_used_mb(self, organization_id: str) -> float:
        """Ile MB zużywa organizacja."""
        result = await self.db.execute(
            select(func.sum(FileUpload.file_size_mb)).where(
                FileUpload.organization_id == UUID(organization_id),
                FileUpload.is_deleted == False,
            )
        )
        return round(result.scalar() or 0.0, 2)

    # === PRIVATE ===

    async def _get_record(self, file_id: UUID) -> FileUpload:
        result = await self.db.execute(
            select(FileUpload).where(
                FileUpload.id == file_id,
                FileUpload.is_deleted == False,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise FileNotFoundError(f"File not found: {file_id}")
        return record

    async def _check_storage_limit(
        self, organization_id: str, additional_mb: float
    ) -> None:
        """Sprawdź czy organizacja ma miejsce w planie."""
        try:
            from fasthub_core.billing.service import BillingService
            billing = BillingService(self.db)
            limit_mb = await billing.get_effective_limit(organization_id, "storage_mb")
            if limit_mb <= 0:
                return  # Billing wyłączony lub brak limitu

            used_mb = await self.get_storage_used_mb(organization_id)
            if used_mb + additional_mb > limit_mb:
                raise PermissionError(
                    f"Limit storage przekroczony: {used_mb:.1f} + {additional_mb:.1f} > {limit_mb:.0f} MB. "
                    f"Zmień plan lub dokup add-on storage."
                )
        except ImportError:
            pass  # Billing nie zainstalowany — nie blokuj

    async def _track_storage_usage(
        self, organization_id: str, delta_mb: float
    ) -> None:
        """Zaktualizuj billing counter storage_used_mb."""
        try:
            from fasthub_core.billing.service import BillingService
            billing = BillingService(self.db)
            if delta_mb > 0:
                await billing.increment_usage(organization_id, "storage_mb", int(delta_mb * 100) / 100)
            # Dla ujemnego delta — billing.decrement lub recalculate
        except Exception:
            pass  # Non-critical


def get_storage_service(
    db: AsyncSession,
    backend: StorageBackend = None,
) -> StorageService:
    """Factory — stwórz StorageService."""
    return StorageService(db=db, backend=backend)
