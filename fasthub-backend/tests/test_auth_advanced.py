"""Advanced auth tests"""


def test_refresh_token(client, test_user_data):
    """Test token refresh"""
    # Register & login
    client.post("/api/v1/auth/register", json=test_user_data)
    login_response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_logout(client, test_user_data, auth_headers):
    """Test logout (token blacklist)"""
    response = client.post("/api/v1/auth/logout", headers=auth_headers)
    
    assert response.status_code == 200
    
    # Token should not work after logout
    response = client.get("/api/v1/organizations/me", headers=auth_headers)
    assert response.status_code == 401


def test_password_reset_request(client, test_user_data):
    """Test password reset request"""
    # Register
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Request reset
    response = client.post(
        "/api/v1/auth/password-reset",
        json={"email": test_user_data["email"]}
    )
    
    assert response.status_code == 200


def test_password_change(client, test_user_data, auth_headers):
    """Test password change"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!"
        }
    )
    
    assert response.status_code == 200
