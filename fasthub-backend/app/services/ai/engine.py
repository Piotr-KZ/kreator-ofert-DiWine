"""
AI Engine — main AI facade for WebCreator.
Orchestrates Claude API calls for validation, generation, chat, legal docs, and readiness checks.

Enhanced with: prompt caching, model selector, better error handling (from Axonet).
"""

import json
import logging
from datetime import datetime
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_conversation import AIConversation
from app.models.block_template import BlockTemplate
from app.models.project import Project
from app.services.ai.claude_client import ClaudeClient
from app.services.ai.logger import log_ai_call
from app.services.ai.model_selector import get_model_tier
from app.services.ai.prompts import PROMPTS, build_cached_prompt, build_chat_prompt

logger = logging.getLogger(__name__)


class AIEngine:
    """Main AI service for WebCreator — facade over ClaudeClient."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.claude = ClaudeClient()

    # ═══════════════════════════════════════
    # ETAP 4: WALIDACJA SPÓJNOŚCI
    # ═══════════════════════════════════════

    async def validate_project(self, project: Project) -> list[dict]:
        """AI analyzes brief + materials + style and checks consistency.

        Returns list of validation items with status ok/warning/error.
        """
        from app.services.creator.site_type_config import get_prompt_hint

        context = self._build_project_context(project)
        hint = get_prompt_hint(project.site_type, "validate_consistency")
        user_msg = f"Przeanalizuj ten projekt:\n\n{context}"
        if hint:
            user_msg += f"\n\nWskazówki dla tego typu strony:\n{hint}"

        system = build_cached_prompt("validate_consistency")

        response = await self.claude.complete_json(
            system=system,
            user_message=user_msg,
            model_tier=get_model_tier("validate_consistency"),
        )

        await log_ai_call(self.db, project, "validate", response)

        items = response.data.get("items", [])
        project.validation_json = {
            "items": items,
            "validated_at": datetime.utcnow().isoformat(),
        }

        return items

    # ═══════════════════════════════════════
    # ETAP 5: GENEROWANIE STRUKTURY
    # ═══════════════════════════════════════

    async def generate_structure(self, project: Project) -> list[dict]:
        """AI generates page structure based on brief.

        Returns list of sections with block_codes and slot data.
        """
        from app.services.creator.site_type_config import get_site_type_config

        context = self._build_project_context(project)
        available_blocks = await self._get_available_blocks_summary()
        type_config = get_site_type_config(project.site_type)

        hint = type_config.prompt_hints.get("generate_structure", "")
        recommended = ", ".join(type_config.recommended_blocks)

        user_msg = (
            f"Kontekst projektu:\n{context}\n\n"
            f"Dostępne klocki:\n{available_blocks}\n\n"
            f"Rekomendowane kategorie (w tej kolejności): {recommended}\n"
            f"Min sekcji: {type_config.min_sections}, Max sekcji: {type_config.max_sections}"
        )
        if hint:
            user_msg += f"\n\nWskazówki dla tego typu strony:\n{hint}"

        system = build_cached_prompt("generate_structure")

        response = await self.claude.complete_json(
            system=system,
            user_message=user_msg,
            model_tier=get_model_tier("generate_structure"),
        )

        await log_ai_call(self.db, project, "generate_structure", response)

        return response.data.get("sections", [])

    # ═══════════════════════════════════════
    # ETAP 5-6: GENEROWANIE TREŚCI SEKCJI
    # ═══════════════════════════════════════

    async def generate_section_content(
        self, project: Project, section, block_template
    ) -> dict:
        """AI fills section slots with content."""
        from app.services.creator.site_type_config import get_prompt_hint

        context = self._build_project_context(project)
        slots_schema = json.dumps(
            block_template.slots_definition, ensure_ascii=False
        )
        hint = get_prompt_hint(project.site_type, "generate_section_content")

        system = build_cached_prompt("generate_section_content")

        user_msg = (
            f"Kontekst projektu:\n{context}\n\n"
            f"Sekcja: {block_template.name} (kod: {section.block_code}, wariant: {section.variant})\n"
            f"Opis klocka: {block_template.description}\n\n"
            f"Wypełnij te sloty:\n{slots_schema}"
        )
        if hint:
            user_msg += f"\n\nWskazówki dla tego typu strony:\n{hint}"

        response = await self.claude.complete_json(
            system=system,
            user_message=user_msg,
            model_tier=get_model_tier("generate_section_content"),
        )

        await log_ai_call(self.db, project, "generate_content", response)

        return response.data

    # ═══════════════════════════════════════
    # CHAT Z AI (streaming)
    # ═══════════════════════════════════════

    async def chat_stream(
        self,
        project: Project,
        context_type: str,
        message: str,
        conversation: AIConversation,
    ) -> AsyncIterator[str]:
        """Chat with AI in project context — streaming."""
        project_context = self._build_project_context(project)
        system = build_chat_prompt(context_type, project_context)

        history = conversation.messages_json or []

        full_response = []
        async for chunk in self.claude.chat(
            system, history, message,
            model_tier=get_model_tier(f"chat_{context_type}"),
        ):
            full_response.append(chunk)
            yield chunk

        # Save in conversation history
        assistant_text = "".join(full_response)
        conversation.messages_json = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": assistant_text},
        ]
        # Approximate token tracking
        conversation.total_tokens_in += len(message) // 4
        conversation.total_tokens_out += len(assistant_text) // 4

    # ═══════════════════════════════════════
    # CHAT KREATOR (widget na wszystkich krokach)
    # ═══════════════════════════════════════

    async def chat_creator_stream(
        self,
        project: Project,
        current_step: int,
        message: str,
        conversation: AIConversation,
    ) -> AsyncIterator[str]:
        """Chat with AI in full project context - floating widget on all steps."""
        project_context = self._build_full_project_state(project)

        step_names = {
            1: "Brief firmowy", 2: "Materialy", 3: "Styl wizualny",
            4: "Walidacja AI", 5: "Struktura", 6: "Podglad",
            7: "Konfiguracja", 8: "Sprawdzenie gotowosci", 9: "Publikacja",
        }
        step_label = step_names.get(current_step, f"Krok {current_step}")

        raw = PROMPTS.get("chat_creator", "")
        prompt_text = raw.replace("{current_step}", f"{current_step} ({step_label})")
        parts = prompt_text.split("{project_context}")
        static_part = parts[0].rstrip()
        suffix = parts[1].lstrip() if len(parts) > 1 else ""

        system = [
            {
                "type": "text",
                "text": static_part,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": project_context + ("\n" + suffix if suffix else ""),
            },
        ]

        history = conversation.messages_json or []

        full_response = []
        async for chunk in self.claude.chat(
            system, history, message,
            model_tier=get_model_tier("chat_creator"),
        ):
            full_response.append(chunk)
            yield chunk

        assistant_text = "".join(full_response)
        conversation.messages_json = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": assistant_text},
        ]
        conversation.total_tokens_in += len(message) // 4
        conversation.total_tokens_out += len(assistant_text) // 4

    # ═══════════════════════════════════════
    # ETAP 7: GENEROWANIE DOKUMENTOW PRAWNYCH
    # ═══════════════════════════════════════

    async def generate_legal(self, project: Project, doc_type: str) -> str:
        """AI generates a legal document tailored to the company."""
        context = self._build_project_context(project)
        prompt_key = f"generate_{doc_type}"

        system = build_cached_prompt(prompt_key)

        response = await self.claude.complete(
            system=system,
            user_message=f"Dane firmy:\n{context}",
            model_tier=get_model_tier(prompt_key),
        )

        await log_ai_call(self.db, project, f"generate_legal_{doc_type}", response)

        return response.text

    # ═══════════════════════════════════════
    # ETAP 8: SPRAWDZENIE GOTOWOŚCI
    # ═══════════════════════════════════════

    async def check_readiness(self, project: Project) -> list[dict]:
        """AI checks if the site is ready for publishing."""
        context = self._build_full_project_state(project)

        system = build_cached_prompt("check_readiness")

        response = await self.claude.complete_json(
            system=system,
            user_message=f"Sprawdź gotowość:\n{context}",
            model_tier=get_model_tier("check_readiness"),
        )

        await log_ai_call(self.db, project, "check_readiness", response)

        return response.data.get("checks", [])

    # ═══════════════════════════════════════
    # ETAP 7: SUGESTIE SEO
    # ═══════════════════════════════════════

    async def suggest_seo(self, project: Project) -> dict:
        """AI suggests SEO metadata based on project brief and content."""
        context = self._build_full_project_state(project)

        system = build_cached_prompt("suggest_seo")

        response = await self.claude.complete_json(
            system=system,
            user_message=f"Zaproponuj SEO dla tego projektu:\n\n{context}",
            model_tier=get_model_tier("suggest_seo"),
        )

        await log_ai_call(self.db, project, "suggest_seo", response)

        return response.data

    # ═══════════════════════════════════════
    # AI ALT TEXTS (WCAG)
    # ═══════════════════════════════════════

    async def suggest_alt_texts(self, project: Project) -> dict:
        """AI generates alt text suggestions for images missing alt descriptions."""
        context = self._build_full_project_state(project)

        # Collect images without alt
        missing = []
        for s in (project.sections or []):
            if s.is_visible and s.slots_json:
                for key, val in s.slots_json.items():
                    if "image" in key.lower() and isinstance(val, str) and val:
                        alt_key = f"{key}_alt"
                        if not s.slots_json.get(alt_key):
                            missing.append(
                                f"- Sekcja {s.block_code} (poz. {s.position}), slot '{key}', "
                                f"tytuł sekcji: '{s.slots_json.get('title', 'brak')}'"
                            )

        if not missing:
            return {"alt_texts": {}}

        system = build_cached_prompt("suggest_alt_texts")
        user_msg = (
            f"Kontekst projektu:\n{context}\n\n"
            f"Obrazy bez alt text:\n" + "\n".join(missing)
        )

        response = await self.claude.complete_json(
            system=system,
            user_message=user_msg,
            model_tier=get_model_tier("suggest_alt_texts"),
        )

        await log_ai_call(self.db, project, "suggest_alt_texts", response)
        return response.data

    # ═══════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════

    def _build_project_context(self, project: Project) -> str:
        """Build project context for AI (brief + style + materials)."""
        from app.services.creator.site_type_config import get_site_type_config

        parts = []

        # Site type info (Brief 42)
        type_config = get_site_type_config(project.site_type)
        parts.append(f"TYP STRONY: {type_config.label} ({project.site_type or 'firmowa'})")

        if project.brief_json:
            parts.append(
                f"BRIEF:\n{json.dumps(project.brief_json, ensure_ascii=False, indent=2)}"
            )

        if project.style_json:
            parts.append(
                f"STYL WIZUALNY:\n{json.dumps(project.style_json, ensure_ascii=False, indent=2)}"
            )

        if project.materials:
            mat_summary = []
            for m in project.materials:
                if m.type == "link":
                    mat_summary.append(
                        f"- Link: {m.external_url} ({m.description or 'brak opisu'})"
                    )
                elif m.ai_extracted_text:
                    mat_summary.append(
                        f"- Dokument '{m.original_filename}': {m.ai_extracted_text[:500]}"
                    )
                else:
                    mat_summary.append(
                        f"- Plik: {m.original_filename} ({m.type})"
                    )
            parts.append("MATERIAŁY:\n" + "\n".join(mat_summary))

        if project.validation_json:
            parts.append(
                f"WALIDACJA AI:\n{json.dumps(project.validation_json, ensure_ascii=False, indent=2)}"
            )

        return "\n\n---\n\n".join(parts) if parts else "Brak danych projektu."

    def _build_full_project_state(self, project: Project) -> str:
        """Full project state (brief + style + sections + config) — for check_readiness."""
        context = self._build_project_context(project)

        if project.sections:
            sections_summary = []
            for s in project.sections:
                slots = s.slots_json or {}
                sections_summary.append(
                    f"  Sekcja {s.position}: {s.block_code} (wariant {s.variant}) — "
                    f"tytuł: {slots.get('title', 'brak')}"
                )
            context += "\n\n---\n\nSEKCJE STRONY:\n" + "\n".join(sections_summary)

        if project.config_json:
            context += (
                "\n\n---\n\nKONFIGURACJA:\n"
                + json.dumps(project.config_json, ensure_ascii=False, indent=2)
            )

        return context

    async def _get_available_blocks_summary(self) -> str:
        """Summary of available blocks for AI."""
        result = await self.db.execute(
            select(BlockTemplate).where(BlockTemplate.is_active == True)
        )
        blocks = result.scalars().all()
        summary = []
        for b in blocks:
            slots = [s["id"] for s in (b.slots_definition or []) if isinstance(s, dict)]
            summary.append(
                f"- {b.code} ({b.name}): sloty={slots}, media={b.media_type}"
            )
        return "\n".join(summary) if summary else "Brak klocków w bibliotece."
