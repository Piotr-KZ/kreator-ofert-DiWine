# ============================================================================


@pytest.mark.asyncio
async def test_access_other_user_profile():
    """Test user cannot access another user's profile"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        other_user_id = uuid4()
        
        response = await client.get(
            f"/api/v1/users/{other_user_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_access_other_organization():
    """Test user cannot access organization they don't belong to"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        other_org_id = uuid4()
        
        response = await client.get(
            f"/api/v1/organizations/{other_org_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_non_admin_cannot_delete_members():
    """Test viewer role cannot delete organization members"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        org_id = uuid4()
        member_id = uuid4()
        
        # Token for viewer role
        response = await client.delete(
            f"/api/v1/organizations/{org_id}/members/{member_id}",
            headers={"Authorization": "Bearer viewer_token"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_non_owner_cannot_delete_organization():
    """Test admin cannot delete organization (only owner can)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        org_id = uuid4()
        
        # Token for admin (not owner)
        response = await client.delete(
            f"/api/v1/organizations/{org_id}",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 403
        assert "owner" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_blacklisted_token_rejected():
    """Test logged-out token is rejected"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First logout (blacklists token)
        token = "valid.jwt.token"
        await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to use blacklisted token
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert "blacklisted" in response.json()["detail"].lower() or "logged out" in response.json()["detail"].lower()


# ====================================================================================
# PHASE 3: LOW PRIORITY - Schema Validation (15 tests)
# ====================================================================================
