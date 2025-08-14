"""
Debug test per verificare cosa restituisce l'endpoint health
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_debug_health():
    """Debug test per verificare la response dell'endpoint health."""
    # Setup test environment
    test_env = {
        "DATABASE_URL": "postgresql://localhost:5432/gymbro_test_db",
        "REDIS_URL": "redis://localhost:6379",
        "JWT_SECRET": "test-secret-key-for-testing",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
    }

    with patch.dict(os.environ, test_env, clear=False):
        from main import app

        with TestClient(app) as client:
            response = client.get("/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Content: {response.content}")
            print(
                f"Response JSON: {response.json() if response.content else 'No content'}"
            )

            # Anche se il test fallisce, vogliamo vedere l'output
            assert False, f"Response details logged above"


if __name__ == "__main__":
    test_debug_health()
