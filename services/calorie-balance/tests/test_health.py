"""Basic health check tests for calorie-balance service."""

from unittest.mock import MagicMock, patch

import pytest


def test_health_endpoint_import():
    """Test that health endpoint can be imported without external dependencies."""
    # Mock Supabase client creation to avoid actual connections
    with patch("app.core.database.create_supabase_client") as mock_client:
        mock_client.return_value = MagicMock()

        from app.api.v1.endpoints.health import router

        assert router is not None


def test_settings_can_be_created():
    """Test that settings can be created with test environment."""
    from app.core.config import Settings

    settings = Settings()
    assert settings.service_name == "calorie-balance"
    assert settings.environment == "test"


def test_basic_configuration():
    """Test basic configuration without external dependencies."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings is not None
    assert settings.debug is True  # Should be True in test environment


@pytest.mark.asyncio
async def test_app_can_be_created():
    """Test that the FastAPI app can be created with mocked dependencies."""
    with patch("app.core.database.create_supabase_client") as mock_client:
        mock_client.return_value = None
        
        # Import app after mocking the database client
        from app.main import app
        
        # Test that app was created successfully
        assert app is not None
        assert app.title == "CalorieBalance Service"


@pytest.mark.asyncio
async def test_health_endpoint_function():
    """Test the health endpoint function directly."""
    with patch("app.core.database.create_supabase_client") as mock_client:
        mock_client.return_value = MagicMock()

        from app.api.v1.endpoints.health import health_status
        from app.core.config import get_settings

        # Test the function directly
        result = await health_status()
        settings = get_settings()

        assert result["status"] == "healthy"
        assert result["service"] == settings.service_name
        assert result["version"] == "1.0.0"
