"""
FileUpload — metadane uploadu pliku.

Plik fizycznie żyje w storage (local/S3).
Ten model trzyma: kto uploadował, kiedy, ile waży, jaki typ, ścieżka w storage.

Relacje:
- organization_id: do której organizacji należy plik
- uploaded_by: UUID usera
- entity_type + entity_id: do czego jest przypisany (np. process, user_avatar, invoice)
"""

from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from fasthub_core.db.session import Base


class FileUpload(Base):
    """Metadane uploadowanego pliku."""

    __tablename__ = "file_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Kto i skąd
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)

    # Plik
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)  # UUID-based, unique
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_size_mb = Column(Float, nullable=False)  # Dla billing tracking

    # Storage
    storage_backend = Column(String(20), nullable=False)  # "local" | "s3"
    storage_path = Column(String(1000), nullable=False)     # Pełna ścieżka w storage
    storage_bucket = Column(String(100), nullable=True)     # S3 bucket name (null dla local)

    # Kontekst (do czego przypisany)
    entity_type = Column(String(50), nullable=True, index=True)   # "process", "avatar", "invoice", "attachment"
    entity_id = Column(String(100), nullable=True, index=True)    # UUID encji

    # Opis
    description = Column(Text, nullable=True)

    # Status
    is_public = Column(Boolean, default=False)          # Czy dostępny bez auth
    is_deleted = Column(Boolean, default=False)          # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_file_org_entity", "organization_id", "entity_type", "entity_id"),
        Index("ix_file_org_created", "organization_id", "created_at"),
    )

    def __repr__(self):
        return f"<FileUpload {self.original_filename} ({self.file_size_mb:.1f} MB)>"
