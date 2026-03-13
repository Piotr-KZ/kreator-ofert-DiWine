"""
Tests for Brief 36: Dashboard — Stats, Integrations, Forms, Catalog.
26 tests covering all new endpoints + model behaviour.
"""

import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.form_submission import FormSubmission
from app.models.project import Project
from app.models.published_site import PublishedSite
from app.models.site_integration import SiteIntegration


# ─── Fixtures ───


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_organization, test_user) -> Project:
    """Create a test project."""
    project = Project(
        organization_id=test_organization.id,
        created_by=test_user.id,
        name="Dashboard Test Site",
        site_type="firmowa",
        status="published",
        current_step=9,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def published_site(
    db_session: AsyncSession, test_project, test_organization
) -> PublishedSite:
    """Create a published site for the test project."""
    site = PublishedSite(
        project_id=test_project.id,
        organization_id=test_organization.id,
        subdomain="test-dashboard",
        is_active=True,
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site


@pytest_asyncio.fixture
async def site_integration(
    db_session: AsyncSession, published_site
) -> SiteIntegration:
    """Create a connected integration."""
    integration = SiteIntegration(
        site_id=published_site.id,
        provider="google_analytics",
        status="configured",
        config_json={"tracking_id": "G-TEST123"},
    )
    db_session.add(integration)
    await db_session.commit()
    await db_session.refresh(integration)
    return integration


@pytest_asyncio.fixture
async def form_submission(
    db_session: AsyncSession, published_site, test_organization
) -> FormSubmission:
    """Create a form submission."""
    submission = FormSubmission(
        site_id=published_site.id,
        organization_id=test_organization.id,
        data_json={"name": "Jan Kowalski", "email": "jan@test.pl", "message": "Test"},
        ip="127.0.0.1",
        read=False,
    )
    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)
    return submission


# ─── MySites ───


class TestMySites:
    @pytest.mark.asyncio
    async def test_list_projects(self, async_client, auth_headers, test_project):
        """GET /projects → list with status and step."""
        response = await async_client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        site = next(p for p in data if p["id"] == str(test_project.id))
        assert site["status"] == "published"
        assert site["current_step"] == 9

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, async_client, auth_headers):
        """GET /projects → empty list when no projects."""
        response = await async_client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_project_redirect(self, async_client, auth_headers):
        """POST /projects → 201 creates new project."""
        response = await async_client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"name": "Nowa Strona"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "Nowa Strona"
        assert response.json()["status"] == "draft"

    @pytest.mark.asyncio
    async def test_project_has_published_at(self, async_client, auth_headers, test_project):
        """GET /projects/{id} → includes published_at field."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "published_at" in response.json()


# ─── Stats ───


class TestStats:
    @pytest.mark.asyncio
    async def test_stats_returns_structure(
        self, async_client, auth_headers, test_project, published_site
    ):
        """GET /projects/{id}/stats → returns correct structure."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "visitors" in data
        assert "leads" in data
        assert "bounce_rate" in data
        assert "published_at" in data
        assert "daily_visitors" in data
        assert "traffic_sources" in data

    @pytest.mark.asyncio
    async def test_stats_counts_leads(
        self, async_client, auth_headers, test_project, published_site, form_submission
    ):
        """Stats leads count reflects form_submissions."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["leads"] >= 1

    @pytest.mark.asyncio
    async def test_stats_period_filter(
        self, async_client, auth_headers, test_project, published_site
    ):
        """Stats accepts period parameter."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}/stats?period=7d",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["period"] == "7d"

    @pytest.mark.asyncio
    async def test_stats_unpublished_returns_empty(
        self, async_client, auth_headers, test_project
    ):
        """Stats for unpublished site returns zeros."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["visitors"] == 0
        assert data["leads"] == 0


# ─── Integrations ───


class TestIntegrations:
    @pytest.mark.asyncio
    async def test_catalog_returns_categories(self, async_client):
        """GET /integrations/catalog → returns 9 categories."""
        response = await async_client.get("/api/v1/integrations/catalog")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 9
        categories = [c["category"] for c in data]
        assert "analytics" in categories
        assert "email_marketing" in categories
        assert "payments" in categories

    @pytest.mark.asyncio
    async def test_automations_catalog(self, async_client):
        """GET /integrations/automations → returns automation templates."""
        response = await async_client.get("/api/v1/integrations/automations")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3
        groups = [g["group"] for g in data]
        assert "forms_leads" in groups

    @pytest.mark.asyncio
    async def test_connect_integration(
        self, async_client, auth_headers, test_project, published_site, db_session
    ):
        """POST /projects/{id}/integrations → 201 saves to DB."""
        response = await async_client.post(
            f"/api/v1/projects/{test_project.id}/integrations",
            headers=auth_headers,
            json={"provider": "hotjar", "config_json": {"site_id": "1234567"}},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["provider"] == "hotjar"
        assert data["status"] == "configured"

        # Verify in DB
        result = await db_session.execute(
            select(SiteIntegration).where(SiteIntegration.provider == "hotjar")
        )
        assert result.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_list_connected_integrations(
        self, async_client, auth_headers, test_project, published_site, site_integration
    ):
        """GET /projects/{id}/integrations → returns connected list."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}/integrations",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["provider"] == "google_analytics"

    @pytest.mark.asyncio
    async def test_disconnect_integration(
        self, async_client, auth_headers, test_project, published_site, site_integration, db_session
    ):
        """DELETE /projects/{id}/integrations/{iid} → removes from DB."""
        response = await async_client.delete(
            f"/api/v1/projects/{test_project.id}/integrations/{site_integration.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["deleted"] is True

        # Verify removed from DB
        result = await db_session.execute(
            select(SiteIntegration).where(SiteIntegration.id == site_integration.id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_duplicate_provider_blocked(
        self, async_client, auth_headers, test_project, published_site, site_integration
    ):
        """POST duplicate provider → 409."""
        response = await async_client.post(
            f"/api/v1/projects/{test_project.id}/integrations",
            headers=auth_headers,
            json={"provider": "google_analytics", "config_json": {"tracking_id": "G-NEW"}},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_test_endpoint(
        self, async_client, auth_headers, test_project, published_site, site_integration
    ):
        """POST /integrations/{id}/test → returns ok."""
        response = await async_client.post(
            f"/api/v1/projects/{test_project.id}/integrations/{site_integration.id}/test",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["provider"] == "google_analytics"

    @pytest.mark.asyncio
    async def test_integration_not_found(
        self, async_client, auth_headers, test_project, published_site
    ):
        """DELETE unknown integration → 404."""
        import uuid

        response = await async_client.delete(
            f"/api/v1/projects/{test_project.id}/integrations/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_connect_no_published_site(self, async_client, auth_headers, test_project):
        """POST integration without published site → 404."""
        response = await async_client.post(
            f"/api/v1/projects/{test_project.id}/integrations",
            headers=auth_headers,
            json={"provider": "hotjar", "config_json": {}},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─── Forms ───


class TestForms:
    @pytest.mark.asyncio
    async def test_list_submissions(
        self, async_client, auth_headers, test_project, published_site, form_submission
    ):
        """GET /projects/{id}/form-submissions → returns list."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project.id}/form-submissions",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["data_json"]["name"] == "Jan Kowalski"

    @pytest.mark.asyncio
    async def test_mark_submission_read(
        self, async_client, auth_headers, test_project, published_site, form_submission
    ):
        """PATCH /form-submissions/{id} → mark as read."""
        response = await async_client.patch(
            f"/api/v1/projects/{test_project.id}/form-submissions/{form_submission.id}",
            headers=auth_headers,
            json={"read": True},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["read"] is True

    @pytest.mark.asyncio
    async def test_public_form_submit(
        self, async_client, published_site, db_session
    ):
        """POST /sites/{subdomain}/form-submit → 201 saves data."""
        response = await async_client.post(
            f"/api/v1/sites/{published_site.subdomain}/form-submit",
            json={"data": {"email": "visitor@example.com", "msg": "Hello"}},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "saved"

        # Verify in DB
        result = await db_session.execute(
            select(FormSubmission).where(FormSubmission.site_id == published_site.id)
        )
        subs = result.scalars().all()
        assert len(subs) >= 1


# ─── Model ───


class TestModel:
    @pytest.mark.asyncio
    async def test_site_integration_create(self, db_session, published_site):
        """SiteIntegration can be created with all fields."""
        integration = SiteIntegration(
            site_id=published_site.id,
            provider="clarity",
            status="configured",
            config_json={"project_id": "abc123"},
        )
        db_session.add(integration)
        await db_session.commit()
        await db_session.refresh(integration)
        assert integration.id is not None
        assert integration.provider == "clarity"
        assert integration.connected_at is not None

    @pytest.mark.asyncio
    async def test_cascade_delete_with_site(self, db_session, published_site):
        """Deleting published site cascades to integrations."""
        integration = SiteIntegration(
            site_id=published_site.id,
            provider="tidio",
            config_json={"public_key": "xxx"},
        )
        db_session.add(integration)
        await db_session.commit()

        # Delete the published site
        await db_session.delete(published_site)
        await db_session.commit()

        # Integration should be gone
        result = await db_session.execute(
            select(SiteIntegration).where(SiteIntegration.provider == "tidio")
        )
        assert result.scalar_one_or_none() is None
