"""Basic health check tests for user-management service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test that the health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-management"


def test_api_v1_health():
    """Test that the API v1 health endpoint returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-management"
    assert data["version"] == "1.0.0"


def test_docs_endpoint():
    """Test that the API docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint():
    """Test that the ReDoc endpoint is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_app_startup():
    """Test that the app can start up without errors."""
    # This test ensures the app configuration is valid
    assert app is not None
    assert hasattr(app, "routes")
    assert len(app.routes) > 0
