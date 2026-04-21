# Import all models so SQLAlchemy can resolve relationships
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.models.project_material import ProjectMaterial
from app.models.block_template import BlockCategory, BlockTemplate

__all__ = ["Project", "ProjectSection", "ProjectMaterial", "BlockCategory", "BlockTemplate"]
