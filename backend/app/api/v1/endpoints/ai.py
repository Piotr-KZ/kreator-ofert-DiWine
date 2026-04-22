"""
AI endpoints — structure, visual concept, content generation, chat.
"""

import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.schemas.creator import ChatMessage, GenerateRequest
from app.services.ai.engine import AIEngine

router = APIRouter()


async def _get_project_full(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.sections), selectinload(Project.materials))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")
    return project


@router.post("/projects/{project_id}/analyze-website")
async def analyze_website(
    project_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """AI reads a website and extracts brief data."""
    project = await _get_project_full(project_id, db)
    url = body.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="Brak URL")

    engine = AIEngine(db)
    result = await engine.analyze_website(url)
    return result


@router.post("/projects/{project_id}/validate-brief")
async def validate_brief(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """AI validates brief and returns feedback."""
    project = await _get_project_full(project_id, db)
    engine = AIEngine(db)
    items = await engine.validate_brief(project)
    return {"items": items}


@router.post("/projects/{project_id}/generate-structure")
async def generate_structure(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """AI generates page structure based on brief."""
    project = await _get_project_full(project_id, db)
    engine = AIEngine(db)

    sections_data = await engine.generate_structure(project)
    if not sections_data:
        raise HTTPException(status_code=500, detail="AI nie wygenerowalo struktury")

    # Clear existing sections and visual concept (tied to structure)
    for s in project.sections:
        await db.delete(s)
    project.visual_concept_json = None
    await db.flush()

    # Create new sections
    created = []
    for i, s_data in enumerate(sections_data):
        section = ProjectSection(
            id=str(uuid4()),
            project_id=project_id,
            block_code=s_data.get("block_code", s_data.get("block_id", "")),
            position=i,
        )
        db.add(section)
        created.append({
            "id": section.id,
            "block_code": section.block_code,
            "position": i,
            "title": s_data.get("title", ""),
        })

    project.current_step = max(project.current_step or 1, 3)
    await db.flush()

    return {"sections": created}


@router.post("/projects/{project_id}/generate-visual-concept")
async def generate_visual_concept(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """AI generates visual concept for each section."""
    project = await _get_project_full(project_id, db)
    if not project.sections:
        raise HTTPException(status_code=400, detail="Brak sekcji — najpierw wygeneruj strukture")

    engine = AIEngine(db)
    vc = await engine.generate_visual_concept(project)
    if not vc:
        raise HTTPException(status_code=500, detail="AI nie wygenerowalo visual concept")

    project.visual_concept_json = vc
    project.current_step = max(project.current_step or 1, 5)
    await db.flush()

    return vc


@router.get("/projects/{project_id}/visual-concept")
async def get_visual_concept(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_full(project_id, db)
    return project.visual_concept_json or {}


@router.put("/projects/{project_id}/visual-concept")
async def save_visual_concept(
    project_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_full(project_id, db)
    project.visual_concept_json = data
    await db.flush()
    return {"ok": True}


@router.post("/projects/{project_id}/generate-content")
async def generate_all_content(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate content for ALL sections."""
    project = await _get_project_full(project_id, db)
    if not project.sections:
        raise HTTPException(status_code=400, detail="Brak sekcji")

    engine = AIEngine(db)
    results = []

    for section in sorted(project.sections, key=lambda s: s.position):
        content = await engine.generate_content(project, section)
        if content:
            section.slots_json = content
            results.append({
                "section_id": section.id,
                "block_code": section.block_code,
                "slots_json": content,
            })

    project.current_step = max(project.current_step or 1, 4)
    await db.flush()

    return {"sections": results}


@router.post("/projects/{project_id}/sections/{section_id}/regenerate")
async def regenerate_section(
    project_id: str,
    section_id: str,
    body: GenerateRequest = GenerateRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate content for a single section."""
    project = await _get_project_full(project_id, db)

    section = None
    for s in project.sections:
        if s.id == section_id:
            section = s
            break
    if not section:
        raise HTTPException(status_code=404, detail="Sekcja nie znaleziona")

    engine = AIEngine(db)
    content = await engine.regenerate_section(project, section, body.instruction or "")
    if content:
        section.slots_json = content
        await db.flush()

    return {"section_id": section.id, "slots_json": content}


@router.post("/projects/{project_id}/chat")
async def chat(
    project_id: str,
    body: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    """Chat with AI about the project (SSE streaming)."""
    project = await _get_project_full(project_id, db)
    engine = AIEngine(db)

    async def event_stream():
        async for chunk in engine.chat_stream(project, body.message, frontend_context=body.context, current_step=body.step):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
