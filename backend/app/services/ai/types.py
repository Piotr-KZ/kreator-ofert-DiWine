"""
Response dataclasses for Claude API calls.
"""

from dataclasses import dataclass


@dataclass
class ClaudeResponse:
    text: str
    tokens_in: int
    tokens_out: int
    model: str
    duration_ms: int


@dataclass
class ClaudeJsonResponse:
    data: dict
    raw_text: str
    tokens_in: int
    tokens_out: int
    model: str
    duration_ms: int
