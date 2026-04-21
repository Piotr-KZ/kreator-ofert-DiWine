"""
ProjectSection model — one section/block on a page.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class ProjectSection(BaseModel):
    __tablename__ = "project_sections"

    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    block_code = Column(String(10), nullable=False)  # HE1, FI3, CT2
    position = Column(Integer, nullable=False)
    variant = Column(String(1), default="A")  # A, B, C

    slots_json = Column(JSON)  # slot content
    variant_config = Column(JSON)  # variant configuration

    is_visible = Column(Boolean, default=True)

    project = relationship("Project", back_populates="sections")

    def __repr__(self):
        return f"<ProjectSection {self.block_code} pos={self.position}>"
