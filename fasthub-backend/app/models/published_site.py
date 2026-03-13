"""
PublishedSite model — snapshot of a published website + hosting config.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fasthub_core.db.base import BaseModel


class PublishedSite(BaseModel):
    __tablename__ = "published_sites"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), unique=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    # Hosting
    subdomain = Column(String(100), unique=True)
    custom_domain = Column(String(255), unique=True)
    ssl_status = Column(String(20), default="pending")  # pending, active, error

    # Snapshot (generated on publish)
    html_snapshot = Column(Text)
    css_snapshot = Column(Text)
    assets_json = Column(JSONB)

    # Config (from step 7)
    seo_json = Column(JSONB)
    tracking_json = Column(JSONB)
    legal_json = Column(JSONB)
    forms_json = Column(JSONB)

    # Status
    is_active = Column(Boolean, default=True)
    published_at = Column(DateTime, server_default=func.now())
    last_updated_at = Column(DateTime, server_default=func.now())

    # Relations
    project = relationship("Project")
    organization = relationship("Organization", back_populates="published_sites")
    form_submissions = relationship("FormSubmission", backref="site", cascade="all, delete-orphan")
    integrations = relationship("SiteIntegration", backref="site", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PublishedSite {self.subdomain}>"
