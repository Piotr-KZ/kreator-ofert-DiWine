# ============================================================================


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    """Test 429 error after exceeding rate limit"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 101 requests (assuming limit is 100/min)
        for i in range(101):
            response = await client.get("/api/v1/health")
            
            if i < 100:
                assert response.status_code == 200
            else:
                assert response.status_code == 429


@pytest.mark.asyncio
async def test_rate_limit_reset():
    """Test rate limit resets after time window"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Exceed limit
        for _ in range(101):
            await client.get("/api/v1/health")
        
        response = await client.get("/api/v1/health")
        assert response.status_code == 429
        
        # Wait for reset (mock time)
        with patch('app.core.rate_limit.time') as mock_time:
            mock_time.time.return_value += 61  # 61 seconds later
            
            response = await client.get("/api/v1/health")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_per_user():
    """Test rate limit is tracked per authenticated user"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # User 1 exceeds limit
        for _ in range(101):
            await client.get("/api/v1/users/me", headers={"Authorization": "Bearer user1_token"})
        
        response1 = await client.get("/api/v1/users/me", headers={"Authorization": "Bearer user1_token"})
        assert response1.status_code == 429
        
        # User 2 should still be able to make requests
        response2 = await client.get("/api/v1/users/me", headers={"Authorization": "Bearer user2_token"})
        assert response2.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_per_ip():
    """Test rate limit is tracked per IP address for anonymous requests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make requests from IP 192.168.1.1
        for _ in range(101):
            await client.get("/api/v1/health", headers={"X-Forwarded-For": "192.168.1.1"})
        
        response1 = await client.get("/api/v1/health", headers={"X-Forwarded-For": "192.168.1.1"})
        assert response1.status_code == 429
        
        # Different IP should work
        response2 = await client.get("/api/v1/health", headers={"X-Forwarded-For": "192.168.1.2"})
        assert response2.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_headers():
    """Test rate limit headers are returned (X-RateLimit-*)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        
        limit = int(response.headers["X-RateLimit-Limit"])
        remaining = int(response.headers["X-RateLimit-Remaining"])
        
        assert remaining < limit


# ====================================================================================
# PHASE 3: LOW PRIORITY - Auth Edge Cases (3 remaining)
# ====================================================================================
