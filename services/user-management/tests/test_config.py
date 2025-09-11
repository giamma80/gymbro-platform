"""Tests for application configuration."""


def test_settings_creation(test_settings):
    """Test that settings can be created with required env vars."""
    assert test_settings is not None
    assert hasattr(test_settings, "service_name")
    assert hasattr(test_settings, "debug")


def test_service_name(test_settings):
    """Test that service name is set correctly."""
    assert test_settings.service_name == "user-management"


def test_environment_config(test_settings):
    """Test that environment configuration is valid."""
    # Test that required fields have default values
    assert isinstance(test_settings.debug, bool)
    assert isinstance(test_settings.service_name, str)
    assert len(test_settings.service_name) > 0
    valid_envs = ["development", "staging", "production", "test"]
    assert test_settings.environment in valid_envs
