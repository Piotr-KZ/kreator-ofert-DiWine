"""
Project model — main WebCreator object.
One project = one website being built or published.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Basic
    name = Column(String(255), nullable=False)
    site_type = Column(String(50))  # firmowa, lp_produktowa, wizytowka, sklep, portfolio, blog

    # Status flow: draft -> generating -> validating -> building -> published -> archived
    status = Column(String(20), default="draft", index=True)
    current_step = Column(Integer, default=1)  # 1-9

    # Step data (JSONB)
    brief_json = Column(JSONB)
    materials_meta = Column(JSONB)
    style_json = Column(JSONB)
    validation_json = Column(JSONB)
    config_json = Column(JSONB)
    check_json = Column(JSONB)
    ai_visibility = Column(JSONB, default={})

    # Publishing
    domain = Column(String(255))
    custom_domain = Column(String(255))
    published_at = Column(DateTime)

    # Relations
    organization = relationship("Organization", backref="projects")
    creator = relationship("User")
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
    ai_conversations = relationship(
        "AIConversation",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project {self.name} ({self.status})>"
