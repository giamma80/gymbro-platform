"""Tests for application configuration."""

from app.core.config import Settings


def test_settings_creation():
    """Test that settings can be created."""
    settings = Settings()
    assert settings is not None
    assert hasattr(settings, "service_name")
    assert hasattr(settings, "debug")


def test_service_name():
    """Test that service name is set correctly."""
    settings = Settings()
    assert settings.service_name == "user-management"


def test_environment_config():
    """Test that environment configuration is valid."""
    settings = Settings()
    # Test that required fields have default values
    assert isinstance(settings.debug, bool)
    assert isinstance(settings.service_name, str)
    assert len(settings.service_name) > 0
    assert settings.environment in ["development", "staging", "production"]
