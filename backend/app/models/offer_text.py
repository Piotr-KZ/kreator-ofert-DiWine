"""
OfferTextTemplate — library of pre-written text blocks for offers.
AI personalizes these, doesn't write from scratch.
"""

from sqlalchemy import Boolean, Column, Integer, String, Text
from app.db.base import BaseModel


class OfferTextTemplate(BaseModel):
    __tablename__ = "offer_text_templates"

    block_type = Column(String(30), nullable=False, index=True)
    occasion_code = Column(String(20), nullable=True, index=True)
    variant = Column(String(1), default="A")
    name = Column(String(100), nullable=False)
    template_text = Column(Text, nullable=False)
    tone = Column(String(20), default="profesjonalny")
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    def __repr__(self):
        return f"<OfferTextTemplate {self.block_type}/{self.occasion_code}/{self.variant}>"
