"""
BlockCategory + BlockTemplate models — block library.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class BlockCategory(BaseModel):
    __tablename__ = "block_categories"

    code = Column(String(5), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50))
    order = Column(Integer, default=0)

    def __repr__(self):
        return f"<BlockCategory {self.code}: {self.name}>"


class BlockTemplate(BaseModel):
    __tablename__ = "block_templates"

    code = Column(String(10), unique=True, nullable=False, index=True)
    category_code = Column(String(5), ForeignKey("block_categories.code"), nullable=False, index=True)

    name = Column(String(255))
    description = Column(Text)

    html_template = Column(Text, nullable=False)
    css = Column(Text)

    slots_definition = Column(JSON)

    media_type = Column(String(20))
    layout_type = Column(String(30))
    photo_shape = Column(String(20))
    text_style = Column(String(20))

    variants = Column(JSON)

    size = Column(String(1), default="M")
    page_height = Column(String(2), default="F")  # F = Full page (każdy klocek = 1 strona)
    responsive = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    category = relationship("BlockCategory")

    def __repr__(self):
        return f"<BlockTemplate {self.code}: {self.name}>"
