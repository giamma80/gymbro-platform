"""
Test per API endpoints
"""

import json

import pytest


class TestHealthEndpoints:
    """Test per endpoint di health check."""

    @pytest.mark.asyncio
    async @pytest.mark.asyncio
 async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    @pytest.mark.asyncio
    async @pytest.mark.asyncio
 async def test_readiness_check(self, client):
        """Test readiness endpoint."""
        response = await client.get("/ready")
        assert response.status_code == 200

        data = response.json()
        assert "ready" in data
        assert data["ready"] is True


class TestAuthenticationEndpoints:
    """Test per endpoint di autenticazione."""

    @pytest.mark.asyncio
    async @pytest.mark.asyncio
 async def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = await client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 201

        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert data["message"] == "User registered successfully"

    @pytest.mark.asyncio


    async def test_register_user_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email."""
        # First registration
        response = await client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 201

        # Second registration with same email
        response = await client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio


    async def test_register_user_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email."""
        sample_user_data["email"] = "invalid-email"

        response = await client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio


    async def test_register_user_weak_password(self, client, sample_user_data):
        """Test registration with weak password."""
        sample_user_data["password"] = "weak"

        response = await client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "password" in data["detail"].lower()

    @pytest.mark.asyncio


    async def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        # Register user first
        client.post("/auth/register", json=sample_user_data)

        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio


    async def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/auth/register", json=sample_user_data)

        # Login with wrong password
        login_data = {"email": sample_user_data["email"], "password": "wrong_password"}
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio


    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 401


class TestUserProfileEndpoints:
    """Test per endpoint del profilo utente."""

    @pytest.mark.asyncio


    async def test_get_profile_success(self, client, auth_headers):
        """Test successful profile retrieval."""
        response = await client.get("/users/profile", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "user_id" in data

    @pytest.mark.asyncio


    async def test_get_profile_unauthorized(self, client):
        """Test profile retrieval without authentication."""
        response = await client.get("/users/profile")
        assert response.status_code == 401

    @pytest.mark.asyncio


    async def test_get_profile_invalid_token(self, client):
        """Test profile retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/users/profile", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio


    async def test_update_profile_success(self, client, auth_headers):
        """Test successful profile update."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "height_cm": 185,
            "weight_kg": 80.0,
        }

        response = await client.put("/users/profile", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["height_cm"] == 185

    @pytest.mark.asyncio


    async def test_update_profile_unauthorized(self, client):
        """Test profile update without authentication."""
        update_data = {"first_name": "Updated"}

        response = await client.put("/users/profile", json=update_data)
        assert response.status_code == 401

    @pytest.mark.asyncio


    async def test_delete_account_success(self, client, auth_headers):
        """Test successful account deletion."""
        response = await client.delete("/users/account", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio


    async def test_delete_account_unauthorized(self, client):
        """Test account deletion without authentication."""
        response = await client.delete("/users/account")
        assert response.status_code == 401


class TestUserPreferencesEndpoints:
    """Test per endpoint delle preferenze utente."""

    @pytest.mark.asyncio


    async def test_get_preferences_success(self, client, auth_headers):
        """Test successful preferences retrieval."""
        response = await client.get("/users/preferences", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "timezone" in data
        assert "language" in data
        assert "push_notifications" in data

    @pytest.mark.asyncio


    async def test_update_preferences_success(self, client, auth_headers):
        """Test successful preferences update."""
        preferences_data = {
            "timezone": "Europe/Rome",
            "language": "en",
            "push_notifications": False,
            "email_notifications": True,
        }

        response = await client.put(
            "/users/preferences", json=preferences_data, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["timezone"] == "Europe/Rome"
        assert data["language"] == "en"
        assert data["push_notifications"] is False

    @pytest.mark.asyncio


    async def test_update_preferences_invalid_timezone(self, client, auth_headers):
        """Test preferences update with invalid timezone."""
        preferences_data = {"timezone": "Invalid/Timezone"}

        response = await client.put(
            "/users/preferences", json=preferences_data, headers=auth_headers
        )
        assert response.status_code == 400


@pytest.mark.integration
class TestIntegrationScenarios:
    """Test di integrazione end-to-end."""

    @pytest.mark.asyncio


    async def test_complete_user_journey(self, client, sample_user_data):
        """Test complete user journey from registration to deletion."""
        # 1. Register
        response = await client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 201

        # 2. Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get profile
        response = await client.get("/users/profile", headers=headers)
        assert response.status_code == 200

        # 4. Update profile
        update_data = {"first_name": "Updated"}
        response = await client.put("/users/profile", json=update_data, headers=headers)
        assert response.status_code == 200

        # 5. Update preferences
        prefs_data = {"language": "en", "push_notifications": False}
        response = await client.put("/users/preferences", json=prefs_data, headers=headers)
        assert response.status_code == 200

        # 6. Delete account
        response = await client.delete("/users/account", headers=headers)
        assert response.status_code == 200

    @pytest.mark.asyncio


    async def test_multiple_users_registration(self, client):
        """Test registration of multiple users."""
        users_data = [
            {
                "email": f"user{i}@example.com",
                "password": "StrongPassword123!",
                "first_name": f"User{i}",
                "last_name": "Test",
                "date_of_birth": "1990-01-01",
                "gender": "male",
                "height_cm": 180,
                "weight_kg": 75.5,
                "activity_level": "moderately_active",
            }
            for i in range(1, 4)
        ]

        for user_data in users_data:
            response = await client.post("/auth/register", json=user_data)
            assert response.status_code == 201


@pytest.mark.slow
class TestPerformanceTests:
    """Test di performance."""

    @pytest.mark.asyncio


    async def test_concurrent_registrations(self, client):
        """Test registrazioni concorrenti."""
        import threading
        import time

        results = []

        def register_user(user_id):
            user_data = {
                "email": f"concurrent{user_id}@example.com",
                "password": "StrongPassword123!",
                "first_name": f"User{user_id}",
                "last_name": "Test",
                "date_of_birth": "1990-01-01",
                "gender": "male",
                "height_cm": 180,
                "weight_kg": 75.5,
                "activity_level": "moderately_active",
            }
            start_time = time.time()
            response = await client.post("/auth/register", json=user_data)
            end_time = time.time()

            results.append(
                {
                    "user_id": user_id,
                    "status_code": response.status_code,
                    "duration": end_time - start_time,
                }
            )

        # Create 5 concurrent registrations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all registrations were successful
        assert len(results) == 5
        for result in results:
            assert result["status_code"] == 201
            assert result["duration"] < 2.0  # Should complete within 2 seconds
