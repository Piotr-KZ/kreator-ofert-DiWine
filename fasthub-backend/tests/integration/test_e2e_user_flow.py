"""
End-to-end happy path test — Register → Brief → Materials → Style → AI Validate
→ AI Generate (SSE) → Edit Section → Add Section → Reorder → Config → Readiness
→ Publish → Verify DB → Export ZIP.

Plus 2 edge-case tests.
"""

import io
import json
import zipfile

import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.models.member import Member
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.models.published_site import PublishedSite


# ─── helpers ───

async def register_and_get_headers(client, db: AsyncSession, email: str, password: str):
    """Register, login, and return auth headers with X-Organization-Id."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "E2E Tester",
            "organization_name": "E2E Org",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    tokens = login_resp.json()

    # Resolve org_id
    from app.models.user import User
    user = (await db.execute(select(User).where(User.email == email))).scalar_one()
    member = (await db.execute(select(Member).where(Member.user_id == user.id))).scalar_one()

    return {
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-Organization-Id": str(member.organization_id),
    }


# ─── fixtures ───

@pytest_asyncio.fixture
async def seeded_categories(db_session: AsyncSession):
    from app.services.creator.block_service import seed_block_categories
    await seed_block_categories(db_session)
    return db_session


@pytest_asyncio.fixture
async def seeded_blocks(seeded_categories: AsyncSession):
    from app.services.creator.seed_blocks import seed_block_templates
    await seed_block_templates(seeded_categories)
    return seeded_categories


# ============================================================================
# E2E Happy Path
# ============================================================================

class TestE2EHappyPath:
    """Full journey: register → publish → export ZIP (1 sequential test)."""

    @pytest.mark.asyncio
    async def test_full_happy_path(self, async_client, db_session, seeded_blocks):
        ac = async_client
        db = db_session

        # ── 1. Register + Auth ──
        headers = await register_and_get_headers(ac, db, "e2e@example.com", "E2ePass123")

        me_resp = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "e2e@example.com"

        # ── 2. Create Project ──
        create_resp = await ac.post(
            "/api/v1/creator/projects",
            headers=headers,
            json={"name": "ACME Corp Website", "site_type": "firmowa"},
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project = create_resp.json()
        pid = project["id"]
        assert project["status"] == "draft"

        # ── 3. Save Brief ──
        brief_resp = await ac.put(
            f"/api/v1/projects/{pid}/brief",
            headers=headers,
            json={
                "company_name": "ACME Corp",
                "industry": "IT",
                "whatYouDo": "Software development and consulting",
                "target_audience": "Small and medium businesses",
                "competitive_advantage": "10+ years of experience",
            },
        )
        assert brief_resp.status_code == 200
        assert brief_resp.json()["brief_json"]["company_name"] == "ACME Corp"

        # ── 4. Add Material (link) ──
        mat_resp = await ac.post(
            f"/api/v1/projects/{pid}/materials/link",
            headers=headers,
            json={
                "url": "https://competitor.example.com",
                "type": "competitor",
                "description": "Main competitor website",
            },
        )
        assert mat_resp.status_code == status.HTTP_201_CREATED
        assert mat_resp.json()["type"] == "competitor"

        # ── 5. Save Style ──
        style_resp = await ac.put(
            f"/api/v1/projects/{pid}/style",
            headers=headers,
            json={
                "color_primary": "#3B82F6",
                "color_secondary": "#64748B",
                "color_accent": "#F59E0B",
                "heading_font": "Outfit",
                "body_font": "Inter",
                "border_radius": "rounded",
            },
        )
        assert style_resp.status_code == 200
        assert style_resp.json()["style_json"]["heading_font"] == "Outfit"

        # ── 6. AI Validate ──
        with patch(
            "app.services.ai.engine.AIEngine.validate_project",
            new_callable=AsyncMock,
            return_value=[{"status": "ok", "area": "brief", "message": "Brief is complete"}],
        ):
            validate_resp = await ac.post(
                f"/api/v1/projects/{pid}/ai/validate",
                headers=headers,
            )
        assert validate_resp.status_code == 200
        items = validate_resp.json()
        assert items[0]["status"] == "ok"

        # ── 7. AI Generate Site (SSE) ──
        with patch("app.services.ai.engine.AIEngine.generate_structure", new_callable=AsyncMock) as mock_struct, \
             patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock_content:
            mock_struct.return_value = [
                {"block_code": "HE1"},
                {"block_code": "FI1"},
                {"block_code": "CT1"},
            ]
            mock_content.return_value = {"title": "Generated Title", "subtitle": "Generated Subtitle"}

            sse_resp = await ac.post(
                f"/api/v1/projects/{pid}/ai/generate-site",
                headers=headers,
            )
            assert sse_resp.status_code == 200
            assert sse_resp.headers.get("content-type", "").startswith("text/event-stream")

        # ── 8. Verify sections in DB ──
        result = await db.execute(
            select(ProjectSection).where(ProjectSection.project_id == pid).order_by(ProjectSection.position)
        )
        sections = result.scalars().all()
        assert len(sections) == 3
        section_ids = [str(s.id) for s in sections]

        # ── 9. Edit Section ──
        edit_resp = await ac.patch(
            f"/api/v1/projects/{pid}/sections/{section_ids[0]}",
            headers=headers,
            json={"slots_json": {"title": "Welcome to ACME", "subtitle": "We build great software"}},
        )
        assert edit_resp.status_code == 200
        assert edit_resp.json()["slots_json"]["title"] == "Welcome to ACME"

        # ── 10. Add Section ──
        add_resp = await ac.post(
            f"/api/v1/projects/{pid}/sections",
            headers=headers,
            json={"block_code": "FI1", "slots_json": {"title": "Our Services"}},
        )
        assert add_resp.status_code == status.HTTP_201_CREATED
        new_section_id = add_resp.json()["id"]

        # ── 11. Reorder Sections ──
        reorder_resp = await ac.post(
            f"/api/v1/projects/{pid}/sections/reorder",
            headers=headers,
            json={"order": [section_ids[0], new_section_id, section_ids[1], section_ids[2]]},
        )
        assert reorder_resp.status_code == 200

        # ── 12. Save Config ──
        config_resp = await ac.put(
            f"/api/v1/projects/{pid}/config",
            headers=headers,
            json={
                "forms": {"contact_email": "kontakt@acme.com", "thank_you_message": "Dziekujemy!"},
                "social": {"facebook": "https://fb.com/acme"},
                "seo": {
                    "meta_title": "ACME Corp - Software Development",
                    "meta_description": "Professional software development services",
                    "tracking": {"ga4_id": "G-E2ETEST"},
                },
                "legal": {
                    "privacy_policy": {"source": "ai", "html": "<h1>Privacy Policy</h1><p>We respect your privacy.</p>"},
                    "cookie_banner": {"enabled": True, "style": "bar", "text": "We use cookies."},
                },
                "hosting": {
                    "domain_type": "subdomain",
                    "subdomain": "acme-e2e",
                    "deploy_method": "auto",
                },
            },
        )
        assert config_resp.status_code == 200
        assert config_resp.json()["config_json"]["hosting"]["subdomain"] == "acme-e2e"

        # ── 13. Check Readiness ──
        readiness_resp = await ac.post(
            f"/api/v1/projects/{pid}/check-readiness",
            headers=headers,
        )
        assert readiness_resp.status_code == 200
        readiness = readiness_resp.json()
        assert readiness["can_publish"] is True
        assert readiness["score"] > 0

        # ── 14. Publish ──
        publish_resp = await ac.post(
            f"/api/v1/projects/{pid}/publish",
            headers=headers,
        )
        assert publish_resp.status_code == 200
        pub_data = publish_resp.json()
        assert pub_data["status"] == "published"
        assert pub_data["subdomain"] == "acme-e2e"
        assert "webcreator.site" in pub_data["url"]
        assert pub_data["published_at"] is not None

        # ── 15. Verify DB ──
        site_result = await db.execute(
            select(PublishedSite).where(PublishedSite.project_id == pid)
        )
        site = site_result.scalar_one()
        assert site.is_active is True
        assert site.subdomain == "acme-e2e"
        assert "<!DOCTYPE html>" in site.html_snapshot
        assert "G-E2ETEST" in site.html_snapshot
        assert "cookie-banner" in site.html_snapshot

        # ── 16. Export ZIP ──
        zip_resp = await ac.get(
            f"/api/v1/projects/{pid}/export-zip",
            headers=headers,
        )
        assert zip_resp.status_code == 200
        assert zip_resp.headers["content-type"] == "application/zip"

        z = zipfile.ZipFile(io.BytesIO(zip_resp.content))
        names = z.namelist()
        assert "index.html" in names
        assert "style.css" in names

        index_html = z.read("index.html").decode()
        assert "Welcome to ACME" in index_html or "ACME" in index_html


# ============================================================================
# Edge Cases
# ============================================================================

class TestE2EEdgeCases:
    """Edge cases discovered during E2E flow."""

    @pytest.mark.asyncio
    async def test_cannot_publish_without_privacy_policy(
        self, async_client, auth_headers, db_session, seeded_blocks, test_organization, test_user,
    ):
        """Project without privacy policy → readiness can_publish=False."""
        ac = async_client
        db = db_session

        # Create project with sections but no legal config
        project = Project(
            organization_id=test_organization.id,
            created_by=test_user.id,
            name="No Privacy Policy Site",
            site_type="firmowa",
            status="building",
            current_step=7,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        # Add a section
        section = ProjectSection(
            project_id=project.id,
            block_code="HE1",
            position=0,
            variant="A",
            slots_json={"title": "Hello"},
        )
        db.add(section)
        await db.commit()

        # Set config WITHOUT privacy policy
        project.config_json = {
            "hosting": {"domain_type": "subdomain", "subdomain": "no-pp", "deploy_method": "auto"},
        }
        await db.commit()

        readiness_resp = await ac.post(
            f"/api/v1/projects/{project.id}/check-readiness",
            headers=auth_headers,
        )
        assert readiness_resp.status_code == 200
        data = readiness_resp.json()
        assert data["can_publish"] is False

        pp_check = next(c for c in data["checks"] if c["key"] == "privacy_policy")
        assert pp_check["status"] == "error"

    @pytest.mark.asyncio
    async def test_ai_validation_error_handling(
        self, async_client, auth_headers, db_session, test_organization, test_user,
    ):
        """AI validation failure → error response."""
        ac = async_client
        db = db_session

        project = Project(
            organization_id=test_organization.id,
            created_by=test_user.id,
            name="AI Error Test",
            site_type="firmowa",
            status="draft",
            current_step=3,
            brief_json={"company_name": "Test"},
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        with patch(
            "app.services.ai.engine.AIEngine.validate_project",
            new_callable=AsyncMock,
            side_effect=Exception("Anthropic API down"),
        ):
            resp = await ac.post(
                f"/api/v1/projects/{project.id}/ai/validate",
                headers=auth_headers,
            )
        assert resp.status_code == 500
