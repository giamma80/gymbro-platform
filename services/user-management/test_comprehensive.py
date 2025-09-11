#!/usr/bin/env python3
"""
User Management Service - Comprehensive Test Suite
=================================================
Service: user-management
Schema: user_management
Date: 9 settembre 2025

This script runs a comprehensive test suite for the user management service,
including database connectivity, API endpoints, and data validation.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import requests
from dotenv import load_dotenv

load_dotenv()

# Test Configuration
BASE_URL = "http://localhost:8001"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_EMAIL = "test@nutrifit.com"

# Original test data values (for reset)
ORIGINAL_DATA = {
    "user_profile": {
        "display_name": "Test User",
        "first_name": "Test",
        "last_name": "User",
        "timezone": "Europe/Rome",
        "locale": "it-IT",
    },
    "privacy_settings": {
        "marketing_consent": False,
        "analytics_consent": False,
        "consent_level": "minimal",
    },
}


class TestColors:
    """ANSI color codes for test output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


class UserManagementTests:
    """Comprehensive test suite for user management service."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.start_time = time.time()

    async def reset_test_data(self):
        """Reset test user data to original values."""
        self.log_info("🔄 Resetting test data to original values...")

        try:
            # Reset user profile to original values
            profile_data = ORIGINAL_DATA["user_profile"]
            result = self.put(f"/api/v1/users/{TEST_USER_ID}/profile", profile_data)

            if result["status_code"] != 200:
                self.log_info(
                    f"⚠️  Could not reset profile: {result.get('error', 'Unknown error')}"
                )

            # Reset privacy settings to original values
            privacy_data = ORIGINAL_DATA["privacy_settings"]
            result = self.put(f"/api/v1/users/{TEST_USER_ID}/privacy", privacy_data)

            if result["status_code"] != 200:
                self.log_info(
                    f"⚠️  Could not reset privacy: {result.get('error', 'Unknown error')}"
                )

            self.log_info("✅ Test data reset completed")

        except Exception as e:
            self.log_info(f"❌ Error resetting test data: {str(e)}")

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result with colors."""
        self.total += 1
        if passed:
            self.passed += 1
            status = f"{TestColors.GREEN}✅ PASS{TestColors.END}"
        else:
            self.failed += 1
            status = f"{TestColors.RED}❌ FAIL{TestColors.END}"

        print(f"{status} {test_name}")
        if details:
            print(f"     {details}")

    def log_section(self, section_name: str):
        """Log test section header."""
        print(
            f"\n{TestColors.BLUE}{TestColors.BOLD}📋 " f"{section_name}{TestColors.END}"
        )
        print("=" * (len(section_name) + 4))

    def log_info(self, message: str):
        """Log informational message."""
        print(f"{TestColors.CYAN}ℹ️  {message}{TestColors.END}")

    def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to API."""
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            return {
                "status_code": response.status_code,
                "data": (response.json() if response.status_code == 200 else None),
                "error": (response.text if response.status_code != 200 else None),
            }
        except Exception as e:
            return {"status_code": 0, "error": str(e), "data": None}

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request to API."""
        try:
            response = requests.put(
                f"{BASE_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            return {
                "status_code": response.status_code,
                "data": (response.json() if response.status_code == 200 else None),
                "error": (response.text if response.status_code != 200 else None),
            }
        except Exception as e:
            return {"status_code": 0, "error": str(e), "data": None}

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request to API."""
        try:
            kwargs = {"timeout": 5}
            if data:
                kwargs["json"] = data
                kwargs["headers"] = {"Content-Type": "application/json"}

            response = requests.post(f"{BASE_URL}{endpoint}", **kwargs)
            return {
                "status_code": response.status_code,
                "data": (response.json() if response.status_code == 200 else None),
                "error": (response.text if response.status_code != 200 else None),
            }
        except Exception as e:
            return {"status_code": 0, "error": str(e), "data": None}

    async def test_database_repositories(self):
        """Test database repositories directly."""
        self.log_section("Database Repository Tests")

        try:
            from app.infrastructure.repositories import (
                PrivacySettingsRepository,
                UserProfileRepository,
                UserRepository,
                UserServiceContextRepository,
            )

            # Test User Repository
            user_repo = UserRepository()
            user = await user_repo.get_by_id(UUID(TEST_USER_ID))
            self.log_test(
                "User Repository - Get by ID",
                user is not None and user.email == TEST_EMAIL,
                f"Found user: {user.email if user else 'None'}",
            )

            user_by_email = await user_repo.get_by_email(TEST_EMAIL)
            self.log_test(
                "User Repository - Get by Email",
                user_by_email is not None and str(user_by_email.id) == TEST_USER_ID,
                f"Found user: {user_by_email.username if user_by_email else 'None'}",
            )

            # Test User Profile Repository
            profile_repo = UserProfileRepository()
            profile = await profile_repo.get_by_user_id(UUID(TEST_USER_ID))
            self.log_test(
                "User Profile Repository - Get by User ID",
                profile is not None and profile.display_name == "Test User",
                f"Found profile: {profile.display_name if profile else 'None'}",
            )

            # Test Privacy Settings Repository
            privacy_repo = PrivacySettingsRepository()
            privacy = await privacy_repo.get_by_user_id(UUID(TEST_USER_ID))
            self.log_test(
                "Privacy Settings Repository - Get by User ID",
                privacy is not None and privacy.has_basic_consent,
                f"Consent level: {privacy.consent_level if privacy else 'None'}",
            )

            # Test Service Context Repository
            context_repo = UserServiceContextRepository()
            context = await context_repo.get_by_user_id(UUID(TEST_USER_ID))
            self.log_test(
                "Service Context Repository - Get by User ID",
                context is not None and context.email == TEST_EMAIL,
                f"Found context: {context.full_name if context else 'None'}",
            )

        except Exception as e:
            self.log_test("Database Repository Tests", False, f"Error: {str(e)}")

    def test_health_endpoints(self):
        """Test health check endpoints."""
        self.log_section("Health Check Tests")

        # Test basic health
        result = self.get("/health")
        self.log_test(
            "Basic Health Check",
            result["status_code"] == 200 and result["data"]["status"] == "healthy",
            f"Status: {result['data']['status'] if result['data'] else 'Error'}",
        )

        # Test readiness check
        result = self.get("/health/ready")
        self.log_test(
            "Readiness Check",
            result["status_code"] == 200,
            f"Database: {result['data']['checks']['supabase'] if result['data'] and 'checks' in result['data'] else 'Unknown'}",
        )

        # Test liveness check
        result = self.get("/health/live")
        self.log_test(
            "Liveness Check",
            result["status_code"] == 200 and result["data"]["status"] == "alive",
            f"Status: {result['data']['status'] if result['data'] else 'Error'}",
        )

    def test_user_endpoints(self):
        """Test user-related endpoints."""
        self.log_section("User API Tests")

        # Test get user by ID
        result = self.get(f"/api/v1/users/{TEST_USER_ID}")
        self.log_test(
            "Get User by ID",
            result["status_code"] == 200 and result["data"]["email"] == TEST_EMAIL,
            f"User: {result['data']['username'] if result['data'] else 'Not found'}",
        )

        # Test get user by email
        result = self.get(f"/api/v1/users/email/{TEST_EMAIL}")
        self.log_test(
            "Get User by Email",
            result["status_code"] == 200 and result["data"]["id"] == TEST_USER_ID,
            f"User ID: {result['data']['id'] if result['data'] else 'Not found'}",
        )

        # Test list users
        result = self.get("/api/v1/users?limit=10")
        self.log_test(
            "List Users",
            result["status_code"] == 200 and isinstance(result["data"], list),
            f"Found {len(result['data']) if result['data'] else 0} users",
        )

        # Test user not found
        result = self.get("/api/v1/users/00000000-0000-0000-0000-000000000999")
        self.log_test(
            "User Not Found (404)",
            result["status_code"] == 404,
            "Correctly returns 404 for non-existent user",
        )

    def test_profile_endpoints(self):
        """Test user profile endpoints."""
        self.log_section("User Profile API Tests")

        # Test get user profile
        result = self.get(f"/api/v1/users/{TEST_USER_ID}/profile")
        self.log_test(
            "Get User Profile",
            result["status_code"] == 200
            and result["data"]["display_name"] == "Test User",
            f"Profile: {result['data']['full_name'] if result['data'] else 'Not found'}",
        )

        # Test update user profile
        update_data = {"display_name": "Updated Test User", "timezone": "Europe/Paris"}
        result = self.put(f"/api/v1/users/{TEST_USER_ID}/profile", update_data)
        self.log_test(
            "Update User Profile",
            result["status_code"] == 200
            and result["data"]["display_name"] == "Updated Test User",
            f"Updated profile: {result['data']['display_name'] if result['data'] else 'Update failed'}",
        )

        # Restore original profile
        restore_data = {"display_name": "Test User", "timezone": "Europe/Rome"}
        self.put(f"/api/v1/users/{TEST_USER_ID}/profile", restore_data)

    def test_privacy_endpoints(self):
        """Test privacy settings endpoints."""
        self.log_section("Privacy Settings API Tests")

        # Test get privacy settings
        result = self.get(f"/api/v1/users/{TEST_USER_ID}/privacy")
        self.log_test(
            "Get Privacy Settings",
            result["status_code"] == 200 and result["data"]["has_basic_consent"],
            f"Consent level: {result['data']['consent_level'] if result['data'] else 'Not found'}",
        )

        # Test update privacy settings
        update_data = {"marketing_consent": True, "profile_visibility": True}
        result = self.put(f"/api/v1/users/{TEST_USER_ID}/privacy", update_data)
        self.log_test(
            "Update Privacy Settings",
            result["status_code"] == 200 and result["data"]["marketing_consent"],
            f"Marketing consent: {result['data']['marketing_consent'] if result['data'] else 'Update failed'}",
        )

        # Restore original settings
        restore_data = {"marketing_consent": False, "profile_visibility": False}
        self.put(f"/api/v1/users/{TEST_USER_ID}/privacy", restore_data)

    def test_service_context_endpoints(self):
        """Test service context endpoints for GraphQL Federation."""
        self.log_section("Service Context API Tests")

        # Test get user service context
        result = self.get(f"/api/v1/users/{TEST_USER_ID}/context")
        self.log_test(
            "Get User Service Context",
            result["status_code"] == 200 and result["data"]["user_id"] == TEST_USER_ID,
            f"Context: {result['data']['full_name'] if result['data'] else 'Not found'}",
        )

        # Test list active contexts
        result = self.get("/api/v1/users/context/active?limit=5")
        self.log_test(
            "List Active User Contexts",
            result["status_code"] == 200 and isinstance(result["data"], list),
            f"Found {len(result['data']) if result['data'] else 0} active contexts",
        )

    def test_user_actions(self):
        """Test user action endpoints."""
        self.log_section("User Action API Tests")

        # Test verify email (already verified)
        result = self.post(f"/api/v1/users/{TEST_USER_ID}/verify-email")
        self.log_test(
            "Verify Email (Already Verified)",
            result["status_code"] == 200
            and "already verified" in result["data"]["message"].lower(),
            f"Message: {result['data']['message'] if result['data'] else 'No response'}",
        )

        # Test record login
        result = self.post(f"/api/v1/users/{TEST_USER_ID}/login")
        self.log_test(
            "Record User Login",
            result["status_code"] == 200
            and "login recorded" in result["data"]["message"].lower(),
            f"Last login: {result['data']['last_login'] if result['data'] and result['data']['last_login'] else 'Not recorded'}",
        )

    def test_data_validation(self):
        """Test data validation and constraints."""
        self.log_section("Data Validation Tests")

        # Test profile age validation (should fail for too young user)
        invalid_data = {"date_of_birth": "2020-01-01"}  # Too young (< 13 years)
        result = self.put(f"/api/v1/users/{TEST_USER_ID}/profile", invalid_data)
        self.log_test(
            "Age Validation (< 13 years)",
            result["status_code"] == 422,  # Validation error
            "Correctly rejects users under 13 years old",
        )

        # Test invalid email format
        result = self.get("/api/v1/users/email/invalid-email")
        self.log_test(
            "Invalid Email Format",
            result["status_code"] in [404, 422],  # Not found or validation error
            "Correctly handles invalid email format",
        )

    def generate_summary(self):
        """Generate test summary."""
        duration = time.time() - self.start_time

        print(f"\n{TestColors.PURPLE}{TestColors.BOLD}📊 Test Summary{TestColors.END}")
        print("=" * 20)
        print(f"Total Tests: {TestColors.BOLD}{self.total}{TestColors.END}")
        print(f"Passed: {TestColors.GREEN}{self.passed}{TestColors.END}")
        print(f"Failed: {TestColors.RED}{self.failed}{TestColors.END}")
        print(
            f"Success Rate: {TestColors.CYAN}{(self.passed/self.total*100):.1f}%{TestColors.END}"
        )
        print(f"Duration: {TestColors.YELLOW}{duration:.2f} seconds{TestColors.END}")

        if self.failed == 0:
            print(
                f"\n{TestColors.GREEN}{TestColors.BOLD}🎉 All tests passed! Service is ready for production.{TestColors.END}"
            )
        else:
            print(
                f"\n{TestColors.RED}{TestColors.BOLD}⚠️  {self.failed} test(s) failed. Please review the issues above.{TestColors.END}"
            )

        return self.failed == 0

    async def run_all_tests(self):
        """Run the complete test suite."""
        print(f"{TestColors.BOLD}{TestColors.WHITE}")
        print("🧪 User Management Service - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Service: user-management")
        print(f"Schema: user_management")
        print(f"Base URL: {BASE_URL}")
        print(f"Test User: {TEST_EMAIL} ({TEST_USER_ID})")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{TestColors.END}")

        # Wait for service to be ready
        self.log_info("Waiting for service to be ready...")
        time.sleep(2)

        # Reset test data to ensure clean state
        await self.reset_test_data()

        # Run database tests
        await self.test_database_repositories()

        # Run API tests
        self.test_health_endpoints()
        self.test_user_endpoints()
        self.test_profile_endpoints()
        self.test_privacy_endpoints()
        self.test_service_context_endpoints()
        self.test_user_actions()
        self.test_data_validation()

        # Generate summary
        return self.generate_summary()


async def main():
    """Main test execution function."""
    tests = UserManagementTests()
    success = await tests.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
