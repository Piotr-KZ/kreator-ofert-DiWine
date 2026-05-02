import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel as PBase
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.offer_template import OfferTemplate
from app.models.project_section import ProjectSection

router = APIRouter(prefix="/offer-templates", tags=["offer-templates"])


class SaveTemplateReq(PBase):
    project_id: str
    name: str
    description: str = ""
    occasion_code: str = ""


class TemplateOut(PBase):
    id: str
    name: str
    description: str
    occasion_code: Optional[str]
    block_count: int
    created_at: Optional[str]


@router.post("")
async def save_as_template(data: SaveTemplateReq, db: AsyncSession = Depends(get_db)):
    """Save current project sections as reusable template."""
    result = await db.execute(
        select(ProjectSection).where(ProjectSection.project_id == data.project_id)
        .order_by(ProjectSection.position)
    )
    sections = result.scalars().all()
    if not sections:
        raise HTTPException(status_code=400, detail="Projekt nie ma sekcji")

    sections_data = [
        {"block_code": s.block_code, "slots_json": s.slots_json, "position": s.position}
        for s in sections
    ]

    tpl = OfferTemplate(
        name=data.name,
        description=data.description,
        occasion_code=data.occasion_code or None,
        sections_json=json.dumps(sections_data, ensure_ascii=False),
        block_count=len(sections_data),
    )
    db.add(tpl)
    await db.commit()
    await db.refresh(tpl)
    return {"id": tpl.id, "name": tpl.name, "block_count": tpl.block_count}


@router.get("")
async def list_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OfferTemplate).order_by(OfferTemplate.created_at.desc()))
    return [
        {"id": t.id, "name": t.name, "description": t.description,
         "occasion_code": t.occasion_code, "block_count": t.block_count,
         "created_at": str(t.created_at)[:10] if t.created_at else ""}
        for t in result.scalars().all()
    ]


@router.delete("/{template_id}")
async def delete_template(template_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OfferTemplate).where(OfferTemplate.id == template_id))
    tpl = result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404)
    await db.delete(tpl)
    await db.commit()
    return {"ok": True}


@router.post("/{template_id}/apply")
async def apply_template(template_id: str, project_id: str, db: AsyncSession = Depends(get_db)):
    """Apply template to existing project — replaces sections."""
    tpl_result = await db.execute(select(OfferTemplate).where(OfferTemplate.id == template_id))
    tpl = tpl_result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404, detail="Szablon nie znaleziony")

    # Delete existing sections
    existing = await db.execute(select(ProjectSection).where(ProjectSection.project_id == project_id))
    for s in existing.scalars().all():
        await db.delete(s)

    # Create new from template
    sections = json.loads(tpl.sections_json)
    from uuid import uuid4
    for s in sections:
        db.add(ProjectSection(
            id=str(uuid4()),
            project_id=project_id,
            block_code=s["block_code"],
            position=s["position"],
            slots_json=s.get("slots_json", {}),
        ))

    await db.commit()
    return {"ok": True, "sections_count": len(sections)}
