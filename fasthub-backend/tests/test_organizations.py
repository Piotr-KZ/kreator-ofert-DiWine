"""Organization management tests"""


def test_get_my_organization(client, auth_headers):
    """Test getting current organization"""
    response = client.get("/api/v1/organizations/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "is_complete" in data


def test_complete_organization(client, auth_headers):
    """Test completing organization onboarding"""
    # Get organization ID
    org_response = client.get("/api/v1/organizations/me", headers=auth_headers)
    org_id = org_response.json()["id"]
    
    # Complete organization
    response = client.patch(
        f"/api/v1/organizations/{org_id}/complete",
        headers=auth_headers,
        json={
            "name": "Test Company",
            "type": "business",
            "nip": "1234567890",
            "phone": "+48123456789",
            "billing_street": "ul. Testowa 123",
            "billing_city": "Warsaw",
            "billing_postal_code": "00-001",
            "billing_country": "Poland"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["is_complete"] is True
    assert data["nip"] == "1234567890"


def test_complete_organization_invalid_nip(client, auth_headers):
    """Test completing organization with invalid NIP"""
    org_response = client.get("/api/v1/organizations/me", headers=auth_headers)
    org_id = org_response.json()["id"]
    
    response = client.patch(
        f"/api/v1/organizations/{org_id}/complete",
        headers=auth_headers,
        json={
            "name": "Test Company",
            "type": "business",
            "nip": "12345",  # Invalid - too short
            "phone": "+48123456789",
            "billing_street": "ul. Testowa 123",
            "billing_city": "Warsaw",
            "billing_postal_code": "00-001",
            "billing_country": "Poland"
        }
    )
    
    assert response.status_code == 422
    assert "nip" in str(response.json()).lower()


def test_complete_organization_invalid_postal_code(client, auth_headers):
    """Test completing organization with invalid postal code"""
    org_response = client.get("/api/v1/organizations/me", headers=auth_headers)
    org_id = org_response.json()["id"]
    
    response = client.patch(
        f"/api/v1/organizations/{org_id}/complete",
        headers=auth_headers,
        json={
            "name": "Test Company",
            "type": "business",
            "nip": "1234567890",
            "phone": "+48123456789",
            "billing_street": "ul. Testowa 123",
            "billing_city": "Warsaw",
            "billing_postal_code": "1234",  # Invalid - too short
            "billing_country": "Poland"
        }
    )
    
    assert response.status_code == 422
    assert "postal" in str(response.json()).lower()


def test_update_organization(client, auth_headers):
    """Test updating organization"""
    org_response = client.get("/api/v1/organizations/me", headers=auth_headers)
    org_id = org_response.json()["id"]
    
    response = client.patch(
        f"/api/v1/organizations/{org_id}",
        headers=auth_headers,
        json={
            "name": "Updated Org Name"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Org Name"
