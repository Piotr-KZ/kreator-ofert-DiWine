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
from app.services.creator.renderer import PageRenderer
from app.services.media.unsplash import UnsplashService

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


def _ai_error(e: Exception) -> HTTPException:
    """Convert RuntimeError from ClaudeClient into a proper HTTP 502 response."""
    return HTTPException(status_code=502, detail=str(e))


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

    try:
        engine = AIEngine(db)
        result = await engine.analyze_website(url)
    except RuntimeError as e:
        raise _ai_error(e)
    return result


@router.post("/projects/{project_id}/validate-brief")
async def validate_brief(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """AI validates brief and returns feedback."""
    project = await _get_project_full(project_id, db)
    try:
        engine = AIEngine(db)
        items = await engine.validate_brief(project)
    except RuntimeError as e:
        raise _ai_error(e)
    return {"items": items}


@router.post("/projects/{project_id}/generate-structure")
async def generate_structure(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """AI generates page structure based on brief."""
    project = await _get_project_full(project_id, db)
    try:
        engine = AIEngine(db)
        sections_data = await engine.generate_structure(project)
    except RuntimeError as e:
        raise _ai_error(e)
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
        bg_color = s_data.get("bg_color")
        variant_config = {"name": s_data.get("title", ""), "bgColor": bg_color} if (s_data.get("title") or bg_color) else None
        section = ProjectSection(
            id=str(uuid4()),
            project_id=project_id,
            block_code=s_data.get("block_code", s_data.get("block_id", "")),
            position=i,
            variant_config=variant_config,
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

    try:
        engine = AIEngine(db)
        vc = await engine.generate_visual_concept(project)
    except RuntimeError as e:
        raise _ai_error(e)
    if not vc:
        raise HTTPException(status_code=500, detail="AI nie wygenerowalo visual concept")

    project.visual_concept_json = vc
    project.current_step = max(project.current_step or 1, 5)
    await db.flush()

    # Resolve media — fetch real Unsplash photos for sections with photo_query
    unsplash = UnsplashService()
    if unsplash.enabled:
        renderer = PageRenderer()
        await renderer.resolve_media(project, unsplash)
        await db.flush()

    # Commit before returning — frontend immediately calls loadProject which needs committed data
    await db.commit()
    return vc


@router.post("/projects/{project_id}/resolve-media")
async def resolve_media(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch real Unsplash photos for all sections with photo_query in visual concept."""
    project = await _get_project_full(project_id, db)
    if not project.visual_concept_json:
        raise HTTPException(status_code=400, detail="Brak visual concept — najpierw wygeneruj")

    unsplash = UnsplashService()
    if not unsplash.enabled:
        raise HTTPException(status_code=500, detail="Unsplash API nie skonfigurowane (brak UNSPLASH_ACCESS_KEY)")

    renderer = PageRenderer()
    await renderer.resolve_media(project, unsplash)
    await db.flush()

    # Return updated sections with image URLs
    return {
        "resolved": True,
        "sections": [
            {"id": str(s.id), "block_code": s.block_code, "image": (s.slots_json or {}).get("image") or (s.slots_json or {}).get("hero_image")}
            for s in project.sections
        ],
    }


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

    try:
        engine = AIEngine(db)
    except RuntimeError as e:
        raise _ai_error(e)
    results = []

    for section in sorted(project.sections, key=lambda s: s.position):
        try:
            content = await engine.generate_content(project, section)
        except RuntimeError as e:
            raise _ai_error(e)
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

    try:
        engine = AIEngine(db)
        content = await engine.regenerate_section(project, section, body.instruction or "")
    except RuntimeError as e:
        raise _ai_error(e)
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
