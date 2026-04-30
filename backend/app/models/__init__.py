# Import all models so SQLAlchemy can resolve relationships
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.models.project_material import ProjectMaterial
from app.models.block_template import BlockCategory, BlockTemplate
from app.models.offer import (
    Client, Supplier, Occasion, Product, Packaging,
    DiscountRule, Color, Offer, OfferSet, OfferSetItem,
)
from app.models.offer_text import OfferTextTemplate

__all__ = [
    "Project", "ProjectSection", "ProjectMaterial", "BlockCategory", "BlockTemplate",
    "Client", "Supplier", "Occasion", "Product", "Packaging",
    "DiscountRule", "Color", "Offer", "OfferSet", "OfferSetItem",
    "OfferTextTemplate",
]
