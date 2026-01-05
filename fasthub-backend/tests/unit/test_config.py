"""Test configuration and settings"""
import pytest
from app.core.config import Settings

def test_settings_loaded():
    """Test settings can be loaded"""
    settings = Settings()
    assert settings.PROJECT_NAME is not None
    assert settings.VERSION is not None

def test_settings_has_required_fields():
    """Test settings has all required fields"""
    settings = Settings()
    
    # Required fields
    assert hasattr(settings, "DATABASE_URL")
    assert hasattr(settings, "SECRET_KEY")
    assert hasattr(settings, "ALGORITHM")
    assert hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")

def test_settings_default_values():
    """Test settings default values"""
    settings = Settings()
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

def test_settings_environment_variable():
    """Test settings can be overridden by env vars"""
    import os
    os.environ["PROJECT_NAME"] = "TestProject"
    
    settings = Settings()
    assert settings.PROJECT_NAME == "TestProject"
    
    # Cleanup
    del os.environ["PROJECT_NAME"]
