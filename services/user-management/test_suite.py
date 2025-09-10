#!/usr/bin/env python3
"""
User Management Service - Test Suite
====================================
Comprehensive test script for user management service.
"""

import asyncio
import time
from typing import Dict, Any
from uuid import UUID
import requests

# Test Configuration
BASE_URL = "http://localhost:8001"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_EMAIL = "test@nutrifit.com"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TestRunner:
    """Test runner for user management service."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.start_time = time.time()
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result with colors."""
        self.total += 1
        if passed:
            self.passed += 1
            status = f"{Colors.GREEN}✅ PASS{Colors.END}"
        else:
            self.failed += 1
            status = f"{Colors.RED}❌ FAIL{Colors.END}"
        
        print(f"{status} {test_name}")
        if details:
            print(f"     {details}")
    
    def log_section(self, section_name: str):
        """Log test section header."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}📋 {section_name}{Colors.END}")
        print("=" * len(section_name))
    
    def api_call(self, method: str, endpoint: str, 
                 data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API call."""
        try:
            url = f"{BASE_URL}{endpoint}"
            kwargs = {"timeout": 5}
            
            if data:
                kwargs["json"] = data
                kwargs["headers"] = {"Content-Type": "application/json"}
            
            response = getattr(requests, method.lower())(url, **kwargs)
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.text else None,
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            return {"status_code": 0, "error": str(e), "success": False}
    
    async def test_database_repositories(self):
        """Test database repositories."""
        self.log_section("Database Repository Tests")
        
        try:
            from app.infrastructure.repositories import (
                UserRepository, UserProfileRepository,
                PrivacySettingsRepository, UserServiceContextRepository
            )
            
            # Test repositories
            user_repo = UserRepository()
            user = await user_repo.get_by_id(UUID(TEST_USER_ID))
            self.log_test(
                "User Repository",
                user is not None and user.email == TEST_EMAIL,
                f"User: {user.email if user else 'None'}"
            )
            
            profile_repo = UserProfileRepository()
            profile = await profile_repo.get_by_user_id(UUID(TEST_USER_ID))
            self.log_test(
                "Profile Repository",
                profile is not None,
                f"Profile: {profile.display_name if profile else 'None'}"
            )
            
            privacy_repo = PrivacySettingsRepository()
            privacy = await privacy_repo.get_by_user_id(UUID(TEST_USER_ID))
            self.log_test(
                "Privacy Repository",
                privacy is not None,
                f"Consent: {privacy.consent_level if privacy else 'None'}"
            )
            
            context_repo = UserServiceContextRepository()
            context = await context_repo.get_by_user_id(UUID(TEST_USER_ID))
            self.log_test(
                "Context Repository",
                context is not None,
                f"Context: {context.email if context else 'None'}"
            )
            
        except Exception as e:
            self.log_test("Database Repository Tests", False, f"Error: {e}")
    
    def test_health_endpoints(self):
        """Test health endpoints."""
        self.log_section("Health Check Tests")
        
        result = self.api_call("GET", "/health")
        self.log_test(
            "Health Check",
            result["success"] and result["data"]["status"] == "healthy",
            f"Status: {result.get('data', {}).get('status', 'Error')}"
        )
        
        result = self.api_call("GET", "/health/ready")
        self.log_test(
            "Readiness Check",
            result["success"],
            f"Ready: {result['success']}"
        )
        
        result = self.api_call("GET", "/health/live")
        self.log_test(
            "Liveness Check",
            result["success"] and result["data"]["status"] == "alive",
            f"Status: {result.get('data', {}).get('status', 'Error')}"
        )
    
    def test_user_endpoints(self):
        """Test user endpoints."""
        self.log_section("User API Tests")
        
        # Get user by ID
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}")
        self.log_test(
            "Get User by ID",
            result["success"] and result["data"]["email"] == TEST_EMAIL,
            f"User: {result.get('data', {}).get('username', 'Not found')}"
        )
        
        # Get user by email
        result = self.api_call("GET", f"/api/v1/users/email/{TEST_EMAIL}")
        self.log_test(
            "Get User by Email",
            result["success"] and result["data"]["id"] == TEST_USER_ID,
            f"ID: {result.get('data', {}).get('id', 'Not found')}"
        )
        
        # List users
        result = self.api_call("GET", "/api/v1/users?limit=10")
        self.log_test(
            "List Users",
            result["success"] and isinstance(result.get("data"), list),
            f"Count: {len(result.get('data', []))}"
        )
        
        # Test 404
        result = self.api_call("GET", 
                              "/api/v1/users/00000000-0000-0000-0000-000000000999")
        self.log_test(
            "User Not Found (404)",
            result["status_code"] == 404,
            "Correctly returns 404"
        )
    
    def test_profile_endpoints(self):
        """Test profile endpoints."""
        self.log_section("Profile API Tests")
        
        # Get profile
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}/profile")
        self.log_test(
            "Get Profile",
            result["success"] and result["data"]["display_name"] == "Test User",
            f"Profile: {result.get('data', {}).get('display_name', 'None')}"
        )
        
        # Update profile
        update_data = {"display_name": "Updated Test User"}
        result = self.api_call("PUT", 
                              f"/api/v1/users/{TEST_USER_ID}/profile",
                              update_data)
        self.log_test(
            "Update Profile",
            result["success"],
            f"Updated: {result.get('data', {}).get('display_name', 'Failed')}"
        )
        
        # Restore
        restore_data = {"display_name": "Test User"}
        self.api_call("PUT", f"/api/v1/users/{TEST_USER_ID}/profile", 
                     restore_data)
    
    def test_privacy_endpoints(self):
        """Test privacy endpoints."""
        self.log_section("Privacy API Tests")
        
        # Get privacy
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}/privacy")
        self.log_test(
            "Get Privacy Settings",
            result["success"] and result["data"]["has_basic_consent"],
            f"Consent: {result.get('data', {}).get('consent_level', 'None')}"
        )
        
        # Update privacy
        update_data = {"marketing_consent": True}
        result = self.api_call("PUT", 
                              f"/api/v1/users/{TEST_USER_ID}/privacy",
                              update_data)
        self.log_test(
            "Update Privacy",
            result["success"],
            f"Updated: {result.get('data', {}).get('marketing_consent', False)}"
        )
    
    def test_context_endpoints(self):
        """Test context endpoints."""
        self.log_section("Context API Tests")
        
        # Get context
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}/context")
        self.log_test(
            "Get Service Context",
            result["success"] and result["data"]["user_id"] == TEST_USER_ID,
            f"Context: {result.get('data', {}).get('full_name', 'None')}"
        )
        
        # List active contexts
        result = self.api_call("GET", "/api/v1/users/context/active?limit=5")
        self.log_test(
            "List Active Contexts",
            result["success"] and isinstance(result.get("data"), list),
            f"Active: {len(result.get('data', []))}"
        )
    
    def test_user_actions(self):
        """Test user actions."""
        self.log_section("User Action Tests")
        
        # Verify email
        result = self.api_call("POST", 
                              f"/api/v1/users/{TEST_USER_ID}/verify-email")
        self.log_test(
            "Verify Email",
            result["success"],
            f"Message: {result.get('data', {}).get('message', 'None')}"
        )
        
        # Record login
        result = self.api_call("POST", f"/api/v1/users/{TEST_USER_ID}/login")
        self.log_test(
            "Record Login",
            result["success"],
            f"Login: {result.get('data', {}).get('last_login', 'None')}"
        )
    
    def generate_summary(self):
        """Generate test summary."""
        duration = time.time() - self.start_time
        
        print(f"\n{Colors.PURPLE}{Colors.BOLD}📊 Test Summary{Colors.END}")
        print("=" * 20)
        print(f"Total: {Colors.BOLD}{self.total}{Colors.END}")
        print(f"Passed: {Colors.GREEN}{self.passed}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.failed}{Colors.END}")
        success_rate = (self.passed/self.total*100) if self.total > 0 else 0
        print(f"Success: {Colors.CYAN}{success_rate:.1f}%{Colors.END}")
        print(f"Duration: {Colors.YELLOW}{duration:.2f}s{Colors.END}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  {self.failed} failed{Colors.END}")
        
        return self.failed == 0
    
    async def run_all_tests(self):
        """Run complete test suite."""
        print(f"{Colors.BOLD}🧪 User Management Service Test Suite{Colors.END}")
        print("=" * 50)
        print(f"Service: user-management")
        print(f"Base URL: {BASE_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("")
        
        # Run all tests
        await self.test_database_repositories()
        self.test_health_endpoints()
        self.test_user_endpoints()
        self.test_profile_endpoints()
        self.test_privacy_endpoints()
        self.test_context_endpoints()
        self.test_user_actions()
        
        return self.generate_summary()


async def main():
    """Main test function."""
    tests = TestRunner()
    success = await tests.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
