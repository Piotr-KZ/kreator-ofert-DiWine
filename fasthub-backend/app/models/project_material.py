"""
ProjectMaterial model — client-uploaded files (logo, photos, documents).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class ProjectMaterial(BaseModel):
    __tablename__ = "project_materials"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(String(20), nullable=False)  # logo, photo, document, presentation, link, inspiration

    # File (in WebCreator Storage)
    file_url = Column(String(500))
    original_filename = Column(String(255))
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(100))

    # Or link (for inspiration/competitor)
    external_url = Column(String(500))

    # Metadata
    description = Column(Text)
    ai_extracted_text = Column(Text)  # AI extracts text from PDF/DOCX (Brief 31)
    metadata_json = Column(JSONB)

    # Relations
    project = relationship("Project", back_populates="materials")

    def __repr__(self):
        return f"<ProjectMaterial {self.type} ({self.original_filename or self.external_url})>"
