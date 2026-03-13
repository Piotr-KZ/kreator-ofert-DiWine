"""
Claude API wrapper — single client for all WebCreator AI features.
"""

import base64
import json
import logging
import time
from typing import AsyncIterator

import anthropic

from app.core.config import settings
from app.services.ai.types import ClaudeJsonResponse, ClaudeResponse

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Wrapper over Anthropic API — one client for the entire WebCreator."""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        self.MODELS = {
            "fast": settings.AI_MODEL_FAST,
            "smart": settings.AI_MODEL_SMART,
            "vision": settings.AI_MODEL_SMART,
        }

    # ─── STANDARD CALL ───

    async def complete(
        self,
        system: str,
        user_message: str,
        model_tier: str = "smart",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        images: list[bytes] | None = None,
    ) -> ClaudeResponse:
        """Single Claude API call.

        Args:
            system: system prompt
            user_message: user message
            model_tier: "fast" (Haiku), "smart" (Sonnet), "vision" (Sonnet with images)
            images: list of PNG bytes (for Vision)

        Returns:
            ClaudeResponse with text, tokens_in, tokens_out, model, duration_ms
        """
        model = self.MODELS[model_tier]

        content = []
        if images:
            for img_bytes in images:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.b64encode(img_bytes).decode(),
                    },
                })
        content.append({"type": "text", "text": user_message})

        start = time.monotonic()

        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": content}],
            temperature=temperature,
        )

        duration_ms = int((time.monotonic() - start) * 1000)
        text = response.content[0].text if response.content else ""

        return ClaudeResponse(
            text=text,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            model=model,
            duration_ms=duration_ms,
        )

    # ─── STREAMING (SSE) ───

    async def stream(
        self,
        system: str,
        messages: list[dict],
        model_tier: str = "smart",
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming response (Server-Sent Events).

        Args:
            messages: conversation history [{role, content}, ...]

        Yields:
            text fragments (tokens)
        """
        model = self.MODELS[model_tier]

        async with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    # ─── CHAT MULTI-TURN ───

    async def chat(
        self,
        system: str,
        history: list[dict],
        new_message: str,
        model_tier: str = "fast",
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Chat with conversation history — streaming.

        Args:
            history: existing messages from AI conversation
            new_message: new user message
        """
        messages = history + [{"role": "user", "content": new_message}]
        async for chunk in self.stream(system, messages, model_tier, max_tokens):
            yield chunk

    # ─── JSON RESPONSE ───

    async def complete_json(
        self,
        system: str,
        user_message: str,
        model_tier: str = "smart",
        images: list[bytes] | None = None,
    ) -> ClaudeJsonResponse:
        """Call expecting a JSON response.
        Adds JSON instruction to system prompt + parses response."""

        system_with_json = (
            system
            + "\n\nOdpowiedz WYŁĄCZNIE poprawnym JSON-em. Bez markdown, bez komentarzy, bez ```."
        )

        response = await self.complete(
            system_with_json, user_message, model_tier, images=images
        )

        return ClaudeJsonResponse(
            data=self._parse_json(response.text),
            raw_text=response.text,
            tokens_in=response.tokens_in,
            tokens_out=response.tokens_out,
            model=response.model,
            duration_ms=response.duration_ms,
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Parse JSON from AI response (handles markdown fencing)."""
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            clean = "\n".join(lines)
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from AI: %s", clean[:200])
            return {"raw_text": clean, "_parse_error": True}
