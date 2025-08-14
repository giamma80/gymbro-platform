# Test configuration
import asyncio

import pytest
from fastapi.testclient import TestClient

from main import app

# Configure async testing
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    """Create a test database session."""
    # In a real implementation, you would create a test database
    # For now, this is a placeholder
    yield None


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "height_cm": 180,
        "weight_kg": 75.5,
        "activity_level": "moderately_active",
    }


@pytest.fixture
def admin_user_data():
    """Sample admin user data for testing."""
    return {
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "first_name": "Admin",
        "last_name": "User",
        "date_of_birth": "1985-01-01",
        "gender": "female",
        "height_cm": 165,
        "weight_kg": 60.0,
        "activity_level": "very_active",
        "role": "admin",
    }


@pytest.fixture
def jwt_token(client, sample_user_data):
    """Create a valid JWT token for testing."""
    # For unit tests, we'll create a mock token
    # In integration tests, this would do actual registration/login
    from auth import create_access_token

    token_data = {
        "sub": sample_user_data["email"],
        "user_id": "test-user-id",
        "role": "user",
    }
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(jwt_token):
    """Create authorization headers with JWT token."""
    return {"Authorization": f"Bearer {jwt_token}"}
