# Test configuration
import asyncio
import os
import sys
from pathlib import Path

import httpx
import pytest

# Set environment variables BEFORE any imports
os.environ.update(
    {
        "DATABASE_URL": "sqlite:///./test.db",
        "REDIS_URL": "redis://localhost:6379",
        "JWT_SECRET": "test-secret-key-for-ci",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
    }
)

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure pytest for asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop


@pytest.fixture(scope="function")
async def client():
    """Create an async test client."""
    # Ensure clean import of app
    import importlib

    import main

    importlib.reload(main)

    app = main.app

    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


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
