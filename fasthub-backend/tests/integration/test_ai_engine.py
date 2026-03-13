"""
Tests for Brief 31: AI Engine — Claude Client, AI Engine, Vision, Logger, API endpoints.
All Claude API calls are mocked.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_conversation import AIConversation, AIGenerationLog
from app.models.block_template import BlockCategory, BlockTemplate
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.services.ai.engine import AIEngine


# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def ai_project(db_session: AsyncSession, test_organization, test_user) -> Project:
    """Create a project with brief+style data for AI tests."""
    project = Project(
        organization_id=test_organization.id,
        created_by=test_user.id,
        name="AI Test Website",
        site_type="firmowa",
        brief_json={
            "company_name": "TestCo",
            "industry": "IT",
            "site_goal": "sprzedaz",
            "target_audience": "firmy B2B",
            "usp": ["Szybkość", "Jakość"],
            "desired_impressions": {"professional": True},
            "communication_style": "ekspercki",
        },
        style_json={
            "color_primary": "#4F46E5",
            "color_secondary": "#10B981",
            "heading_font": "Inter",
            "body_font": "Inter",
        },
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project, ["materials"])
    return project


@pytest_asyncio.fixture
async def ai_category(db_session: AsyncSession) -> BlockCategory:
    cat = BlockCategory(code="HE", name="Hero", icon="layout-dashboard", order=0)
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)
    return cat


@pytest_asyncio.fixture
async def ai_block_template(db_session: AsyncSession, ai_category) -> BlockTemplate:
    tmpl = BlockTemplate(
        code="HE1",
        category_code="HE",
        name="Hero z tłem",
        description="Sekcja hero z dużym tłem",
        html_template="<section><h1>{{title}}</h1><p>{{subtitle}}</p></section>",
        slots_definition=[
            {"id": "title", "type": "text", "label": "Tytuł", "max_length": 80},
            {"id": "subtitle", "type": "text", "label": "Podtytuł", "max_length": 200},
        ],
        media_type="photo",
        layout_type="photo-top-1",
    )
    db_session.add(tmpl)
    await db_session.commit()
    await db_session.refresh(tmpl)
    return tmpl


@pytest_asyncio.fixture
async def ai_section(
    db_session: AsyncSession, ai_project, ai_block_template
) -> ProjectSection:
    section = ProjectSection(
        project_id=ai_project.id,
        block_code="HE1",
        position=0,
        variant="A",
    )
    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)
    return section


# ============================================================================
# Mock helpers
# ============================================================================


def _mock_anthropic_response(text="mock response", tokens_in=100, tokens_out=50):
    """Create a mock Anthropic API response."""
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    response.usage = MagicMock(input_tokens=tokens_in, output_tokens=tokens_out)
    return response


def _mock_anthropic_json_response(data: dict):
    """Create a mock Anthropic response that returns JSON."""
    return _mock_anthropic_response(text=json.dumps(data, ensure_ascii=False))


# ============================================================================
# 1. Claude Client tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_complete():
    """Basic call → returns text response."""
    from app.services.ai.claude_client import ClaudeClient

    mock_resp = _mock_anthropic_response(text="Hello World")

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_resp)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        client = ClaudeClient()
        result = await client.complete("system", "user msg")

    assert result.text == "Hello World"
    assert result.tokens_in == 100
    assert result.tokens_out == 50
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_complete_json():
    """JSON call → parsed dict."""
    from app.services.ai.claude_client import ClaudeClient

    data = {"items": [{"key": "test", "status": "ok"}]}
    mock_resp = _mock_anthropic_json_response(data)

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_resp)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        client = ClaudeClient()
        result = await client.complete_json("system", "user msg")

    assert result.data == data
    assert result.tokens_in == 100


@pytest.mark.asyncio
async def test_complete_json_markdown_fencing():
    """JSON wrapped in ```json fencing → parses OK."""
    from app.services.ai.claude_client import ClaudeClient

    data = {"status": "ok"}
    text = f"```json\n{json.dumps(data)}\n```"
    mock_resp = _mock_anthropic_response(text=text)

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_resp)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        client = ClaudeClient()
        result = await client.complete_json("system", "user msg")

    assert result.data == data


@pytest.mark.asyncio
async def test_stream():
    """Streaming → yields text fragments."""
    from app.services.ai.claude_client import ClaudeClient

    async def mock_text_stream():
        for chunk in ["Hello", " ", "World"]:
            yield chunk

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_stream = AsyncMock()
        mock_stream.text_stream = mock_text_stream()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=False)
        mock_client.messages.stream = MagicMock(return_value=mock_stream)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        client = ClaudeClient()
        chunks = []
        async for chunk in client.stream("system", [{"role": "user", "content": "hi"}]):
            chunks.append(chunk)

    assert "".join(chunks) == "Hello World"


# ============================================================================
# 2. AI Engine — validation tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_validate_project_ok(db_session, ai_project):
    """Consistent brief → items with status=ok."""
    data = {
        "items": [
            {"key": "goal_ok", "status": "ok", "message": "Cel spójny"},
            {"key": "style_ok", "status": "ok", "message": "Styl pasuje"},
        ],
        "summary": "Projekt spójny",
    }

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        items = await engine.validate_project(ai_project)

    assert len(items) == 2
    assert all(i["status"] == "ok" for i in items)
    assert ai_project.validation_json is not None


@pytest.mark.asyncio
async def test_validate_project_warnings(db_session, ai_project):
    """Missing elements → warnings."""
    data = {
        "items": [
            {"key": "usp_weak", "status": "warning", "message": "USP mało wyraźne", "suggestion": "Dodaj konkrety"},
        ],
        "summary": "Drobne uwagi",
    }

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        items = await engine.validate_project(ai_project)

    assert items[0]["status"] == "warning"
    assert "suggestion" in items[0]


@pytest.mark.asyncio
async def test_validate_project_errors(db_session, ai_project):
    """Contradictions → errors."""
    data = {
        "items": [
            {"key": "contradiction", "status": "error", "message": "Sprzeczność stylu"},
        ],
        "summary": "Problemy do naprawienia",
    }

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        items = await engine.validate_project(ai_project)

    assert items[0]["status"] == "error"


# ============================================================================
# 3. AI Engine — generation tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_generate_structure(db_session, ai_project, ai_block_template):
    """Brief → list of sections with block_codes."""
    data = {
        "sections": [
            {"block_code": "HE1", "variant": "A", "position": 0, "slots": {"title": "Witaj"}},
            {"block_code": "HE1", "variant": "B", "position": 1, "slots": {"title": "O nas"}},
        ]
    }

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        sections = await engine.generate_structure(ai_project)

    assert len(sections) == 2
    assert sections[0]["block_code"] == "HE1"


@pytest.mark.asyncio
async def test_generate_section_content(
    db_session, ai_project, ai_section, ai_block_template
):
    """Section + slots_def → filled slots."""
    data = {"title": "Witamy w TestCo", "subtitle": "Innowacyjne rozwiązania IT"}

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        slots = await engine.generate_section_content(
            ai_project, ai_section, ai_block_template
        )

    assert "title" in slots
    assert "subtitle" in slots


# ============================================================================
# 4. AI Engine — chat tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_chat_stream(db_session, ai_project):
    """Message → streaming response."""
    from app.models.ai_conversation import AIConversation

    conversation = AIConversation(
        project_id=ai_project.id,
        context="validation",
        messages_json=[],
    )
    db_session.add(conversation)
    await db_session.flush()

    async def mock_text_stream():
        for chunk in ["Świetne", " pytanie!"]:
            yield chunk

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_stream = AsyncMock()
        mock_stream.text_stream = mock_text_stream()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=False)
        mock_client.messages.stream = MagicMock(return_value=mock_stream)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        chunks = []
        async for chunk in engine.chat_stream(
            ai_project, "validation", "Dlaczego?", conversation
        ):
            chunks.append(chunk)

    assert "".join(chunks) == "Świetne pytanie!"


@pytest.mark.asyncio
async def test_chat_history(db_session, ai_project):
    """Conversation history saved in AIConversation."""
    conversation = AIConversation(
        project_id=ai_project.id,
        context="editing",
        messages_json=[],
    )
    db_session.add(conversation)
    await db_session.flush()

    async def mock_text_stream():
        yield "OK"

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_stream = AsyncMock()
        mock_stream.text_stream = mock_text_stream()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=False)
        mock_client.messages.stream = MagicMock(return_value=mock_stream)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        async for _ in engine.chat_stream(
            ai_project, "editing", "Zmień nagłówek", conversation
        ):
            pass

    assert len(conversation.messages_json) == 2
    assert conversation.messages_json[0]["role"] == "user"
    assert conversation.messages_json[1]["role"] == "assistant"


# ============================================================================
# 5. AI Engine — legal tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_generate_privacy_policy(db_session, ai_project):
    """Brief → HTML privacy policy."""
    html_content = "<h2>Polityka prywatności TestCo</h2><p>Administrator danych...</p>"

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_response(text=html_content)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        result = await engine.generate_legal(ai_project, "privacy_policy")

    assert "Polityka prywatności" in result
    assert "<h2>" in result


@pytest.mark.asyncio
async def test_generate_rodo_clause(db_session, ai_project):
    """Brief → RODO clause text."""
    clause = "Administratorem danych osobowych jest TestCo..."

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_response(text=clause)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        result = await engine.generate_legal(ai_project, "rodo_clause")

    assert "Administratorem" in result


# ============================================================================
# 6. AI Vision tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_screenshot_service_capture_from_html():
    """HTML → PNG bytes (mocked playwright)."""
    from app.services.ai.screenshot import ScreenshotService

    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    mock_page = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=fake_png)
    mock_page.set_content = AsyncMock()
    mock_page.close = AsyncMock()

    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)

    with patch.object(ScreenshotService, "get_browser", return_value=mock_browser):
        svc = ScreenshotService()
        result = await svc.capture_from_html("<h1>Test</h1>", "body{}", "desktop")

    assert result == fake_png
    assert len(result) > 0


@pytest.mark.asyncio
async def test_visual_review(db_session, ai_project):
    """Screenshot → AI review items."""
    from app.services.ai.vision import AIVisionService

    review_data = {
        "overall": "Strona wygląda profesjonalnie",
        "score": 8,
        "items": [
            {"category": "layout", "status": "ok", "message": "Układ spójny"},
        ],
    }

    fake_png = b"\x89PNG" + b"\x00" * 100

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic, \
         patch.object(
             AIVisionService, "__init__",
             lambda self, db: (
                 setattr(self, "db", db),
                 setattr(self, "claude", None),
                 setattr(self, "renderer", None),
             ) and None
         ):
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(review_data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        vision = AIVisionService(db_session)
        # Re-init with real claude client after mock
        from app.services.ai.claude_client import ClaudeClient
        vision.claude = ClaudeClient()
        vision.renderer = AsyncMock()
        vision.renderer.capture = AsyncMock(return_value=fake_png)

        result = await vision.visual_review(ai_project)

    assert result["score"] == 8
    assert len(result["items"]) >= 1


@pytest.mark.asyncio
async def test_feedback_loop_converges(db_session, ai_project):
    """Feedback loop → max 3 iterations → final HTML."""
    from app.services.ai.vision import AIVisionService

    ok_review = {"status": "ok", "fixes": []}
    fake_png = b"\x89PNG" + b"\x00" * 50

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(ok_review)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        vision = AIVisionService(db_session)
        vision.renderer = AsyncMock()
        vision.renderer.capture_from_html = AsyncMock(return_value=fake_png)

        async def generator(project, fixes):
            return "<h1>Test</h1>", "body{}"

        result = await vision.generate_with_feedback_loop(
            ai_project, generator, max_iterations=3
        )

    assert result["iterations"] == 1  # Should converge on first try (OK)
    assert result["html"] == "<h1>Test</h1>"


# ============================================================================
# 7. Logging tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_ai_call_logged(db_session, ai_project):
    """After AI call → record in ai_generation_logs."""
    data = {"items": [{"key": "test", "status": "ok", "message": "OK"}], "summary": "OK"}

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        engine = AIEngine(db_session)
        await engine.validate_project(ai_project)

    result = await db_session.execute(
        select(AIGenerationLog).where(AIGenerationLog.project_id == ai_project.id)
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    assert logs[0].action == "validate"
    assert logs[0].tokens_in > 0


def test_cost_estimation():
    """estimate_cost → correct amount."""
    from app.services.ai.logger import estimate_cost

    # Haiku: 1000 in * $1/1M + 500 out * $5/1M = $0.001 + $0.0025 = $0.0035
    cost = estimate_cost("claude-haiku-4-5-20251001", 1000, 500)
    assert cost == 0.0035

    # Sonnet: 1000 in * $3/1M + 500 out * $15/1M = $0.003 + $0.0075 = $0.0105
    cost = estimate_cost("claude-sonnet-4-20250514", 1000, 500)
    assert cost == 0.0105

    # With images: +1 image * 1600 tokens * $3/1M = $0.0048
    cost = estimate_cost("claude-sonnet-4-20250514", 1000, 500, images=1)
    assert cost == 0.0153


# ============================================================================
# 8. API endpoint tests (7 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_validate_endpoint(async_client, auth_headers, db_session, ai_project):
    """POST /projects/{id}/ai/validate → 200."""
    data = {"items": [{"key": "ok", "status": "ok", "message": "Spójne"}], "summary": "OK"}

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        resp = await async_client.post(
            f"/api/v1/projects/{ai_project.id}/ai/validate",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body


@pytest.mark.asyncio
async def test_generate_structure_endpoint(
    async_client, auth_headers, db_session, ai_project, ai_block_template
):
    """POST /projects/{id}/ai/generate-structure → 200."""
    data = {"sections": [{"block_code": "HE1", "variant": "A", "position": 0, "slots": {}}]}

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        resp = await async_client.post(
            f"/api/v1/projects/{ai_project.id}/ai/generate-structure",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert "sections" in resp.json()


@pytest.mark.asyncio
async def test_chat_endpoint_sse(async_client, auth_headers, db_session, ai_project):
    """POST /projects/{id}/ai/chat → SSE stream."""

    async def mock_text_stream():
        yield "Odpowiedź"

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_stream = AsyncMock()
        mock_stream.text_stream = mock_text_stream()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=False)
        mock_client.messages.stream = MagicMock(return_value=mock_stream)
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        resp = await async_client.post(
            f"/api/v1/projects/{ai_project.id}/ai/chat",
            headers=auth_headers,
            json={"context": "validation", "message": "Pomóż mi"},
        )

    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_visual_review_endpoint(async_client, auth_headers, db_session, ai_project):
    """POST /projects/{id}/ai/visual-review → 200."""
    from app.services.ai.screenshot import ScreenshotService

    review_data = {"overall": "OK", "score": 9, "items": []}
    fake_png = b"\x89PNG" + b"\x00" * 50

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic, \
         patch.object(ScreenshotService, "capture", return_value=fake_png):
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(review_data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        resp = await async_client.post(
            f"/api/v1/projects/{ai_project.id}/ai/visual-review",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "score" in body


@pytest.mark.asyncio
async def test_legal_endpoint(async_client, auth_headers, db_session, ai_project):
    """POST /projects/{id}/ai/legal/privacy_policy → 200."""
    html = "<h2>Polityka prywatności</h2><p>Treść...</p>"

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_response(text=html)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        resp = await async_client.post(
            f"/api/v1/projects/{ai_project.id}/ai/legal/privacy_policy",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["doc_type"] == "privacy_policy"
    assert "html" in body


@pytest.mark.asyncio
async def test_check_endpoint(async_client, auth_headers, db_session, ai_project):
    """POST /projects/{id}/ai/check → 200."""
    data = {
        "checks": [{"key": "content_ok", "status": "pass", "message": "OK"}],
        "ready": True,
        "score": 9,
    }

    with patch("app.services.ai.claude_client.anthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_mock_anthropic_json_response(data)
        )
        mock_anthropic.AsyncAnthropic.return_value = mock_client

        resp = await async_client.post(
            f"/api/v1/projects/{ai_project.id}/ai/check",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "checks" in body


@pytest.mark.asyncio
async def test_usage_endpoint(async_client, admin_headers, db_session, ai_project):
    """GET /projects/ai/usage → stats (admin only)."""
    # Create a log entry first
    log = AIGenerationLog(
        project_id=ai_project.id,
        organization_id=ai_project.organization_id,
        action="validate",
        model="claude-sonnet-4-20250514",
        tokens_in=100,
        tokens_out=50,
        cost_usd=0.001,
        duration_ms=500,
    )
    db_session.add(log)
    await db_session.flush()

    resp = await async_client.get(
        "/api/v1/admin/ai/usage",
        headers=admin_headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "period_days" in body
    assert "stats" in body


# ============================================================================
# 9. Authorization test (1 test)
# ============================================================================


@pytest.mark.asyncio
async def test_ai_org_isolation(async_client, db_session, test_organization, test_user):
    """Cannot validate another org's project."""
    from app.core.security import create_access_token

    # Create project for a different org
    from app.models.organization import Organization

    other_org = Organization(name="Other Org", slug="other-org")
    db_session.add(other_org)
    await db_session.flush()
    await db_session.refresh(other_org)

    other_project = Project(
        organization_id=other_org.id,
        created_by=test_user.id,
        name="Other Project",
    )
    db_session.add(other_project)
    await db_session.flush()
    await db_session.refresh(other_project)

    # Use test_user headers (belongs to test_organization, NOT other_org)
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-Id": str(test_organization.id),
    }

    resp = await async_client.post(
        f"/api/v1/projects/{other_project.id}/ai/validate",
        headers=headers,
    )

    # Should return 404 because project is scoped to test_organization
    assert resp.status_code == 404
