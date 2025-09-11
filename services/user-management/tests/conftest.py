"""Pytest configuration and fixtures for user-management service."""

import os
from unittest.mock import patch

import pytest

# Mock environment variables at module level (before any imports)
# This ensures the mock is active during pytest collection phase
test_env = {
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon-key",
    "SUPABASE_SERVICE_KEY": "test-service-key",
    "SECRET_KEY": "test-secret-key",
    "DATABASE_SCHEMA": "test_schema",
    "ENVIRONMENT": "test",
    "DEBUG": "true",
}

# Apply the mock globally before any imports happen
_mock_patcher = patch.dict(os.environ, test_env)
_mock_patcher.start()


@pytest.fixture
def test_settings():
    """Provide test settings instance."""
    from app.core.config import Settings

    return Settings()


# Cleanup mock after all tests are done
def pytest_unconfigure():
    """Clean up the environment mock after tests."""
    _mock_patcher.stop()
