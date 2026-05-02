from sqlalchemy import Column, String, Text, Integer
from app.db.base import BaseModel


class OfferTemplate(BaseModel):
    __tablename__ = "offer_templates"

    name = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    occasion_code = Column(String(20))
    sections_json = Column(Text, nullable=False)  # JSON array of {block_code, slots_json, position}
    block_count = Column(Integer, default=0)
