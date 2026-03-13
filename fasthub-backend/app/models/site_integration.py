"""
SiteIntegration model — integration connected to a published site.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from fasthub_core.db.base import BaseModel


class SiteIntegration(BaseModel):
    __tablename__ = "site_integrations"

    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("published_sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(50), nullable=False)  # google_analytics, hotjar, mailchimp...
    status = Column(String(20), default="configured")  # configured, connected, error
    config_json = Column(JSONB)  # {tracking_id: "G-XXX"} or {api_key: "xxx"}

    connected_at = Column(DateTime, server_default=func.now())
    last_sync_at = Column(DateTime)

    def __repr__(self):
        return f"<SiteIntegration {self.provider} site={self.site_id}>"
