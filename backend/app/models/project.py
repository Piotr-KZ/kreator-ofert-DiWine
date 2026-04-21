"""
Project model — main Lab Creator object.
"""

from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    site_type = Column(String(50))  # company_card, company, lp_product, lp_service, expert

    status = Column(String(20), default="draft", index=True)
    current_step = Column(Integer, default=1)  # 1-5

    # Step data (JSON)
    brief_json = Column(JSON)       # {description, target_audience, usp, tone}
    style_json = Column(JSON)       # {primary_color, secondary_color}
    visual_concept_json = Column(JSON)  # {style, bg_approach, separators, sections[]}

    # Relations
    sections = relationship(
        "ProjectSection",
        back_populates="project",
        order_by="ProjectSection.position",
        cascade="all, delete-orphan",
    )
    materials = relationship(
        "ProjectMaterial",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project {self.name} ({self.status})>"
