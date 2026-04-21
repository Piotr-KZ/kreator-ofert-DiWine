"""
Conftest — shared fixtures for Lab Creator tests.
File-based SQLite, seeded blocks, mocked Anthropic.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.base import Base
from app.models import BlockCategory, BlockTemplate, Project, ProjectMaterial, ProjectSection

# ─── Test database (file-based SQLite per test) ───

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_lab.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest_asyncio.fixture
async def _test_engine():
    """Create and teardown test engine."""
    # Remove old DB file
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest_asyncio.fixture
async def _session_factory(_test_engine):
    """Session factory bound to test engine."""
    factory = async_sessionmaker(
        _test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield factory


@pytest_asyncio.fixture
async def db(_session_factory):
    """Fresh DB session per test (for model-level tests)."""
    async with _session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def seeded_db(_session_factory):
    """DB session with seeded categories + blocks."""
    async with _session_factory() as session:
        # Seed categories
        cats = [
            BlockCategory(code="NA", name="Nawigacja", icon="menu", order=-1),
            BlockCategory(code="HE", name="Hero", icon="layout-dashboard", order=0),
            BlockCategory(code="FI", name="O firmie", icon="building-2", order=1),
            BlockCategory(code="OF", name="Oferta", icon="shopping-bag", order=2),
            BlockCategory(code="CT", name="CTA", icon="zap", order=7),
            BlockCategory(code="KO", name="Kontakt", icon="mail", order=8),
            BlockCategory(code="FO", name="Stopka", icon="minus", order=9),
        ]
        for c in cats:
            session.add(c)

        # Seed block templates
        blocks = [
            BlockTemplate(
                code="NA1", category_code="NA", name="Nawigacja jasna",
                description="Nav bar",
                html_template='<nav><span>{{logo_text}}</span>{{#each menu_items}}<a href="{{this.url}}">{{this.label}}</a>{{/each}}</nav>',
                slots_definition=[
                    {"id": "logo_text", "type": "text", "label": "Nazwa firmy"},
                    {"id": "menu_items", "type": "list", "label": "Menu", "item_fields": [
                        {"id": "label", "type": "text"}, {"id": "url", "type": "url"}
                    ]},
                ],
                media_type="none", layout_type="text-only", size="S", is_active=True,
            ),
            BlockTemplate(
                code="HE1", category_code="HE", name="Hero z tlem",
                description="Hero section",
                html_template='<section><h1>{{heading}}</h1><p>{{subheading}}</p>{{#if cta_text}}<a href="{{cta_url}}">{{cta_text}}</a>{{/if}}</section>',
                slots_definition=[
                    {"id": "heading", "type": "text", "label": "Naglowek"},
                    {"id": "subheading", "type": "text", "label": "Podnaglowek"},
                    {"id": "cta_text", "type": "text", "label": "Przycisk CTA"},
                    {"id": "cta_url", "type": "url", "label": "Link CTA"},
                ],
                media_type="photo_wide", layout_type="photo-full-1", size="L", is_active=True,
            ),
            BlockTemplate(
                code="OF1", category_code="OF", name="Oferta 3 karty",
                description="3 cards",
                html_template='<div><h2>{{heading}}</h2>{{#each items}}<div><h3>{{this.title}}</h3><p>{{this.desc}}</p></div>{{/each}}</div>',
                slots_definition=[
                    {"id": "heading", "type": "text", "label": "Naglowek"},
                    {"id": "items", "type": "list", "label": "Karty", "item_fields": [
                        {"id": "title", "type": "text"}, {"id": "desc", "type": "text"}
                    ]},
                ],
                media_type="icons", layout_type="info-title-text-3", size="M", is_active=True,
            ),
            BlockTemplate(
                code="CT1", category_code="CT", name="CTA prosty",
                description="Call to action",
                html_template='<div><h2>{{heading}}</h2><a href="{{cta_url}}">{{cta_text}}</a></div>',
                slots_definition=[
                    {"id": "heading", "type": "text", "label": "Naglowek"},
                    {"id": "cta_text", "type": "text", "label": "Przycisk"},
                    {"id": "cta_url", "type": "url", "label": "Link"},
                ],
                media_type="none", size="S", is_active=True,
            ),
            BlockTemplate(
                code="KO1", category_code="KO", name="Kontakt prosty",
                description="Contact section",
                html_template='<div><h2>{{heading}}</h2><p>{{email}}</p><p>{{phone}}</p></div>',
                slots_definition=[
                    {"id": "heading", "type": "text"}, {"id": "email", "type": "text"}, {"id": "phone", "type": "text"}
                ],
                media_type="none", size="M", is_active=True,
            ),
            BlockTemplate(
                code="FO1", category_code="FO", name="Stopka prosta",
                description="Footer",
                html_template='<footer><p>{{copyright}}</p></footer>',
                slots_definition=[{"id": "copyright", "type": "text"}],
                media_type="none", size="S", is_active=True,
            ),
        ]
        for b in blocks:
            session.add(b)

        await session.commit()
        yield session


# ─── FastAPI test client ───

@pytest_asyncio.fixture
async def client(_session_factory, seeded_db):
    """Async HTTP test client with overridden DB dependency."""
    from app.main import app
    from app.db.session import get_db

    async def override_get_db():
        async with _session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ─── Mock Anthropic ───

MOCK_STRUCTURE_RESPONSE = [
    {"block_code": "NA1", "title": "Nawigacja"},
    {"block_code": "HE1", "title": "Hero - Innowacyjne Rozwiazania"},
    {"block_code": "OF1", "title": "Nasza Oferta"},
    {"block_code": "CT1", "title": "Zacznij Juz Dzis"},
    {"block_code": "KO1", "title": "Kontakt"},
]

MOCK_VISUAL_CONCEPT = {
    "style": "modern_minimal",
    "bg_approach": "alternating",
    "separator_type": "wave",
    "sections": [
        {"block_code": "NA1", "bg_type": "white", "bg_value": "#ffffff", "media_type": "logo", "photo_query": None, "separator_after": False},
        {"block_code": "HE1", "bg_type": "dark_photo_overlay", "bg_value": "#4F46E5CC", "media_type": "photo_wide", "photo_query": "business team professional", "separator_after": True},
        {"block_code": "OF1", "bg_type": "light_gray", "bg_value": "#f3f4f6", "media_type": "icons", "photo_query": None, "separator_after": True},
        {"block_code": "CT1", "bg_type": "brand_color", "bg_value": "#4F46E5", "media_type": "none", "photo_query": None, "separator_after": True},
        {"block_code": "KO1", "bg_type": "white", "bg_value": "#ffffff", "media_type": "none", "photo_query": None, "separator_after": False},
    ],
}

MOCK_CONTENT_NA1 = {
    "logo_text": "TestFirma",
    "menu_items": [
        {"label": "Start", "url": "#"},
        {"label": "Oferta", "url": "#oferta"},
        {"label": "Kontakt", "url": "#kontakt"},
    ],
}

MOCK_CONTENT_HE1 = {
    "heading": "Innowacyjne Rozwiazania dla Biznesu",
    "subheading": "Tworzymy oprogramowanie ktore zmienia Twoja firme",
    "cta_text": "Rozpocznij",
    "cta_url": "#kontakt",
}

MOCK_CONTENT_OF1 = {
    "heading": "Nasza Oferta",
    "items": [
        {"title": "Konsulting IT", "desc": "Doradzamy najlepsze technologie"},
        {"title": "Development", "desc": "Tworzymy aplikacje na zamowienie"},
        {"title": "Wsparcie", "desc": "Utrzymanie i rozwoj istniejacych systemow"},
    ],
}

MOCK_CONTENT_CT1 = {
    "heading": "Gotowy na zmiany?",
    "cta_text": "Skontaktuj sie",
    "cta_url": "#kontakt",
}

MOCK_CONTENT_KO1 = {
    "heading": "Skontaktuj sie z nami",
    "email": "kontakt@testfirma.pl",
    "phone": "+48 123 456 789",
}

MOCK_CONTENTS = {
    "NA1": MOCK_CONTENT_NA1,
    "HE1": MOCK_CONTENT_HE1,
    "OF1": MOCK_CONTENT_OF1,
    "CT1": MOCK_CONTENT_CT1,
    "KO1": MOCK_CONTENT_KO1,
}


def _make_mock_claude_response(data):
    """Create mock ClaudeJsonResponse."""
    import json
    from app.services.ai.types import ClaudeJsonResponse
    return ClaudeJsonResponse(
        data=data,
        raw_text=json.dumps(data),
        tokens_in=100,
        tokens_out=200,
        model="claude-sonnet-4-20250514",
        duration_ms=500,
    )


@pytest.fixture
def mock_anthropic():
    """Patch ClaudeClient to return mock data (no real API calls)."""
    with patch("app.services.ai.claude_client._get_client") as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_claude_json():
    """Patch ClaudeClient.complete_json to return mock data per context."""
    call_count = {"n": 0}

    async def mock_complete_json(self, system, user_message, max_retries=3):
        call_count["n"] += 1

        if "architektem" in system.lower():
            return _make_mock_claude_response(MOCK_STRUCTURE_RESPONSE)
        elif "art directorem" in system.lower():
            return _make_mock_claude_response(MOCK_VISUAL_CONCEPT)
        elif "copywriterem" in system.lower():
            for code in MOCK_CONTENTS:
                if code in user_message:
                    return _make_mock_claude_response(MOCK_CONTENTS[code])
            return _make_mock_claude_response(MOCK_CONTENT_HE1)
        return _make_mock_claude_response({})

    with patch("app.services.ai.claude_client.ClaudeClient.complete_json", mock_complete_json):
        yield call_count


# ─── Sample project fixture ───

@pytest_asyncio.fixture
async def sample_project(seeded_db: AsyncSession):
    """Project with brief and style, ready for AI generation."""
    from uuid import uuid4
    project = Project(
        id=str(uuid4()),
        name="TestFirma Sp. z o.o.",
        site_type="company_card",
        brief_json={
            "description": "Firma IT tworzaca oprogramowanie na zamowienie",
            "target_audience": "Male i srednie firmy szukajace digitalizacji",
            "usp": "Szybkie wdrozenia w 4 tygodnie",
            "tone": "profesjonalny",
        },
        style_json={
            "primary_color": "#4F46E5",
            "secondary_color": "#F59E0B",
        },
    )
    seeded_db.add(project)
    await seeded_db.commit()
    return project
