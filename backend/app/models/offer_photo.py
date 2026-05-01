"""
OfferPhoto — lifestyle/product photos for offer pages.
"""

from sqlalchemy import Column, String, Boolean, Integer, Text

from app.db.base import BaseModel


class OfferPhoto(BaseModel):
    __tablename__ = "offer_photos"

    url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    query = Column(String(200), nullable=True)
    category = Column(String(30), nullable=False, index=True)   # christmas, easter, lifestyle, wine, gift, universal
    photographer_name = Column(String(100), nullable=True)
    photographer_url = Column(Text, nullable=True)
    source = Column(String(20), default="unsplash")             # unsplash, diwine, upload
    is_default = Column(Boolean, default=False)                 # default photo for this category
    is_active = Column(Boolean, default=True)
    tags_json = Column(Text, nullable=True)                     # JSON array of Polish tag strings
    orientation = Column(String(20), default="landscape")
    width = Column(Integer, default=1200)
    height = Column(Integer, default=800)
