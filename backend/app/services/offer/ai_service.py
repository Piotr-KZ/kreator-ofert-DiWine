"""
AI service for offers — email parsing + text personalization.
Reuses ClaudeClient. GUS lookup is in gus_client.py (no AI).
"""

import logging
from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer_text import OfferTextTemplate
from app.services.ai.claude_client import ClaudeClient
from app.services.offer.ai_prompts import PARSE_EMAIL_PROMPT, PERSONALIZE_TEXT_PROMPT

logger = logging.getLogger(__name__)


class OfferAIService:
    def __init__(self):
        self.claude = ClaudeClient()

    async def parse_email(self, email_text: str) -> dict:
        """Parse client email → structured JSON."""
        user_msg = PARSE_EMAIL_PROMPT.format(email_text=email_text)
        try:
            response = await self.claude.complete_json(
                system="Jesteś asystentem ofertowania prezentów firmowych. Zwracasz JSON.",
                user_message=user_msg,
            )
            if isinstance(response.data, dict) and not response.data.get("_parse_error"):
                return response.data
            return {"error": "Nie udało się przeanalizować emaila"}
        except Exception as e:
            return {"error": f"Błąd parsowania: {e}"}

    async def personalize_text(
        self, template_text: str, company_name: str = "",
        contact_person: str = "", contact_role: str = "",
        occasion_name: str = "", quantity: int = 0, sets_summary: str = "",
    ) -> str:
        """Personalize template. Simple placeholders first, AI if needed."""
        # Step 1: simple replacement
        try:
            result = template_text.format(
                company_name=company_name or "Państwa firma",
                contact_person=contact_person or "Szanowni Państwo",
                contact_role=contact_role or "",
                occasion_name=occasion_name or "",
                quantity=quantity or "",
            )
            if "{" not in result:
                return result
        except (KeyError, IndexError):
            result = template_text

        # Step 2: AI for remaining placeholders
        user_msg = PERSONALIZE_TEXT_PROMPT.format(
            template_text=template_text, company_name=company_name or "",
            contact_person=contact_person or "", contact_role=contact_role or "",
            occasion_name=occasion_name or "", quantity=quantity,
            sets_summary=sets_summary or "brak",
        )
        try:
            response = await self.claude.complete_json(
                system="Jesteś copywriterem. Personalizujesz teksty. Zwracasz JSON.",
                user_message=user_msg,
            )
            if isinstance(response.data, dict) and response.data.get("personalized_text"):
                return response.data["personalized_text"]
        except Exception as e:
            logger.error("Personalization failed: %s", e)
        return result

    @staticmethod
    async def get_templates(db: AsyncSession, block_type: str, occasion_code: Optional[str] = None) -> list[dict]:
        """Get text templates for block_type, matching occasion or universal."""
        query = select(OfferTextTemplate).where(
            OfferTextTemplate.block_type == block_type,
            OfferTextTemplate.is_active == True,
        )
        if occasion_code:
            query = query.where(or_(
                OfferTextTemplate.occasion_code == occasion_code,
                OfferTextTemplate.occasion_code.is_(None),
            ))
        result = await db.execute(query.order_by(OfferTextTemplate.order, OfferTextTemplate.variant))
        return [{"id":t.id,"block_type":t.block_type,"occasion_code":t.occasion_code,
                 "variant":t.variant,"name":t.name,"template_text":t.template_text,"tone":t.tone}
                for t in result.scalars().all()]

    @staticmethod
    def build_sets_summary(sets: list, products: dict) -> str:
        lines = []
        for s in sets:
            items_str = ", ".join(products.get(i.get("product_id",""),{}).get("name","?") for i in s.get("items",[]))
            lines.append(f"- {s.get('name','?')} ({s.get('unit_price',0):.0f} zł): {items_str}")
        return "\n".join(lines) if lines else "Brak zestawów"
