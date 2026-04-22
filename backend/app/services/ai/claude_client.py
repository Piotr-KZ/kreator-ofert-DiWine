"""
Claude API wrapper — simplified for Lab Creator (single model).
"""

import json
import logging
import time
from typing import AsyncIterator

import anthropic

from app.core.config import settings
from app.services.ai.types import ClaudeJsonResponse, ClaudeResponse

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY nie ustawiony w .env")
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def _handle_api_error(e: Exception) -> RuntimeError:
    if isinstance(e, anthropic.APIConnectionError):
        return RuntimeError("Nie udalo sie polaczyc z AI. Sprawdz internet.")
    elif isinstance(e, anthropic.RateLimitError):
        return RuntimeError("Zbyt wiele zapytan do AI. Poczekaj chwile.")
    elif isinstance(e, anthropic.AuthenticationError):
        return RuntimeError("Problem z kluczem API Anthropic.")
    elif isinstance(e, anthropic.APIStatusError):
        return RuntimeError(f"Blad API Anthropic: {e.status_code}")
    return RuntimeError(f"Nieoczekiwany blad AI: {e}")


class ClaudeClient:
    """Single-model Claude wrapper for Lab Creator."""

    def __init__(self):
        self.client = _get_client()
        self.model = settings.AI_MODEL

    async def complete(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ClaudeResponse:
        start = time.monotonic()
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
            )
        except Exception as e:
            raise _handle_api_error(e) from e

        duration_ms = int((time.monotonic() - start) * 1000)
        text = response.content[0].text if response.content else ""

        return ClaudeResponse(
            text=text,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            model=self.model,
            duration_ms=duration_ms,
        )

    async def complete_with_web_search(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4096,
    ) -> ClaudeResponse:
        """Complete with web_search tool — AI can browse the internet."""
        start = time.monotonic()
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
                tools=[{"type": "web_search_20250305"}],
            )
        except Exception as e:
            raise _handle_api_error(e) from e

        duration_ms = int((time.monotonic() - start) * 1000)
        # Extract text from response blocks (skip tool_use/tool_result blocks)
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
        text = "\n".join(text_parts)

        return ClaudeResponse(
            text=text,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            model=self.model,
            duration_ms=duration_ms,
        )

    async def complete_json(
        self,
        system: str,
        user_message: str,
        max_retries: int = 3,
    ) -> ClaudeJsonResponse:
        system_json = system + "\n\nOdpowiedz WYLACZNIE poprawnym JSON-em. Bez markdown, bez komentarzy, bez ```."

        last_error = None
        response = None
        for attempt in range(max_retries):
            response = await self.complete(system_json, user_message)
            parsed = self._parse_json(response.text)
            # Lists are valid JSON, dicts with _parse_error are not
            is_error = isinstance(parsed, dict) and parsed.get("_parse_error")
            if not is_error:
                return ClaudeJsonResponse(
                    data=parsed,
                    raw_text=response.text,
                    tokens_in=response.tokens_in,
                    tokens_out=response.tokens_out,
                    model=response.model,
                    duration_ms=response.duration_ms,
                )
            last_error = response.text
            if attempt < max_retries - 1:
                user_message += "\n\n[UWAGA: Poprzednia odpowiedz nie byla poprawnym JSON-em. Odpowiedz WYLACZNIE JSON-em.]"

        return ClaudeJsonResponse(
            data={"raw_text": last_error, "_parse_error": True},
            raw_text=last_error or "",
            tokens_in=response.tokens_in if response else 0,
            tokens_out=response.tokens_out if response else 0,
            model=self.model,
            duration_ms=response.duration_ms if response else 0,
        )

    async def stream(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise _handle_api_error(e) from e

    async def stream_with_web_search(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream with web_search tool — AI can browse the internet."""
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=[{"type": "web_search_20250305"}],
            ) as stream:
                async for event in stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            yield event.delta.text
        except Exception as e:
            raise _handle_api_error(e) from e

    @staticmethod
    def _parse_json(text: str) -> dict | list:
        """Parse JSON from AI response. Returns dict or list."""
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            else:
                lines = [l for l in lines if not l.strip().startswith("```")]
            clean = "\n".join(lines).strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = clean.find(start_char)
            end_idx = clean.rfind(end_char)
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(clean[start_idx:end_idx + 1])
                except json.JSONDecodeError:
                    continue

        return {"raw_text": clean, "_parse_error": True}
