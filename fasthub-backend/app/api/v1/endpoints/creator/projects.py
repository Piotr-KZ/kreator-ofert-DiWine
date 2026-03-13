"""
Creator: Projects CRUD endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.models.user import User
from app.models.organization import Organization
from app.schemas.creator import ProjectCreate, ProjectListItem, ProjectResponse, ProjectUpdate
from app.services.creator.project_service import ProjectService

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Create a new website project."""
    project = Project(
        organization_id=org.id,
        created_by=current_user.id,
        name=data.name,
        site_type=data.site_type,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.get("", response_model=list[ProjectListItem])
async def list_projects(
    status_filter: str | None = None,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List projects for the current organization."""
    query = select(Project).where(Project.organization_id == org.id)
    if status_filter:
        query = query.where(Project.status == status_filter)
    query = query.order_by(Project.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get project details with sections and materials."""
    svc = ProjectService(db)
    return await svc.get_project_or_404(project_id, org.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update project (name, status, current_step)."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(project, k, v)
    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete project (cascade: sections, materials, conversations)."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    await db.delete(project)
    return None


@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Duplicate a project (copy with new name, status=draft)."""
    svc = ProjectService(db)
    source = await svc.get_project_or_404(project_id, org.id)

    new_project = Project(
        organization_id=org.id,
        created_by=current_user.id,
        name=f"{source.name} (kopia)",
        site_type=source.site_type,
        brief_json=source.brief_json,
        style_json=source.style_json,
        config_json=source.config_json,
    )
    db.add(new_project)
    await db.flush()

    # Copy sections
    for section in source.sections:
        db.add(ProjectSection(
            project_id=new_project.id,
            block_code=section.block_code,
            position=section.position,
            variant=section.variant,
            slots_json=section.slots_json,
            variant_config=section.variant_config,
        ))
    await db.flush()
    await db.refresh(new_project)
    return new_project
