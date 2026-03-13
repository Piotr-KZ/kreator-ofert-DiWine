"""
Project service — helpers for project, section, and material operations.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from app.models.project import Project
from app.models.project_material import ProjectMaterial
from app.models.project_section import ProjectSection


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_or_404(self, project_id: UUID, org_id: UUID) -> Project:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.sections), selectinload(Project.materials))
            .where(Project.id == project_id, Project.organization_id == org_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    async def get_section_or_404(
        self, section_id: UUID, project_id: UUID, org_id: UUID
    ) -> ProjectSection:
        result = await self.db.execute(
            select(ProjectSection)
            .join(Project)
            .where(
                ProjectSection.id == section_id,
                ProjectSection.project_id == project_id,
                Project.organization_id == org_id,
            )
        )
        section = result.scalar_one_or_none()
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found",
            )
        return section

    async def get_material_or_404(
        self, material_id: UUID, project_id: UUID, org_id: UUID
    ) -> ProjectMaterial:
        result = await self.db.execute(
            select(ProjectMaterial)
            .join(Project)
            .where(
                ProjectMaterial.id == material_id,
                ProjectMaterial.project_id == project_id,
                Project.organization_id == org_id,
            )
        )
        material = result.scalar_one_or_none()
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found",
            )
        return material

    async def renumber_positions(self, project_id: UUID) -> None:
        result = await self.db.execute(
            select(ProjectSection)
            .where(ProjectSection.project_id == project_id)
            .order_by(ProjectSection.position)
        )
        sections = result.scalars().all()
        for i, section in enumerate(sections):
            section.position = i

    async def get_max_position(self, project_id: UUID) -> int:
        result = await self.db.execute(
            select(func.max(ProjectSection.position))
            .where(ProjectSection.project_id == project_id)
        )
        val = result.scalar_one_or_none()
        return val if val is not None else -1
