"""
FormSubmission model — stores form submissions from published sites.
"""

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from fasthub_core.db.base import BaseModel


class FormSubmission(BaseModel):
    __tablename__ = "form_submissions"

    site_id = Column(UUID(as_uuid=True), ForeignKey("published_sites.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    data_json = Column(JSONB, nullable=False)
    ip = Column(String(45))
    user_agent = Column(Text)
    read = Column(Boolean, default=False)

    def __repr__(self):
        return f"<FormSubmission {self.id}>"
