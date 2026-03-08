# ============================================================================

from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError
from app.main import app


@pytest.mark.asyncio
async def test_database_connection_failure():
    """Test graceful error when database is unavailable"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch('app.db.session.get_db') as mock_db:
            mock_db.side_effect = ConnectionError("Database unavailable")
            
            response = await client.get("/api/v1/users/me", headers={"Authorization": "Bearer test"})
            
            assert response.status_code == 503
            assert "database" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_duplicate_key_violation():
    """Test creating user with existing email returns 400"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create first user
        user_data = {
            "email": "duplicate@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        }
        
        response1 = await client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = await client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_foreign_key_constraint_violation():
    """Test deleting user with members returns error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # This would be tested with proper database setup
        # For now, mock the constraint violation
        with patch('app.services.user_service.delete_user') as mock_delete:
            mock_delete.side_effect = IntegrityError("", "", "foreign key constraint")
            
            response = await client.delete(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer test"}
            )
            
            assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_transaction_rollback():
    """Test transaction rollback on error"""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.commit.side_effect = Exception("Commit failed")
    
    from app.services.organization_service import create_organization
    
    try:
        await create_organization(
            mock_db,
            name="Test Org",
            owner_id=uuid4()
        )
    except Exception:
        pass
    
    mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_null_constraint_violation():
    """Test creating record with missing required field returns 400"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to create user without required fields
        incomplete_data = {"email": "test@example.com"}  # Missing password
        
        response = await client.post("/api/v1/auth/register", json=incomplete_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("password" in str(err).lower() for err in errors)
