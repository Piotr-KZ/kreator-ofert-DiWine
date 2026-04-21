"""
ProjectMaterial model — uploaded files (logo).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class ProjectMaterial(BaseModel):
    __tablename__ = "project_materials"

    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(String(20), nullable=False)  # logo, photo
    file_url = Column(String(500))
    original_filename = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    description = Column(Text)

    project = relationship("Project", back_populates="materials")

    def __repr__(self):
        return f"<ProjectMaterial {self.type} ({self.original_filename})>"
