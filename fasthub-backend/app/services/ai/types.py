"""
Response dataclasses for Claude API calls.
"""

from dataclasses import dataclass, field


@dataclass
class ClaudeResponse:
    text: str
    tokens_in: int
    tokens_out: int
    model: str
    duration_ms: int
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0


@dataclass
class ClaudeJsonResponse:
    data: dict
    raw_text: str
    tokens_in: int
    tokens_out: int
    model: str
    duration_ms: int
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
