"""
Creator: AI Engine endpoints — validation, generation, chat (SSE), vision, legal, readiness.
"""

import json
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_active_user, get_current_organization, get_current_superuser
from app.db.session import get_db
from app.models.ai_conversation import AIConversation, AIGenerationLog
from app.models.block_template import BlockTemplate
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User
from app.services.ai.engine import AIEngine
from app.services.ai.vision import AIVisionService
from app.services.creator.renderer import PageRenderer

router = APIRouter()


# ─── Schemas ───

class ChatMessage(BaseModel):
    context: str  # "validation" | "structure" | "editing" | "config"
    message: str


class GenerateInstruction(BaseModel):
    instruction: str | None = None


# ─── Helpers ───

async def _get_project_with_data(
    project_id: UUID, org_id: UUID, db: AsyncSession
) -> Project:
    """Load project with sections and materials, scoped to organization."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.sections), selectinload(Project.materials))
        .where(Project.id == project_id, Project.organization_id == org_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


async def _get_or_create_conversation(
    db: AsyncSession, project_id: UUID, context: str
) -> AIConversation:
    """Get existing or create new AI conversation for project+context."""
    result = await db.execute(
        select(AIConversation).where(
            AIConversation.project_id == project_id,
            AIConversation.context == context,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        conversation = AIConversation(
            project_id=project_id,
            context=context,
            messages_json=[],
        )
        db.add(conversation)
        await db.flush()
    return conversation


# ─── Endpoints ───

@router.post("/{project_id}/ai/validate")
async def validate_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 4: AI validates project consistency."""
    project = await _get_project_with_data(project_id, org.id, db)
    engine = AIEngine(db)
    items = await engine.validate_project(project)
    return {"items": items}


@router.post("/{project_id}/ai/generate-structure")
async def generate_structure(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 5: AI generates page structure (list of sections with content)."""
    project = await _get_project_with_data(project_id, org.id, db)
    engine = AIEngine(db)
    sections = await engine.generate_structure(project)
    return {"sections": sections}


@router.post("/{project_id}/ai/chat")
async def chat_with_ai(
    project_id: UUID,
    data: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Chat with AI — streaming (SSE)."""
    if data.context not in ("validation", "structure", "editing", "config"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid context"
        )

    project = await _get_project_with_data(project_id, org.id, db)
    conversation = await _get_or_create_conversation(db, project_id, data.context)

    engine = AIEngine(db)

    async def stream_generator():
        async for chunk in engine.chat_stream(
            project, data.context, data.message, conversation
        ):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"
        await db.flush()

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.post("/{project_id}/ai/visual-review")
async def visual_review(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 6: 'AI Preview' button — AI reviews the page visually."""
    project = await _get_project_with_data(project_id, org.id, db)
    vision = AIVisionService(db)
    review = await vision.visual_review(project)
    return review


@router.post("/{project_id}/ai/legal/{doc_type}")
async def generate_legal(
    project_id: UUID,
    doc_type: str,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 7: AI generates legal document (privacy_policy, terms, rodo_clause, cookie_info)."""
    if doc_type not in ("privacy_policy", "terms", "rodo_clause", "cookie_info"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid doc_type"
        )
    project = await _get_project_with_data(project_id, org.id, db)
    engine = AIEngine(db)
    html = await engine.generate_legal(project, doc_type)
    return {"html": html, "doc_type": doc_type}


@router.post("/{project_id}/ai/check")
async def check_readiness(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 8: AI checks publishing readiness."""
    project = await _get_project_with_data(project_id, org.id, db)
    engine = AIEngine(db)
    checks = await engine.check_readiness(project)

    # Save in project
    project.check_json = {
        "checks": checks,
        "checked_at": datetime.utcnow().isoformat(),
    }
    await db.flush()

    return {"checks": checks}


@router.post("/{project_id}/ai/generate-site")
async def generate_site(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 4→5: AI generates full site (structure + content). SSE progress stream."""
    project = await _get_project_with_data(project_id, org.id, db)

    engine = AIEngine(db)

    async def progress_stream():
        # Step 1: Generate structure
        yield f"data: {json.dumps({'status': 'generating', 'message': 'AI projektuje strukturę strony...', 'progress': 10})}\n\n"

        try:
            sections_data = await engine.generate_structure(project)
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
            return

        yield f"data: {json.dumps({'status': 'generating', 'message': 'Struktura gotowa, piszę treści...', 'progress': 30})}\n\n"

        # Step 2: Create sections in DB
        from app.models.project_section import ProjectSection

        created_sections = []
        for i, sec in enumerate(sections_data):
            section = ProjectSection(
                project_id=project.id,
                block_code=sec.get("block_code", "HE1"),
                position=i,
                variant="A",
            )
            db.add(section)
            await db.flush()
            await db.refresh(section)
            created_sections.append((section, sec))

        yield f"data: {json.dumps({'status': 'generating', 'message': f'Tworzę treści ({len(created_sections)} sekcji)...', 'progress': 40})}\n\n"

        # Step 3: Generate content for each section
        for idx, (section, sec_data) in enumerate(created_sections):
            progress = 40 + int(50 * (idx + 1) / len(created_sections))
            yield f"data: {json.dumps({'status': 'generating', 'message': f'AI pisze treści ({idx + 1}/{len(created_sections)})...', 'progress': progress})}\n\n"

            try:
                result = await db.execute(
                    select(BlockTemplate).where(BlockTemplate.code == section.block_code)
                )
                block = result.scalar_one_or_none()
                if block:
                    slots = await engine.generate_section_content(project, section, block)
                    section.slots_json = slots
                else:
                    section.slots_json = sec_data.get("slots", {})
            except Exception:
                section.slots_json = sec_data.get("slots", {})

        # Step 4: Update project status
        project.status = "building"
        project.current_step = 5
        await db.commit()

        yield f"data: {json.dumps({'status': 'completed', 'message': 'Strona gotowa!', 'progress': 100, 'result': {'sections': len(created_sections)}})}\n\n"

    return StreamingResponse(progress_stream(), media_type="text/event-stream")


@router.post("/{project_id}/ai/generate-content/{section_id}")
async def generate_section_content_with_instruction(
    project_id: UUID,
    section_id: UUID,
    data: GenerateInstruction | None = None,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Stage 5-6: AI regenerates content for a single section with optional instruction."""
    project = await _get_project_with_data(project_id, org.id, db)
    from app.services.creator.project_service import ProjectService

    svc = ProjectService(db)
    section = await svc.get_section_or_404(section_id, project_id, org.id)

    result = await db.execute(
        select(BlockTemplate).where(BlockTemplate.code == section.block_code)
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Block template not found"
        )

    engine = AIEngine(db)
    slots = await engine.generate_section_content(project, section, block)
    section.slots_json = slots
    await db.commit()

    return {"slots": slots}


@router.get("/{project_id}/render")
async def render_page(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Return rendered HTML + CSS for the project page."""
    project = await _get_project_with_data(project_id, org.id, db)
    renderer = PageRenderer()
    html_body, css = await renderer.render_project_html(db, project)
    return {"html": html_body, "css": css}


# Usage endpoint is registered separately under /admin prefix to avoid
# collision with /{project_id} path parameter.

usage_router = APIRouter()


@usage_router.get("/ai/usage")
async def get_ai_usage(
    days: int = 30,
    current_user: User = Depends(get_current_superuser),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """Admin: AI usage statistics."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            AIGenerationLog.action,
            func.count(AIGenerationLog.id).label("count"),
            func.sum(AIGenerationLog.tokens_in).label("tokens_in"),
            func.sum(AIGenerationLog.tokens_out).label("tokens_out"),
            func.sum(AIGenerationLog.cost_usd).label("cost_usd"),
            func.avg(AIGenerationLog.duration_ms).label("avg_duration"),
        )
        .where(AIGenerationLog.created_at >= since)
        .group_by(AIGenerationLog.action)
    )

    return {
        "period_days": days,
        "stats": [dict(r._mapping) for r in result],
    }
