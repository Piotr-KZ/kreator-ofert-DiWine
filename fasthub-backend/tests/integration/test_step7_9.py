"""
Tests for Brief 35: Kreator etapy 7-9 — Config, Readiness, Publish.
33 tests total.
"""

import io
import json
import zipfile
import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock

from app.models.block_template import BlockCategory, BlockTemplate
from app.models.form_submission import FormSubmission
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.models.published_site import PublishedSite


# ============================================================================
# Fixtures
# ============================================================================

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


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_organization, test_user):
    project = Project(
        organization_id=test_organization.id,
        created_by=test_user.id,
        name="Test Brief 35",
        site_type="firmowa",
        status="building",
        current_step=7,
        brief_json={"company_name": "ACME Sp. z o.o.", "industry": "IT", "whatYouDo": "Software development"},
        style_json={
            "color_primary": "#3B82F6",
            "color_secondary": "#64748B",
            "color_accent": "#F59E0B",
            "heading_font": "Outfit",
            "body_font": "Inter",
            "border_radius": "rounded",
        },
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def project_with_sections(test_project, db_session, seeded_blocks):
    """Project with 3 sections including content."""
    s1 = ProjectSection(
        project_id=test_project.id,
        block_code="HE1",
        position=0,
        variant="A",
        slots_json={"title": "ACME Software", "subtitle": "Najlepsze rozwiązania IT", "cta_text": "Kontakt"},
    )
    s2 = ProjectSection(
        project_id=test_project.id,
        block_code="FI1",
        position=1,
        variant="A",
        slots_json={"title": "O nas", "description": "Dostarczamy innowacyjne rozwiązania."},
    )
    s3 = ProjectSection(
        project_id=test_project.id,
        block_code="CT1",
        position=2,
        variant="A",
        slots_json={"title": "Skontaktuj się", "button_text": "Wyślij"},
    )
    db_session.add_all([s1, s2, s3])
    await db_session.commit()
    await db_session.refresh(test_project, ["sections"])
    return test_project


@pytest_asyncio.fixture
async def configured_project(project_with_sections, db_session):
    """Project with full config_json set."""
    project_with_sections.config_json = {
        "forms": {
            "contact_email": "kontakt@acme.pl",
            "thank_you_message": "Dziękujemy!",
            "send_email_notification": True,
        },
        "social": {"facebook": "https://fb.com/acme", "linkedin": "https://linkedin.com/company/acme"},
        "seo": {
            "meta_title": "ACME - Najlepsze rozwiązania IT",
            "meta_description": "Dostarczamy innowacyjne rozwiązania IT dla firm",
            "og_title": "ACME Software",
            "og_description": "Innowacyjne IT",
            "tracking": {"ga4_id": "G-TEST123"},
        },
        "legal": {
            "privacy_policy": {"source": "ai", "html": "<h1>Polityka prywatności ACME</h1><p>...</p>"},
            "terms": {"source": "own", "html": "<h1>Regulamin</h1><p>...</p>"},
            "cookie_banner": {"enabled": True, "style": "bar", "text": "Używamy cookies."},
            "rodo": {"enabled": True, "text": "Wyrażam zgodę na przetwarzanie danych."},
        },
        "hosting": {
            "domain_type": "subdomain",
            "subdomain": "acme-test",
            "deploy_method": "auto",
        },
    }
    await db_session.commit()
    await db_session.refresh(project_with_sections)
    return project_with_sections


# ============================================================================
# STEP 7: Config
# ============================================================================

class TestStep7Config:
    """Step 7: Config save/get (9 tests)."""

    @pytest.mark.asyncio
    async def test_save_forms_config(self, async_client, auth_headers, test_project):
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"forms": {"contact_email": "test@example.com", "thank_you_message": "Thanks!"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config_json"]["forms"]["contact_email"] == "test@example.com"
        assert data["config_json"]["forms"]["thank_you_message"] == "Thanks!"

    @pytest.mark.asyncio
    async def test_save_social_config(self, async_client, auth_headers, test_project):
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"social": {"facebook": "https://fb.com/test", "instagram": "https://ig.com/test"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config_json"]["social"]["facebook"] == "https://fb.com/test"

    @pytest.mark.asyncio
    async def test_save_seo_config(self, async_client, auth_headers, test_project):
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"seo": {"meta_title": "Test Title", "meta_description": "Test description"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config_json"]["seo"]["meta_title"] == "Test Title"

    @pytest.mark.asyncio
    async def test_save_tracking_config(self, async_client, auth_headers, test_project):
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"seo": {"tracking": {"ga4_id": "G-12345", "fb_pixel_id": "123456"}}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config_json"]["seo"]["tracking"]["ga4_id"] == "G-12345"

    @pytest.mark.asyncio
    async def test_save_legal_config(self, async_client, auth_headers, test_project):
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"legal": {
                "privacy_policy": {"source": "own", "html": "<p>Policy</p>"},
                "cookie_banner": {"enabled": True, "style": "bar"},
            }},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config_json"]["legal"]["privacy_policy"]["source"] == "own"
        assert data["config_json"]["legal"]["cookie_banner"]["enabled"] is True

    @pytest.mark.asyncio
    async def test_save_hosting_config(self, async_client, auth_headers, test_project):
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"hosting": {"domain_type": "subdomain", "subdomain": "mysite", "deploy_method": "auto"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config_json"]["hosting"]["subdomain"] == "mysite"

    @pytest.mark.asyncio
    async def test_get_config(self, async_client, auth_headers, test_project, db_session):
        test_project.config_json = {"forms": {"contact_email": "hello@test.com"}}
        await db_session.commit()

        resp = await async_client.get(
            f"/api/v1/projects/{test_project.id}/config",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["config_json"]["forms"]["contact_email"] == "hello@test.com"

    @pytest.mark.asyncio
    async def test_config_merge_preserves_other_tabs(self, async_client, auth_headers, test_project, db_session):
        """Saving one tab doesn't erase another tab's config."""
        # Save forms first
        await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"forms": {"contact_email": "keep@this.com"}},
            headers=auth_headers,
        )
        # Save social
        resp = await async_client.put(
            f"/api/v1/projects/{test_project.id}/config",
            json={"social": {"facebook": "https://fb.com/test"}},
            headers=auth_headers,
        )
        data = resp.json()
        # Forms should still be there
        assert data["config_json"]["forms"]["contact_email"] == "keep@this.com"
        assert data["config_json"]["social"]["facebook"] == "https://fb.com/test"

    @pytest.mark.asyncio
    async def test_ai_suggest_seo(self, async_client, auth_headers, test_project):
        """AI suggest-seo endpoint works."""
        mock_response = MagicMock()
        mock_response.data = {
            "meta_title": "ACME - IT Solutions",
            "meta_description": "Best IT solutions",
            "og_title": "ACME Software",
            "og_description": "IT Solutions",
        }

        with patch("app.services.ai.engine.AIEngine.suggest_seo", new_callable=AsyncMock, return_value=mock_response.data):
            resp = await async_client.post(
                f"/api/v1/projects/{test_project.id}/ai/suggest-seo",
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert "meta_title" in resp.json()


# ============================================================================
# STEP 8: Readiness
# ============================================================================

class TestStep8Readiness:
    """Step 8: Readiness checks (6 tests)."""

    @pytest.mark.asyncio
    async def test_readiness_all_pass(self, async_client, auth_headers, configured_project):
        resp = await async_client.post(
            f"/api/v1/projects/{configured_project.id}/check-readiness",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["can_publish"] is True
        assert len(data["checks"]) == 15
        # All pass or warn (no errors since config is complete)
        errors = [c for c in data["checks"] if c["status"] == "error"]
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_readiness_missing_analytics_warns(self, async_client, auth_headers, project_with_sections, db_session):
        """No tracking IDs → analytics warn."""
        project_with_sections.config_json = {
            "seo": {"meta_title": "Test", "meta_description": "Test"},
            "legal": {"privacy_policy": {"source": "ai", "html": "<p>PP</p>"}},
        }
        await db_session.commit()

        resp = await async_client.post(
            f"/api/v1/projects/{project_with_sections.id}/check-readiness",
            headers=auth_headers,
        )
        data = resp.json()
        analytics_check = next(c for c in data["checks"] if c["key"] == "analytics")
        assert analytics_check["status"] == "warn"

    @pytest.mark.asyncio
    async def test_readiness_missing_privacy_error(self, async_client, auth_headers, project_with_sections, db_session):
        """No privacy policy → error."""
        project_with_sections.config_json = {}
        await db_session.commit()

        resp = await async_client.post(
            f"/api/v1/projects/{project_with_sections.id}/check-readiness",
            headers=auth_headers,
        )
        data = resp.json()
        pp_check = next(c for c in data["checks"] if c["key"] == "privacy_policy")
        assert pp_check["status"] == "error"
        assert data["can_publish"] is False

    @pytest.mark.asyncio
    async def test_readiness_empty_sections_warn(self, async_client, auth_headers, test_project, db_session, seeded_blocks):
        """Sections without slots_json → warn."""
        s = ProjectSection(
            project_id=test_project.id,
            block_code="HE1",
            position=0,
            variant="A",
            slots_json=None,
        )
        db_session.add(s)
        await db_session.commit()

        resp = await async_client.post(
            f"/api/v1/projects/{test_project.id}/check-readiness",
            headers=auth_headers,
        )
        data = resp.json()
        sections_check = next(c for c in data["checks"] if c["key"] == "sections_filled")
        assert sections_check["status"] == "warn"

    @pytest.mark.asyncio
    async def test_readiness_saves_check_json(self, async_client, auth_headers, configured_project, db_session):
        """Check results are saved in project.check_json."""
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/check-readiness",
            headers=auth_headers,
        )
        await db_session.refresh(configured_project)
        assert configured_project.check_json is not None
        assert "checks" in configured_project.check_json

    @pytest.mark.asyncio
    async def test_readiness_score_count(self, async_client, auth_headers, configured_project):
        resp = await async_client.post(
            f"/api/v1/projects/{configured_project.id}/check-readiness",
            headers=auth_headers,
        )
        data = resp.json()
        passed = sum(1 for c in data["checks"] if c["status"] == "pass")
        assert data["score"] == passed


# ============================================================================
# STEP 9: Publish
# ============================================================================

class TestStep9Publish:
    """Step 9: Publishing pipeline (9 tests)."""

    @pytest.mark.asyncio
    async def test_publish_creates_record(self, async_client, auth_headers, configured_project, db_session):
        resp = await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "published"
        assert data["subdomain"] == "acme-test"

        # Check DB
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == configured_project.id)
        )
        site = result.scalar_one()
        assert site.is_active is True
        assert site.subdomain == "acme-test"

    @pytest.mark.asyncio
    async def test_publish_generates_html_with_tracking(self, async_client, auth_headers, configured_project, db_session):
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == configured_project.id)
        )
        site = result.scalar_one()
        html = site.html_snapshot
        assert "<!DOCTYPE html>" in html
        assert "G-TEST123" in html  # GA4
        assert "ACME - Najlepsze rozwiązania IT" in html  # meta title

    @pytest.mark.asyncio
    async def test_publish_cookie_banner_in_html(self, async_client, auth_headers, configured_project, db_session):
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == configured_project.id)
        )
        site = result.scalar_one()
        assert "cookie-banner" in site.html_snapshot

    @pytest.mark.asyncio
    async def test_publish_sets_project_status(self, async_client, auth_headers, configured_project, db_session):
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        await db_session.refresh(configured_project)
        assert configured_project.status == "published"
        assert configured_project.published_at is not None

    @pytest.mark.asyncio
    async def test_unpublish(self, async_client, auth_headers, configured_project, db_session):
        # Publish first
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )

        # Unpublish
        resp = await async_client.post(
            f"/api/v1/projects/{configured_project.id}/unpublish",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "unpublished"

        await db_session.refresh(configured_project)
        assert configured_project.status == "draft"

        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == configured_project.id)
        )
        site = result.scalar_one()
        assert site.is_active is False

    @pytest.mark.asyncio
    async def test_republish(self, async_client, auth_headers, configured_project, db_session):
        # Publish first
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )

        # Republish
        resp = await async_client.post(
            f"/api/v1/projects/{configured_project.id}/republish",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "republished"

    @pytest.mark.asyncio
    async def test_export_zip(self, async_client, auth_headers, configured_project):
        resp = await async_client.get(
            f"/api/v1/projects/{configured_project.id}/export-zip",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"

        # Verify ZIP contents
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        names = z.namelist()
        assert "index.html" in names
        assert "style.css" in names
        assert "sitemap.xml" in names
        assert "robots.txt" in names

    @pytest.mark.asyncio
    async def test_export_zip_contains_legal_pages(self, async_client, auth_headers, configured_project):
        resp = await async_client.get(
            f"/api/v1/projects/{configured_project.id}/export-zip",
            headers=auth_headers,
        )
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        names = z.namelist()
        assert "polityka-prywatnosci.html" in names
        assert "regulamin.html" in names

    @pytest.mark.asyncio
    async def test_export_zip_sitemap_valid(self, async_client, auth_headers, configured_project):
        resp = await async_client.get(
            f"/api/v1/projects/{configured_project.id}/export-zip",
            headers=auth_headers,
        )
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        sitemap = z.read("sitemap.xml").decode()
        assert '<?xml version="1.0"' in sitemap
        assert "acme-test" in sitemap
        assert "<loc>" in sitemap


# ============================================================================
# Forms
# ============================================================================

class TestFormSubmissions:
    """Form submissions (3 tests)."""

    @pytest.mark.asyncio
    async def test_submit_form_saves(self, async_client, configured_project, db_session, auth_headers):
        # Publish first to create site
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )

        # Submit form (public endpoint, no auth)
        resp = await async_client.post(
            "/api/v1/sites/acme-test/form-submit",
            json={"data": {"name": "Jan Kowalski", "email": "jan@test.pl", "message": "Cześć!"}},
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "saved"

        # Verify DB
        result = await db_session.execute(select(FormSubmission))
        sub = result.scalar_one()
        assert sub.data_json["name"] == "Jan Kowalski"

    @pytest.mark.asyncio
    async def test_submit_form_404_inactive_site(self, async_client):
        """Submit to non-existent site → 404."""
        resp = await async_client.post(
            "/api/v1/sites/nonexistent-site/form-submit",
            json={"data": {"name": "Test"}},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_form_submissions(self, async_client, configured_project, db_session, auth_headers):
        # Publish + submit
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        await async_client.post(
            "/api/v1/sites/acme-test/form-submit",
            json={"data": {"name": "Test User"}},
        )

        # List submissions
        resp = await async_client.get(
            f"/api/v1/projects/{configured_project.id}/form-submissions",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        subs = resp.json()
        assert len(subs) == 1
        assert subs[0]["data_json"]["name"] == "Test User"


# ============================================================================
# Tracking
# ============================================================================

class TestTracking:
    """Tracking code injection (4 tests)."""

    @pytest.mark.asyncio
    async def test_ga4_script_injected(self, async_client, auth_headers, configured_project, db_session):
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == configured_project.id)
        )
        site = result.scalar_one()
        assert "googletagmanager.com/gtag/js?id=G-TEST123" in site.html_snapshot

    @pytest.mark.asyncio
    async def test_fb_pixel_injected(self, async_client, auth_headers, project_with_sections, db_session):
        project_with_sections.config_json = {
            "seo": {"tracking": {"fb_pixel_id": "999888"}},
            "hosting": {"subdomain": "fb-test", "domain_type": "subdomain", "deploy_method": "auto"},
        }
        await db_session.commit()

        await async_client.post(
            f"/api/v1/projects/{project_with_sections.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == project_with_sections.id)
        )
        site = result.scalar_one()
        assert "999888" in site.html_snapshot
        assert "fbevents.js" in site.html_snapshot

    @pytest.mark.asyncio
    async def test_custom_head_injected(self, async_client, auth_headers, project_with_sections, db_session):
        project_with_sections.config_json = {
            "seo": {"tracking": {"custom_head": '<script>console.log("hello")</script>'}},
            "hosting": {"subdomain": "custom-head-test", "domain_type": "subdomain", "deploy_method": "auto"},
        }
        await db_session.commit()

        await async_client.post(
            f"/api/v1/projects/{project_with_sections.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == project_with_sections.id)
        )
        site = result.scalar_one()
        assert 'console.log("hello")' in site.html_snapshot

    @pytest.mark.asyncio
    async def test_no_tracking_no_scripts(self, async_client, auth_headers, project_with_sections, db_session):
        project_with_sections.config_json = {
            "hosting": {"subdomain": "no-track", "domain_type": "subdomain", "deploy_method": "auto"},
        }
        await db_session.commit()

        await async_client.post(
            f"/api/v1/projects/{project_with_sections.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == project_with_sections.id)
        )
        site = result.scalar_one()
        assert "googletagmanager" not in site.html_snapshot
        assert "fbevents" not in site.html_snapshot


# ============================================================================
# Cookie Banner
# ============================================================================

class TestCookieBanner:
    """Cookie banner rendering (2 tests)."""

    @pytest.mark.asyncio
    async def test_cookie_banner_enabled(self, async_client, auth_headers, configured_project, db_session):
        await async_client.post(
            f"/api/v1/projects/{configured_project.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == configured_project.id)
        )
        site = result.scalar_one()
        assert "cookie-banner" in site.html_snapshot
        assert "Używamy cookies." in site.html_snapshot

    @pytest.mark.asyncio
    async def test_cookie_banner_disabled(self, async_client, auth_headers, project_with_sections, db_session):
        project_with_sections.config_json = {
            "legal": {"cookie_banner": {"enabled": False}},
            "hosting": {"subdomain": "no-cookie", "domain_type": "subdomain", "deploy_method": "auto"},
        }
        await db_session.commit()

        await async_client.post(
            f"/api/v1/projects/{project_with_sections.id}/publish",
            headers=auth_headers,
        )
        result = await db_session.execute(
            select(PublishedSite).where(PublishedSite.project_id == project_with_sections.id)
        )
        site = result.scalar_one()
        assert "cookie-banner" not in site.html_snapshot
