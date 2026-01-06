# Coverage: app/services/user_repository.py
# ============================================================================

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.user_repository import (
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    delete_user,
    search_users,
)


@pytest.mark.asyncio
async def test_get_user_by_email():
    """Test retrieving user by email address"""
    email = "test@example.com"
    user_id = uuid4()
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = {
        "id": user_id,
        "email": email,
        "full_name": "Test User"
    }
    mock_db.execute.return_value = mock_result
    
    user = await get_user_by_email(mock_db, email)
    
    assert user is not None
    assert user["email"] == email
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_id():
    """Test retrieving user by UUID"""
    user_id = uuid4()
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = {
        "id": user_id,
        "email": "test@example.com"
    }
    mock_db.execute.return_value = mock_result
    
    user = await get_user_by_id(mock_db, user_id)
    
    assert user is not None
    assert user["id"] == user_id


@pytest.mark.asyncio
async def test_update_user_profile():
    """Test updating user profile fields"""
    user_id = uuid4()
    updates = {"full_name": "Updated Name", "phone": "+1234567890"}
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = {"id": user_id, **updates}
    mock_db.execute.return_value = mock_result
    
    updated_user = await update_user_profile(mock_db, user_id, updates)
    
    assert updated_user["full_name"] == updates["full_name"]
    assert updated_user["phone"] == updates["phone"]
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user():
    """Test soft-deleting user account"""
    user_id = uuid4()
    
    mock_db = AsyncMock()
    
    result = await delete_user(mock_db, user_id)
    
    assert result is True
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_search_users():
    """Test searching users by name or email"""
    search_term = "john"
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [
        {"id": uuid4(), "email": "john@example.com", "full_name": "John Doe"},
        {"id": uuid4(), "email": "johnny@example.com", "full_name": "Johnny Smith"}
    ]
    mock_db.execute.return_value = mock_result
    
    users = await search_users(mock_db, search_term, limit=10)
    
    assert len(users) == 2
    assert any("john" in user["email"].lower() for user in users)


# ============================================================================
