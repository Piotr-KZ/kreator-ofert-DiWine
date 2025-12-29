"""Auth tests"""


def test_register_user(client, test_user_data):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user_data):
    """Test duplicate email registration"""
    # First registration
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Second registration (duplicate)
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password"""
    # Register
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Login with wrong password
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPassword123!"
    })
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()
