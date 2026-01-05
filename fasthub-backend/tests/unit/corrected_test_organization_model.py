"""Test Organization model"""
import pytest
from app.models.organization import Organization

def test_organization_creation():
    """Test organization basic creation"""
    org = Organization(
        name="Test Company",
        email="info@testcompany.com"
    )
    assert org.name == "Test Company"
    assert org.email == "info@testcompany.com"

def test_organization_tax_id_optional():
    """Test tax_id (NIP) is optional"""
    org = Organization(name="Test")
    assert org.tax_id is None

def test_organization_billing_address_optional():
    """Test billing address fields are optional"""
    org = Organization(name="Test")
    assert org.billing_street is None
    assert org.billing_city is None
    assert org.billing_postal_code is None
    assert org.billing_country is None

def test_organization_with_full_address():
    """Test organization with complete billing address"""
    org = Organization(
        name="Test Corp",
        billing_street="ul. Testowa 1",
        billing_city="Warszawa",
        billing_postal_code="00-001",
        billing_country="Poland"
    )
    assert org.billing_street == "ul. Testowa 1"
    assert org.billing_city == "Warszawa"
