# Coverage: app/services/organization_repository.py
# ============================================================================

import pytest
from app.services.organization_repository import (
    get_organization_by_slug,
    update_organization,
    delete_organization,
    list_user_organizations,
    ensure_unique_slug,
)


@pytest.mark.asyncio
async def test_get_organization_by_slug():
    """Test retrieving organization by slug"""
    slug = "test-org"
    org_id = uuid4()
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = {
        "id": org_id,
        "slug": slug,
        "name": "Test Organization"
    }
    mock_db.execute.return_value = mock_result
    
    org = await get_organization_by_slug(mock_db, slug)
    
    assert org is not None
    assert org["slug"] == slug


@pytest.mark.asyncio
async def test_update_organization():
    """Test updating organization fields"""
    org_id = uuid4()
    updates = {"name": "Updated Org Name", "description": "New description"}
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = {"id": org_id, **updates}
    mock_db.execute.return_value = mock_result
    
    updated_org = await update_organization(mock_db, org_id, updates)
    
    assert updated_org["name"] == updates["name"]
    assert updated_org["description"] == updates["description"]
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_organization():
    """Test deleting organization"""
    org_id = uuid4()
    
    mock_db = AsyncMock()
    
    result = await delete_organization(mock_db, org_id)
    
    assert result is True
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_list_user_organizations():
    """Test listing all organizations user belongs to"""
    user_id = uuid4()
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [
        {"id": uuid4(), "name": "Org 1", "role": "owner"},
        {"id": uuid4(), "name": "Org 2", "role": "admin"}
    ]
    mock_db.execute.return_value = mock_result
    
    orgs = await list_user_organizations(mock_db, user_id)
    
    assert len(orgs) == 2
    assert all("role" in org for org in orgs)


@pytest.mark.asyncio
async def test_slug_uniqueness():
    """Test slug generation ensures uniqueness"""
    base_slug = "test-org"
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    # First slug exists, so it should try test-org-2
    mock_result.scalar_one_or_none.side_effect = [
        {"id": uuid4()},  # test-org exists
        None  # test-org-2 doesn't exist
    ]
    mock_db.execute.return_value = mock_result
    
    unique_slug = await ensure_unique_slug(mock_db, base_slug)
    
    assert unique_slug == "test-org-2"
    assert mock_db.execute.call_count == 2
