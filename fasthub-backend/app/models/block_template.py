"""
BlockCategory + BlockTemplate models — block library for the page builder.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class BlockCategory(BaseModel):
    __tablename__ = "block_categories"

    code = Column(String(5), unique=True, nullable=False, index=True)  # HE, FI, OF, CE...
    name = Column(String(100), nullable=False)
    icon = Column(String(50))  # lucide icon name
    order = Column(Integer, default=0)

    def __repr__(self):
        return f"<BlockCategory {self.code}: {self.name}>"


class BlockTemplate(BaseModel):
    __tablename__ = "block_templates"

    code = Column(String(10), unique=True, nullable=False, index=True)  # HE1, HE2, FI1...
    category_code = Column(String(5), ForeignKey("block_categories.code"), nullable=False, index=True)

    name = Column(String(255))
    description = Column(Text)  # AI hint: when to use this block

    # HTML template with placeholders
    html_template = Column(Text, nullable=False)
    css = Column(Text)

    # Slot definitions
    slots_definition = Column(JSONB, nullable=False)

    # Configurator tags
    media_type = Column(String(20))   # photo, video, infographic, table, chart, logo, opinion, none
    layout_type = Column(String(30))  # photo-top-1, photo-bottom-2, vid-full, info-title-3...
    photo_shape = Column(String(20))  # sharp, round-sm, round-lg, circle, blob, arch...
    text_style = Column(String(20))   # continuous, bullet, tagline

    # Variants (A/B/C)
    variants = Column(JSONB)

    # Metadata
    size = Column(String(1), default="M")  # S, M, L
    responsive = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Relations
    category = relationship("BlockCategory")

    def __repr__(self):
        return f"<BlockTemplate {self.code}: {self.name}>"
