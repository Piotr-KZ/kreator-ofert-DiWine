"""
Creator: Sections endpoints (steps 5-6).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.project_section import ProjectSection
from app.models.user import User
from app.schemas.creator import ReorderData, SectionCreate, SectionResponse, SectionUpdate
from app.services.creator.project_service import ProjectService

router = APIRouter()


@router.get("/{project_id}/sections", response_model=list[SectionResponse])
async def list_sections(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List project sections (sorted by position)."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    return project.sections


@router.post(
    "/{project_id}/sections",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_section(
    project_id: UUID,
    data: SectionCreate,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a section to the project."""
    svc = ProjectService(db)
    await svc.get_project_or_404(project_id, org.id)

    max_pos = await svc.get_max_position(project_id)
    position = data.position if data.position is not None else max_pos + 1

    section = ProjectSection(
        project_id=project_id,
        block_code=data.block_code,
        position=position,
        variant=data.variant or "A",
        slots_json=data.slots_json,
        variant_config=data.variant_config,
    )
    db.add(section)
    await db.flush()
    await db.refresh(section)
    return section


@router.patch("/{project_id}/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    project_id: UUID,
    section_id: UUID,
    data: SectionUpdate,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a section (content, variant, config)."""
    svc = ProjectService(db)
    section = await svc.get_section_or_404(section_id, project_id, org.id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(section, k, v)
    await db.flush()
    await db.refresh(section)
    return section


@router.delete("/{project_id}/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    project_id: UUID,
    section_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a section and renumber positions."""
    svc = ProjectService(db)
    section = await svc.get_section_or_404(section_id, project_id, org.id)
    await db.delete(section)
    await db.flush()
    await svc.renumber_positions(project_id)
    return None


@router.post("/{project_id}/sections/reorder")
async def reorder_sections(
    project_id: UUID,
    data: ReorderData,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reorder sections (drag & drop). data.order = [section_id_1, section_id_2, ...]"""
    svc = ProjectService(db)
    await svc.get_project_or_404(project_id, org.id)

    for i, section_id in enumerate(data.order):
        await db.execute(
            update(ProjectSection)
            .where(
                ProjectSection.id == section_id,
                ProjectSection.project_id == project_id,
            )
            .values(position=i)
        )
    return {"ok": True}
