"""Pytest configuration and fixtures for user-management service."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    """Mock required environment variables for all tests."""
    test_env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "test-anon-key",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "SECRET_KEY": "test-secret-key",
        "DATABASE_SCHEMA": "test_schema",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
    }
    
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def test_settings():
    """Provide test settings instance."""
    from app.core.config import Settings
    return Settings()
