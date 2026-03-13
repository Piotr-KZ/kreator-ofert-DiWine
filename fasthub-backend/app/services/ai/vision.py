"""
AI Vision Service — visual review and feedback loop.

Two modes:
1. Feedback loop (automatic) — generate → screenshot → AI reviews → fix → repeat
2. AI Preview (on demand) — screenshot → AI comments
"""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.services.ai.claude_client import ClaudeClient
from app.services.ai.logger import log_ai_call
from app.services.ai.prompts import PROMPTS
from app.services.ai.screenshot import ScreenshotService

logger = logging.getLogger(__name__)


class AIVisionService:
    """AI reviews website visually (screenshots) and gives feedback."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.claude = ClaudeClient()
        self.renderer = ScreenshotService()

    # ─── LEVEL 2: AI PREVIEW (on demand) ───

    async def visual_review(self, project: Project) -> dict:
        """User clicks 'AI Preview' → AI reviews the page and comments.

        Returns:
            {
                "overall": "...",
                "items": [{"category": "...", "status": "...", "message": "...", "suggestion": "..."}],
                "score": 8
            }
        """
        desktop_png = await self.renderer.capture(project, viewport="desktop")
        mobile_png = await self.renderer.capture(project, viewport="mobile")

        brief_summary = self._brief_summary(project)

        response = await self.claude.complete_json(
            system=PROMPTS["visual_review"],
            user_message=f"""Oglądasz stronę WWW. Obraz 1 = desktop, Obraz 2 = mobile.

Kontekst projektu: {brief_summary}

Oceń wizualnie: układ, czytelność, responsywność, kontrast, proporcje, spójność.
Bądź konkretny — wskaż problemy i jak je naprawić.""",
            model_tier="vision",
            images=[desktop_png, mobile_png],
        )

        await log_ai_call(
            self.db, project, "visual_review", response, screenshots_count=2
        )

        return response.data

    # ─── LEVEL 1: FEEDBACK LOOP (automatic) ───

    async def generate_with_feedback_loop(
        self,
        project: Project,
        html_css_generator,
        max_iterations: int = 3,
        on_progress=None,
    ) -> dict:
        """Generate page with automatic feedback loop.

        1. Generator creates HTML/CSS from blocks
        2. Playwright renders → screenshot
        3. AI reviews screenshot and identifies issues
        4. If issues → AI proposes fixes → generator fixes → goto 2
        5. If OK → return final HTML/CSS

        Args:
            html_css_generator: async callable (project, fixes) → (html, css)
            max_iterations: max loop iterations (default 3)
            on_progress: callback: async (iteration, status_message) → None

        Returns:
            {"html": "...", "css": "...", "iterations": N, "fixes_applied": [...]}
        """
        all_fixes = []
        current_fixes = []
        html = ""
        css = ""

        for iteration in range(1, max_iterations + 1):
            if on_progress:
                messages = {
                    1: "AI buduje stronę...",
                    2: "AI sprawdza i poprawia...",
                    3: "AI dopieszcza szczegóły...",
                }
                await on_progress(
                    iteration, messages.get(iteration, f"Iteracja {iteration}...")
                )

            # 1. Generate HTML/CSS (with potential fixes)
            html, css = await html_css_generator(project, current_fixes)

            # 2. Screenshot desktop + mobile
            desktop_png = await self.renderer.capture_from_html(
                html, css, viewport="desktop"
            )
            mobile_png = await self.renderer.capture_from_html(
                html, css, viewport="mobile"
            )

            # 3. AI reviews
            review = await self.claude.complete_json(
                system=PROMPTS["visual_fix_review"],
                user_message=f"""Iteracja {iteration}/{max_iterations}.
Obraz 1 = desktop, Obraz 2 = mobile.

Poprzednie poprawki: {json.dumps(all_fixes, ensure_ascii=False) if all_fixes else 'brak (pierwsza generacja)'}

Czy widzisz problemy wizualne? Jeśli tak — opisz DOKŁADNIE co poprawić (CSS zmiany, układ, rozmiary).
Jeśli strona wygląda dobrze — odpowiedz {{"status": "ok", "fixes": []}}""",
                model_tier="vision",
                images=[desktop_png, mobile_png],
            )

            await log_ai_call(
                self.db,
                project,
                "visual_fix_review",
                review,
                screenshots_count=2,
                iterations=iteration,
            )

            fixes = review.data.get("fixes", [])

            if not fixes or review.data.get("status") == "ok":
                logger.info(
                    "Vision loop: OK after %d iterations, %d fixes",
                    iteration,
                    len(all_fixes),
                )
                return {
                    "html": html,
                    "css": css,
                    "iterations": iteration,
                    "fixes_applied": all_fixes,
                    "final_review": review.data,
                }

            # 4. Remember fixes and continue
            all_fixes.extend(fixes)
            current_fixes = fixes
            logger.info(
                "Vision loop: iteration %d, %d new fixes", iteration, len(fixes)
            )

        # Max iterations reached — return what we have
        return {
            "html": html,
            "css": css,
            "iterations": max_iterations,
            "fixes_applied": all_fixes,
            "final_review": {"status": "max_iterations_reached"},
        }

    def _brief_summary(self, project: Project) -> str:
        """Short project summary for Vision (don't send full brief — too many tokens)."""
        brief = project.brief_json or {}
        return f"""Firma: {brief.get('company_name', '?')}
Branża: {brief.get('industry', '?')}
Cel: {brief.get('site_goal', '?')}
Wrażenie: {brief.get('desired_impressions', '?')}
Styl: {json.dumps(project.style_json or {}, ensure_ascii=False)[:200]}"""
