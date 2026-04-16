"""
Claude API wrapper — single client for all WebCreator AI features.

Ported from Axonet: error handling, singleton, cost estimation, prompt caching.
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

# ─── Singleton client ───

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Get or create singleton Anthropic client."""
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("AI_NO_KEY")
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


# ─── Error mapping (from Axonet) ───

ERROR_MAP = {
    "AI_NO_KEY": "Klucz API Anthropic nie jest skonfigurowany. Ustaw ANTHROPIC_API_KEY w .env",
    "ANTHROPIC_CONNECTION_ERROR": "Nie udało się połączyć z AI. Sprawdź połączenie internetowe.",
    "ANTHROPIC_TIMEOUT": "Zapytanie do AI trwało zbyt długo. Spróbuj ponownie.",
    "ANTHROPIC_RATE_LIMIT": "Zbyt wiele zapytań do AI. Poczekaj chwilę i spróbuj ponownie.",
    "ANTHROPIC_AUTH_ERROR": "Problem z kluczem API. Sprawdź konfigurację.",
    "ANTHROPIC_INSUFFICIENT_CREDITS": "Brak kredytów na koncie Anthropic. Doładuj konto w panelu Anthropic.",
    "ANTHROPIC_OVERLOADED": "Serwery AI są przeciążone. Spróbuj za minutę.",
    "ANTHROPIC_API_ERROR": "Błąd API Anthropic. Spróbuj ponownie.",
}


def get_user_error(error_code: str) -> str:
    """Map error code to user-friendly Polish message."""
    for key, msg in ERROR_MAP.items():
        if key in error_code:
            return msg
    return "Wystąpił nieoczekiwany błąd AI. Spróbuj ponownie."


def _handle_api_error(e: Exception) -> RuntimeError:
    """Convert Anthropic exceptions to RuntimeError with error codes."""
    if isinstance(e, anthropic.APIConnectionError):
        logger.error(f"Anthropic connection error: {e}")
        return RuntimeError("ANTHROPIC_CONNECTION_ERROR")
    elif isinstance(e, anthropic.APITimeoutError):
        logger.error(f"Anthropic timeout: {e}")
        return RuntimeError("ANTHROPIC_TIMEOUT")
    elif isinstance(e, anthropic.RateLimitError):
        logger.warning(f"Anthropic rate limit: {e}")
        return RuntimeError("ANTHROPIC_RATE_LIMIT")
    elif isinstance(e, anthropic.AuthenticationError):
        logger.error(f"Anthropic auth error: {e}")
        return RuntimeError("ANTHROPIC_AUTH_ERROR")
    elif isinstance(e, anthropic.APIStatusError):
        error_msg = str(e).lower()
        if "credit balance" in error_msg or "insufficient" in error_msg:
            logger.error(f"Anthropic insufficient credits: {e}")
            return RuntimeError("ANTHROPIC_INSUFFICIENT_CREDITS")
        if e.status_code == 529 or "overloaded" in error_msg:
            logger.error(f"Anthropic overloaded: {e}")
            return RuntimeError("ANTHROPIC_OVERLOADED")
        logger.error(f"Anthropic API error {e.status_code}: {e}")
        return RuntimeError(f"ANTHROPIC_API_ERROR_{e.status_code}")
    else:
        logger.error(f"Unexpected AI error: {e}")
        return RuntimeError(f"AI_UNKNOWN_ERROR: {e}")


# ─── Cost estimation (from Axonet) ───

def estimate_cost(
    model: str,
    tokens_in: int,
    tokens_out: int,
    cache_read: int = 0,
    cache_creation: int = 0,
    images: int = 0,
) -> float:
    """Estimate API call cost in USD, with prompt cache pricing."""
    RATES = {
        "claude-haiku-4-5-20251001": (1.0, 5.0),
        "claude-sonnet-4-20250514": (3.0, 15.0),
        "claude-opus-4-20250514": (15.0, 75.0),
    }
    in_rate, out_rate = RATES.get(model, (3.0, 15.0))

    base_input = tokens_in - cache_read - cache_creation
    cost = (
        max(0, base_input) * in_rate
        + cache_read * in_rate * 0.1       # Cache read = 10% of input rate
        + cache_creation * in_rate * 1.25  # Cache creation = 125% of input rate
        + tokens_out * out_rate
    ) / 1_000_000

    # Images: ~1600 tokens per image
    if images:
        cost += images * 1600 * in_rate / 1_000_000

    return round(cost, 6)


class ClaudeClient:
    """Wrapper over Anthropic API — one client for the entire WebCreator."""

    def __init__(self):
        self.client = _get_client()
        self.MODELS = {
            "fast": settings.AI_MODEL_FAST,
            "smart": settings.AI_MODEL_SMART,
            "vision": settings.AI_MODEL_SMART,
        }

    # ─── STANDARD CALL ───

    async def complete(
        self,
        system: str | list[dict],
        user_message: str,
        model_tier: str = "smart",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        images: list[bytes] | None = None,
    ) -> ClaudeResponse:
        """Single Claude API call with full error handling.

        Args:
            system: system prompt (str or list[dict] with cache_control)
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

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": content}],
                temperature=temperature,
            )
        except Exception as e:
            raise _handle_api_error(e) from e

        duration_ms = int((time.monotonic() - start) * 1000)
        text = response.content[0].text if response.content else ""

        cache_read = getattr(response.usage, "cache_read_input_tokens", 0) or 0
        cache_creation = getattr(response.usage, "cache_creation_input_tokens", 0) or 0

        return ClaudeResponse(
            text=text,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            model=model,
            duration_ms=duration_ms,
            cache_read_tokens=cache_read,
            cache_creation_tokens=cache_creation,
        )

    # ─── STREAMING (SSE) ───

    async def stream(
        self,
        system: str | list[dict],
        messages: list[dict],
        model_tier: str = "smart",
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming response (Server-Sent Events).

        Args:
            system: system prompt (str or list[dict] with cache_control)
            messages: conversation history [{role, content}, ...]

        Yields:
            text fragments (tokens)
        """
        model = self.MODELS[model_tier]

        try:
            async with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise _handle_api_error(e) from e

    # ─── CHAT MULTI-TURN ───

    async def chat(
        self,
        system: str | list[dict],
        history: list[dict],
        new_message: str,
        model_tier: str = "fast",
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Chat with conversation history — streaming.

        Args:
            system: system prompt (str or list[dict] with cache_control)
            history: existing messages from AI conversation
            new_message: new user message
        """
        messages = history + [{"role": "user", "content": new_message}]
        async for chunk in self.stream(system, messages, model_tier, max_tokens):
            yield chunk

    # ─── JSON RESPONSE WITH RETRY ───

    async def complete_json(
        self,
        system: str | list[dict],
        user_message: str,
        model_tier: str = "smart",
        images: list[bytes] | None = None,
        max_retries: int = 3,
    ) -> ClaudeJsonResponse:
        """Call expecting a JSON response. Retries up to max_retries on parse failure.

        Adds JSON instruction to system prompt + parses response.
        """
        json_instruction = (
            "\n\nOdpowiedz WYŁĄCZNIE poprawnym JSON-em. "
            "Bez markdown, bez komentarzy, bez ```."
        )

        if isinstance(system, list):
            # Append to last text block
            system_with_json = list(system)
            last_block = {**system_with_json[-1]}
            last_block["text"] = last_block["text"] + json_instruction
            system_with_json[-1] = last_block
        else:
            system_with_json = system + json_instruction

        last_error = None
        for attempt in range(max_retries):
            response = await self.complete(
                system_with_json, user_message, model_tier, images=images
            )

            parsed = self._parse_json(response.text)
            if not parsed.get("_parse_error"):
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
                logger.warning(
                    f"JSON parse failed (attempt {attempt + 1}/{max_retries}), retrying..."
                )
                # Add hint about the error for next attempt
                user_message = (
                    f"{user_message}\n\n"
                    f"[UWAGA: Poprzednia odpowiedź nie była poprawnym JSON-em. "
                    f"Odpowiedz WYŁĄCZNIE poprawnym JSON-em.]"
                )

        # All retries failed — return last response with parse error
        logger.error(f"JSON parse failed after {max_retries} attempts")
        return ClaudeJsonResponse(
            data={"raw_text": last_error, "_parse_error": True},
            raw_text=last_error or "",
            tokens_in=response.tokens_in,
            tokens_out=response.tokens_out,
            model=response.model,
            duration_ms=response.duration_ms,
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Parse JSON from AI response (handles markdown fencing, comments)."""
        clean = text.strip()

        # Remove markdown code fences
        if clean.startswith("```"):
            lines = clean.split("\n")
            # Remove first line (```json or ```) and last line (```)
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            else:
                lines = [l for l in lines if not l.strip().startswith("```")]
            clean = "\n".join(lines).strip()

        # Try direct parse
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object/array in text
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = clean.find(start_char)
            end_idx = clean.rfind(end_char)
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(clean[start_idx:end_idx + 1])
                except json.JSONDecodeError:
                    continue

        logger.warning("Failed to parse JSON from AI: %s", clean[:200])
        return {"raw_text": clean, "_parse_error": True}
