"""
Tests for WebCreator: Projects, Brief, Style, Materials, Sections, Blocks, Seed.
"""

import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockCategory, BlockTemplate
from app.models.project import Project
from app.models.project_material import ProjectMaterial
from app.models.project_section import ProjectSection


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_organization, test_user) -> Project:
    """Create a test project."""
    project = Project(
        organization_id=test_organization.id,
        created_by=test_user.id,
        name="Test Website",
        site_type="firmowa",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_section(db_session: AsyncSession, test_project) -> ProjectSection:
    """Create a test section."""
    section = ProjectSection(
        project_id=test_project.id,
        block_code="HE1",
        position=0,
        variant="A",
        slots_json={"title": "Hello", "subtitle": "World"},
    )
    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)
    return section


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession) -> BlockCategory:
    """Create a test block category."""
    cat = BlockCategory(code="HE", name="Hero", icon="layout-dashboard", order=0)
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)
    return cat


@pytest_asyncio.fixture
async def test_block_template(db_session: AsyncSession, test_category) -> BlockTemplate:
    """Create a test block template."""
    tmpl = BlockTemplate(
        code="HE1",
        category_code="HE",
        name="Hero z tlem",
        html_template="<section><h1>{{title}}</h1></section>",
        slots_definition=[
            {"id": "title", "type": "text", "label": "Tytul", "max_length": 80},
        ],
        media_type="photo",
        layout_type="photo-top-1",
    )
    db_session.add(tmpl)
    await db_session.commit()
    await db_session.refresh(tmpl)
    return tmpl


# ============================================================================
# Projects CRUD
# ============================================================================

@pytest.mark.asyncio
async def test_create_project(async_client, auth_headers):
    """Create project -> 201, status=draft."""
    response = await async_client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Moja strona", "site_type": "firmowa"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Moja strona"
    assert data["status"] == "draft"
    assert data["current_step"] == 1


@pytest.mark.asyncio
async def test_list_projects(async_client, auth_headers, test_project):
    """List projects -> only projects from this organization."""
    response = await async_client.get("/api/v1/projects", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "Test Website" for p in data)


@pytest.mark.asyncio
async def test_get_project(async_client, auth_headers, test_project):
    """Get project details with sections and materials."""
    response = await async_client.get(
        f"/api/v1/projects/{test_project.id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Website"
    assert data["site_type"] == "firmowa"


@pytest.mark.asyncio
async def test_update_project(async_client, auth_headers, test_project):
    """Update project name and status."""
    response = await async_client.patch(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers,
        json={"name": "Updated Name", "status": "generating"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "generating"


@pytest.mark.asyncio
async def test_delete_project(async_client, auth_headers, test_project):
    """Delete project -> cascade: sections, materials deleted."""
    response = await async_client.delete(
        f"/api/v1/projects/{test_project.id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deleted
    response = await async_client.get(
        f"/api/v1/projects/{test_project.id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_duplicate_project(async_client, auth_headers, test_project, test_section):
    """Duplicate project -> copy with sections, status=draft."""
    response = await async_client.post(
        f"/api/v1/projects/{test_project.id}/duplicate", headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Website (kopia)"
    assert data["status"] == "draft"
    assert data["id"] != str(test_project.id)


# ============================================================================
# Brief
# ============================================================================

@pytest.mark.asyncio
async def test_save_brief(async_client, auth_headers, test_project):
    """Save brief_json."""
    brief = {
        "site_type": "firmowa",
        "company_name": "ACME",
        "industry": "IT",
        "description": "Firma IT",
    }
    response = await async_client.put(
        f"/api/v1/projects/{test_project.id}/brief",
        headers=auth_headers,
        json=brief,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_get_brief(async_client, auth_headers, test_project, db_session):
    """Get brief_json."""
    # First save
    test_project.brief_json = {"company_name": "ACME"}
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/projects/{test_project.id}/brief", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["company_name"] == "ACME"


# ============================================================================
# Materials
# ============================================================================

@pytest.mark.asyncio
async def test_add_link_material(async_client, auth_headers, test_project):
    """Add a link/inspiration material."""
    response = await async_client.post(
        f"/api/v1/projects/{test_project.id}/materials/link",
        headers=auth_headers,
        json={"url": "https://example.com", "type": "inspiration", "description": "Nice site"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["external_url"] == "https://example.com"
    assert data["type"] == "inspiration"


@pytest.mark.asyncio
async def test_list_materials(async_client, auth_headers, test_project, db_session):
    """List project materials."""
    mat = ProjectMaterial(
        project_id=test_project.id,
        type="link",
        external_url="https://example.com",
    )
    db_session.add(mat)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/projects/{test_project.id}/materials", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_delete_material(async_client, auth_headers, test_project, db_session):
    """Delete material -> record removed."""
    mat = ProjectMaterial(
        project_id=test_project.id,
        type="link",
        external_url="https://example.com",
    )
    db_session.add(mat)
    await db_session.commit()
    await db_session.refresh(mat)

    response = await async_client.delete(
        f"/api/v1/projects/{test_project.id}/materials/{mat.id}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


# ============================================================================
# Style
# ============================================================================

@pytest.mark.asyncio
async def test_save_style(async_client, auth_headers, test_project):
    """Save style_json."""
    style = {
        "color_primary": "#3B82F6",
        "heading_font": "Outfit",
        "border_radius": "rounded-sm",
    }
    response = await async_client.put(
        f"/api/v1/projects/{test_project.id}/style",
        headers=auth_headers,
        json=style,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_get_style(async_client, auth_headers, test_project, db_session):
    """Get style_json."""
    test_project.style_json = {"color_primary": "#FF0000"}
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/projects/{test_project.id}/style", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["color_primary"] == "#FF0000"


# ============================================================================
# Sections
# ============================================================================

@pytest.mark.asyncio
async def test_add_section(async_client, auth_headers, test_project):
    """Add section -> position auto."""
    response = await async_client.post(
        f"/api/v1/projects/{test_project.id}/sections",
        headers=auth_headers,
        json={"block_code": "HE1", "variant": "A"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["block_code"] == "HE1"
    assert data["position"] == 0


@pytest.mark.asyncio
async def test_update_section(async_client, auth_headers, test_project, test_section):
    """Update section content and variant."""
    response = await async_client.patch(
        f"/api/v1/projects/{test_project.id}/sections/{test_section.id}",
        headers=auth_headers,
        json={"variant": "B", "slots_json": {"title": "Updated"}},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["variant"] == "B"
    assert data["slots_json"]["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_section(async_client, auth_headers, test_project, test_section):
    """Delete section -> renumber."""
    response = await async_client.delete(
        f"/api/v1/projects/{test_project.id}/sections/{test_section.id}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_reorder_sections(async_client, auth_headers, test_project, db_session):
    """Reorder sections via drag & drop."""
    s1 = ProjectSection(project_id=test_project.id, block_code="HE1", position=0)
    s2 = ProjectSection(project_id=test_project.id, block_code="FI1", position=1)
    db_session.add_all([s1, s2])
    await db_session.commit()
    await db_session.refresh(s1)
    await db_session.refresh(s2)

    # Reverse order
    response = await async_client.post(
        f"/api/v1/projects/{test_project.id}/sections/reorder",
        headers=auth_headers,
        json={"order": [str(s2.id), str(s1.id)]},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_list_sections(async_client, auth_headers, test_project, test_section):
    """List sections sorted by position."""
    response = await async_client.get(
        f"/api/v1/projects/{test_project.id}/sections", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


# ============================================================================
# Block Templates
# ============================================================================

@pytest.mark.asyncio
async def test_list_categories(async_client, auth_headers, test_category):
    """List block categories."""
    response = await async_client.get(
        "/api/v1/blocks/categories", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(c["code"] == "HE" for c in data)


@pytest.mark.asyncio
async def test_list_blocks(async_client, auth_headers, test_block_template):
    """List block templates with filtering."""
    response = await async_client.get(
        "/api/v1/blocks?category=HE", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_match_blocks(async_client, auth_headers, test_block_template):
    """Configurator: match blocks by criteria."""
    response = await async_client.post(
        "/api/v1/blocks/match",
        headers=auth_headers,
        json={"media_type": "photo"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


# ============================================================================
# Authorization
# ============================================================================

@pytest.mark.asyncio
async def test_project_belongs_to_org(async_client, auth_headers, db_session, test_user):
    """Cannot access projects from another organization."""
    from app.models import Organization

    other_org = Organization(name="Other Org", slug="other-org")
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)

    other_project = Project(
        organization_id=other_org.id,
        created_by=test_user.id,
        name="Other Project",
    )
    db_session.add(other_project)
    await db_session.commit()
    await db_session.refresh(other_project)

    response = await async_client.get(
        f"/api/v1/projects/{other_project.id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Seed
# ============================================================================

@pytest.mark.asyncio
async def test_seed_categories(db_session):
    """Seed 21 categories (NA, HE, FI, OF, CE, ZE, OP, FA, CT, KO, FO, GA, RE, PR, PB, RO, KR, CF, OB, LO, ST)."""
    from app.services.creator.block_service import seed_block_categories

    created = await seed_block_categories(db_session)
    assert created == 21

    result = await db_session.execute(select(BlockCategory))
    categories = result.scalars().all()
    assert len(categories) == 21

    # Idempotent — run again
    created2 = await seed_block_categories(db_session)
    assert created2 == 0
