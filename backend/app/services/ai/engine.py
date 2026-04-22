"""
AI Engine — main AI facade for Lab Creator.
Structure generation, visual concept, content generation, chat.
"""

import json
import logging
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockTemplate
from app.models.project import Project
from app.services.ai.claude_client import ClaudeClient
from app.services.ai.prompts import (
    ANALYZE_WEBSITE_PROMPT,
    CHAT_SYSTEM_PROMPT,
    CONTENT_PROMPT,
    REGENERATE_SECTION_PROMPT,
    STRUCTURE_PROMPT,
    VALIDATION_PROMPT,
    VISUAL_CONCEPT_PROMPT,
)
from app.services.ai.context import ProjectContext
from app.services.creator.site_structure import get_structure_config

logger = logging.getLogger(__name__)


class AIEngine:
    """Main AI service for Lab Creator."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.claude = ClaudeClient()

    # ─── WEBSITE ANALYSIS ───

    async def analyze_website(self, url: str) -> dict:
        """Use AI with web_search to analyze a website and extract brief data."""
        user_msg = ANALYZE_WEBSITE_PROMPT.format(website_url=url)

        # Use web_search tool for real internet access
        try:
            response = await self.claude.complete_with_web_search(
                system="Jestes analitykiem stron www. Zwracasz JSON.",
                user_message=user_msg,
            )
            parsed = ClaudeClient._parse_json(response.text)
            if isinstance(parsed, dict) and not parsed.get("_parse_error"):
                return parsed
            return {"error": "Nie udało się przeanalizować strony", "summary": response.text[:200]}
        except Exception as e:
            logger.error("Website analysis failed for %s: %s", url, e)
            return {"error": f"Błąd analizy: {e}"}

    # ─── VALIDATION ───

    async def validate_brief(self, project: Project) -> list[dict]:
        """Validate brief and return feedback items."""
        brief = project.brief_json or {}
        config = get_structure_config(project.site_type or "company")

        # Build website context if available
        website_context = ""
        website = brief.get("website", "")
        if website:
            website_context = f"Strona www firmy: {website}\nUwzglednij informacje ktore znasz o tej firmie przy tworzeniu sugestii."

        user_msg = VALIDATION_PROMPT.format(
            site_type_label=config["label"],
            description=brief.get("description", ""),
            target_audience=brief.get("target_audience", ""),
            usp=brief.get("usp", ""),
            tone=brief.get("tone", "profesjonalny"),
            website_context=website_context,
        )

        response = await self.claude.complete_json(
            system="Jestes konsultantem marketingowym. Zwracasz JSON.",
            user_message=user_msg,
        )

        if isinstance(response.data, dict) and response.data.get("_parse_error"):
            logger.error("Validation failed: %s", response.raw_text[:200])
            return [{"type": "ok", "message": "Walidacja niedostepna — kontynuuj"}]

        return response.data if isinstance(response.data, list) else []

    # ─── STRUCTURE GENERATION ───

    async def generate_structure(self, project: Project) -> list[dict]:
        """Generate page structure based on brief."""
        brief = project.brief_json or {}
        config = get_structure_config(project.site_type or "company")
        blocks_summary = await self._get_blocks_summary(config)

        required = ", ".join(config["required"]) if config["required"] else "brak"
        forbidden = ", ".join(config["forbidden"]) if config["forbidden"] else "brak"

        user_msg = STRUCTURE_PROMPT.format(
            description=brief.get("description", ""),
            target=brief.get("target_audience", ""),
            usp=brief.get("usp", ""),
            tone=brief.get("tone", "profesjonalny"),
            site_type_label=config["label"],
            max_sections=config["max_sections"],
            required_sections=required,
            forbidden_sections=forbidden,
            available_blocks_list=blocks_summary,
        )

        response = await self.claude.complete_json(
            system="Jestes architektem stron www. Zwracasz JSON.",
            user_message=user_msg,
        )

        if isinstance(response.data, dict) and response.data.get("_parse_error"):
            logger.error("Structure generation failed: %s", response.raw_text[:200])
            return []

        sections = response.data if isinstance(response.data, list) else response.data.get("sections", [])
        return sections

    # ─── VISUAL CONCEPT ───

    async def generate_visual_concept(self, project: Project) -> dict:
        """Generate visual concept with cumulative context (knows content)."""
        brief = project.brief_json or {}
        style = project.style_json or {}
        ctx = ProjectContext(project)

        sections_data = []
        for s in sorted(project.sections, key=lambda x: x.position):
            sections_data.append({
                "block_code": s.block_code,
                "position": s.position,
            })

        # Build visual concept prompt with content awareness
        visual_context = ctx.for_visual()
        user_msg = visual_context + "\n" + VISUAL_CONCEPT_PROMPT.format(
            description=brief.get("description", ""),
            target=brief.get("target_audience", ""),
            tone=brief.get("tone", "profesjonalny"),
            primary_color=style.get("primary_color", "#4F46E5"),
            secondary_color=style.get("secondary_color", "#F59E0B"),
            sections_json=json.dumps(sections_data, ensure_ascii=False, indent=2),
        )

        response = await self.claude.complete_json(
            system="Jestes art directorem stron www. Zwracasz JSON.",
            user_message=user_msg,
        )

        if isinstance(response.data, dict) and response.data.get("_parse_error"):
            logger.error("Visual concept generation failed: %s", response.raw_text[:200])
            return {}

        return response.data

    # ─── CONTENT GENERATION ───

    async def generate_content(self, project: Project, section) -> dict:
        """Generate content for a single section with cumulative context."""
        brief = project.brief_json or {}
        ctx = ProjectContext(project)

        # Get block template
        result = await self.db.execute(
            select(BlockTemplate).where(BlockTemplate.code == section.block_code)
        )
        block = result.scalar_one_or_none()
        if not block:
            return {}

        slots_def = block.slots_definition or []
        slots_text = json.dumps(slots_def, ensure_ascii=False, indent=2)

        # Build content prompt with cumulative context
        content_context = ctx.for_content(section)
        user_msg = content_context + "\n" + CONTENT_PROMPT.format(
            description=brief.get("description", ""),
            target=brief.get("target_audience", ""),
            usp=brief.get("usp", ""),
            tone=brief.get("tone", "profesjonalny"),
            block_code=section.block_code,
            block_name=block.name or section.block_code,
            slots_definition=slots_text,
        )

        response = await self.claude.complete_json(
            system="Jestes copywriterem stron www. Zwracasz JSON z tresciami.",
            user_message=user_msg,
        )

        if isinstance(response.data, dict) and response.data.get("_parse_error"):
            logger.error("Content generation failed for %s: %s", section.block_code, response.raw_text[:200])
            return {}

        return response.data

    async def regenerate_section(self, project: Project, section, instruction: str = "") -> dict:
        """Regenerate content for a section with optional instruction."""
        brief = project.brief_json or {}

        result = await self.db.execute(
            select(BlockTemplate).where(BlockTemplate.code == section.block_code)
        )
        block = result.scalar_one_or_none()
        if not block:
            return {}

        slots_def = block.slots_definition or []

        if instruction:
            user_msg = REGENERATE_SECTION_PROMPT.format(
                description=brief.get("description", ""),
                target=brief.get("target_audience", ""),
                usp=brief.get("usp", ""),
                tone=brief.get("tone", "profesjonalny"),
                block_code=section.block_code,
                block_name=block.name or section.block_code,
                current_content=json.dumps(section.slots_json or {}, ensure_ascii=False, indent=2),
                slots_definition=json.dumps(slots_def, ensure_ascii=False, indent=2),
                instruction=instruction,
            )
        else:
            return await self.generate_content(project, section)

        response = await self.claude.complete_json(
            system="Jestes copywriterem stron www. Zwracasz JSON z tresciami.",
            user_message=user_msg,
        )

        if isinstance(response.data, dict) and response.data.get("_parse_error"):
            return section.slots_json or {}

        return response.data

    # ─── CHAT ───

    STEP_LABELS = {
        1: "1. Brief + Styl",
        2: "2. Walidacja AI",
        3: "3. Struktura",
        4: "4. Treści",
        5: "5. Kreacja wizualna",
    }

    async def chat_stream(self, project: Project, message: str, frontend_context: dict | None = None, current_step: int | None = None) -> AsyncIterator[str]:
        """Chat with streaming about the project."""
        # Use frontend context if provided (more up-to-date than DB)
        fc = frontend_context or {}
        brief = fc.get("brief") or project.brief_json or {}
        style = fc.get("style") or project.style_json or {}
        step_num = current_step or project.current_step or 1
        step_label = self.STEP_LABELS.get(step_num, f"{step_num}. (nieznany)")

        sections_info = []
        for s in sorted(project.sections, key=lambda x: x.position):
            info = f"  - {s.block_code} (poz. {s.position})"
            if s.slots_json:
                first_text = next((v for v in s.slots_json.values() if isinstance(v, str) and len(v) > 5 and not v.startswith("/") and v != "#"), None)
                if first_text:
                    info += f" — {first_text[:60]}"
            sections_info.append(info)

        vc_status = "wygenerowany" if project.visual_concept_json else "brak"

        context = (
            f"Nazwa: {project.name}\n"
            f"Typ: {project.site_type}\n"
            f"Opis: {brief.get('description', '')}\n"
            f"Klienci: {brief.get('target_audience', '')}\n"
            f"USP: {brief.get('usp', '')}\n"
            f"Ton: {brief.get('tone', 'profesjonalny')}\n"
            f"Kolory: {style.get('primary_color', '#4F46E5')} / {style.get('secondary_color', '#F59E0B')}\n"
            f"Visual concept: {vc_status}\n"
            f"Sekcje ({len(project.sections)}):\n" + "\n".join(sections_info)
        )

        system = CHAT_SYSTEM_PROMPT.format(project_context=context, current_step_label=step_label)
        messages = [{"role": "user", "content": message}]

        async for chunk in self.claude.stream_with_web_search(system, messages):
            yield chunk

    # ─── HELPERS ───

    async def _get_blocks_summary(self, config: dict) -> str:
        """Get available blocks list for structure prompt."""
        result = await self.db.execute(
            select(BlockTemplate).where(BlockTemplate.is_active == True)
        )
        blocks = result.scalars().all()

        allowed = set(config.get("allowed_categories", []))
        forbidden = set(config.get("forbidden", []))

        lines = []
        for b in blocks:
            cat = b.category_code
            if forbidden and cat in forbidden:
                continue
            if allowed and cat not in allowed:
                continue
            lines.append(f"- {b.code}: {b.name} ({b.description or ''})")

        return "\n".join(lines) if lines else "Brak dostepnych blokow"
