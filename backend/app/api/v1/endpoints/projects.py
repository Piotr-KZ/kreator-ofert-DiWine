"""
Project CRUD endpoints for Lab Creator.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.schemas.creator import ProjectCreate, ProjectUpdate, ReorderSections, SectionUpdate

router = APIRouter()


async def _get_project(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.sections), selectinload(Project.materials))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")
    return project


@router.post("/projects")
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(id=str(uuid4()), name=data.name, site_type=data.site_type)
    db.add(project)
    await db.flush()
    return {"id": project.id, "name": project.name, "site_type": project.site_type}


@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "site_type": p.site_type,
            "status": p.status,
            "current_step": p.current_step,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in projects
    ]


@router.get("/projects/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _get_project(project_id, db)
    return {
        "id": project.id,
        "name": project.name,
        "site_type": project.site_type,
        "status": project.status,
        "current_step": project.current_step,
        "brief_json": project.brief_json,
        "style_json": project.style_json,
        "visual_concept_json": project.visual_concept_json,
        "sections": [
            {
                "id": s.id,
                "block_code": s.block_code,
                "position": s.position,
                "variant": s.variant,
                "slots_json": s.slots_json,
                "is_visible": s.is_visible,
                "variant_config": s.variant_config,
            }
            for s in sorted(project.sections, key=lambda x: x.position)
        ],
    }


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    project = await _get_project(project_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    await db.flush()
    return {"ok": True}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _get_project(project_id, db)
    await db.delete(project)
    return {"ok": True}


# ─── SECTIONS ───

@router.post("/projects/{project_id}/sections")
async def add_section(project_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    project = await _get_project(project_id, db)
    position = data.get("position", len(project.sections))
    # Shift existing sections at positions >= new position
    for s in project.sections:
        if s.position >= position:
            s.position += 1
    section = ProjectSection(
        id=str(uuid4()),
        project_id=project_id,
        block_code=data["block_code"],
        position=position,
    )
    db.add(section)
    await db.flush()
    return {"id": section.id, "block_code": section.block_code, "position": section.position}


@router.patch("/projects/{project_id}/sections/{section_id}")
async def update_section(project_id: str, section_id: str, data: SectionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSection).where(
            ProjectSection.id == section_id,
            ProjectSection.project_id == project_id,
        )
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Sekcja nie znaleziona")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(section, key, value)
    await db.flush()
    return {"ok": True}


@router.delete("/projects/{project_id}/sections/{section_id}")
async def delete_section(project_id: str, section_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSection).where(
            ProjectSection.id == section_id,
            ProjectSection.project_id == project_id,
        )
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Sekcja nie znaleziona")
    await db.delete(section)
    return {"ok": True}


@router.post("/projects/{project_id}/sections/{section_id}/duplicate")
async def duplicate_section(project_id: str, section_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectSection).where(
            ProjectSection.id == section_id,
            ProjectSection.project_id == project_id,
        )
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="Sekcja nie znaleziona")
    # Przesuń sekcje poniżej o +1
    all_result = await db.execute(
        select(ProjectSection).where(
            ProjectSection.project_id == project_id,
            ProjectSection.position > section.position,
        )
    )
    for s in all_result.scalars().all():
        s.position += 1
    new_section = ProjectSection(
        id=str(uuid4()),
        project_id=project_id,
        block_code=section.block_code,
        position=section.position + 1,
        variant=section.variant,
        slots_json=section.slots_json,
        is_visible=section.is_visible,
    )
    db.add(new_section)
    await db.flush()
    return {"id": new_section.id, "position": new_section.position}


@router.post("/projects/{project_id}/sections/reorder")
async def reorder_sections(project_id: str, data: ReorderSections, db: AsyncSession = Depends(get_db)):
    project = await _get_project(project_id, db)
    section_map = {s.id: s for s in project.sections}
    for i, sid in enumerate(data.section_ids):
        if sid in section_map:
            section_map[sid].position = i
    await db.flush()
    return {"ok": True}
