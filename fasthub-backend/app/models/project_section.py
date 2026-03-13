"""
ProjectSection model — one section/block on a page.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class ProjectSection(BaseModel):
    __tablename__ = "project_sections"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    block_code = Column(String(10), nullable=False)  # HE1, FI3, CT2
    position = Column(Integer, nullable=False)
    variant = Column(String(1), default="A")  # A, B, C

    # Slot content (AI-generated or user-edited)
    slots_json = Column(JSONB)
    # Variant configuration (media type, layout, etc.)
    variant_config = Column(JSONB)

    is_visible = Column(Boolean, default=True)

    # Relations
    project = relationship("Project", back_populates="sections")

    def __repr__(self):
        return f"<ProjectSection {self.block_code} pos={self.position}>"
