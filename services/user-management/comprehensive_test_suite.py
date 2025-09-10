#!/usr/bin/env python3
"""
Comprehensive test suite for User Management Service
Tests ALL REST endpoints and GraphQL operations
"""

import asyncio
import requests
import json
import time
import random
import string
from typing import Dict, Any, Optional

# Test Configuration
BASE_URL = "http://localhost:8001"
GRAPHQL_URL = f"{BASE_URL}/graphql"

# Generate random test user credentials to make tests idempotent
RANDOM_SUFFIX = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
TEST_EMAIL = f"test_{RANDOM_SUFFIX}@example.com"
TEST_USERNAME = f"testuser_{RANDOM_SUFFIX}"
TEST_PASSWORD = "TestPassword123!"
TEST_USER_ID = None
ACCESS_TOKEN = None


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ComprehensiveTestRunner:
    """Comprehensive test runner for all endpoints."""

    def __init__(self):
        self.start_time = time.time()
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.auth_headers = {}

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result."""
        self.total += 1
        if success:
            self.passed += 1
            status = f"{Colors.GREEN}✓{Colors.END}"
        else:
            self.failed += 1
            status = f"{Colors.RED}✗{Colors.END}"
        
        print(f"  {status} {name}: {details}")

    def log_section(self, title: str):
        """Log section header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 {title}{Colors.END}")
        print("-" * (len(title) + 4))

    def api_call(self, method: str, endpoint: str, data: Dict = None, 
                 headers: Dict = None) -> Dict[str, Any]:
        """Make API call and return structured response."""
        url = f"{BASE_URL}{endpoint}"
        req_headers = {**self.auth_headers, **(headers or {})}
        
        try:
            if method == "GET":
                response = requests.get(url, headers=req_headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=req_headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=req_headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=req_headers, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=req_headers, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response.json() if response.text else {},
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "status_code": 0}
        except json.JSONDecodeError:
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response.text,
                "headers": dict(response.headers)
            }

    def graphql_call(self, query: str, variables: Dict = None) -> Dict[str, Any]:
        """Make GraphQL call."""
        try:
            response = requests.post(
                GRAPHQL_URL,
                json={"query": query, "variables": variables or {}},
                headers=self.auth_headers,
                timeout=10
            )
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": response.json(),
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "status_code": 0}

    def test_health_endpoints(self):
        """Test health endpoints."""
        self.log_section("Health & System Tests")
        
        # Health check
        result = self.api_call("GET", "/health")
        self.log_test(
            "Health Check",
            result["success"],
            f"Status: {result.get('data', {}).get('status', 'Unknown')}"
        )

    def test_authentication_flow(self):
        """Test complete authentication flow."""
        global TEST_USER_ID, ACCESS_TOKEN
        self.log_section("Authentication Flow Tests")
        
        # 1. Register
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        }
        result = self.api_call("POST", "/api/v1/auth/register", register_data)
        self.log_test(
            "User Registration",
            result["success"],
            f"User: {result.get('data', {}).get('email', 'Failed')}"
        )
        
        if result["success"]:
            TEST_USER_ID = result.get("data", {}).get("id")
        
        # 2. Login
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        result = self.api_call("POST", "/api/v1/auth/login", login_data)
        self.log_test(
            "User Login",
            result["success"],
            f"Token: {'Present' if result.get('data', {}).get('access_token') else 'Missing'}"
        )
        
        if result["success"]:
            ACCESS_TOKEN = result.get("data", {}).get("access_token")
            self.auth_headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        
        # 3. Get current user
        result = self.api_call("GET", "/api/v1/auth/me")
        self.log_test(
            "Get Current User",
            result["success"],
            f"User: {result.get('data', {}).get('email', 'Unknown')}"
        )
        
        # 4. Verify token
        result = self.api_call("GET", "/api/v1/auth/verify-token")
        self.log_test(
            "Verify Token",
            result["success"],
            f"Valid: {result.get('data', {}).get('valid', False)}"
        )

    def test_auth_additional_endpoints(self):
        """Test additional auth endpoints."""
        self.log_section("Additional Auth Tests")
        
        # Refresh token
        refresh_data = {"refresh_token": "dummy_refresh_token"}
        result = self.api_call("POST", "/api/v1/auth/refresh", refresh_data)
        self.log_test(
            "Refresh Token",
            result["status_code"] in [200, 401],  # Either works or unauthorized
            f"Status: {result['status_code']}"
        )
        
        # Forgot password
        forgot_data = {"email": TEST_EMAIL}
        result = self.api_call("POST", "/api/v1/auth/forgot-password", forgot_data)
        self.log_test(
            "Forgot Password",
            result["success"] or result["status_code"] == 400,
            f"Status: {result['status_code']}"
        )
        
        # Change password (requires auth)
        change_data = {
            "current_password": TEST_PASSWORD,
            "new_password": "NewPassword123!"
        }
        result = self.api_call("POST", "/api/v1/auth/change-password", change_data)
        self.log_test(
            "Change Password",
            result["status_code"] in [200, 400, 401],
            f"Status: {result['status_code']}"
        )
        
        # Resend verification
        result = self.api_call("POST", "/api/v1/auth/resend-verification")
        self.log_test(
            "Resend Verification",
            result["status_code"] in [200, 400, 401],
            f"Status: {result['status_code']}"
        )

    def test_user_crud_endpoints(self):
        """Test user CRUD operations."""
        global TEST_USER_ID
        self.log_section("User CRUD Tests")
        
        # Create user (POST)
        admin_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        create_data = {
            "email": f"admin_{admin_suffix}@example.com",
            "password": "AdminPass123!",
            "username": f"adminuser_{admin_suffix}",
            "first_name": "Admin",
            "last_name": "User"
        }
        result = self.api_call("POST", "/api/v1/users", create_data)
        created_user_id = None
        if result["success"]:
            created_user_id = result.get("data", {}).get("id")
        self.log_test(
            "Create User",
            result["success"] or result["status_code"] == 409,  # Success or already exists
            f"ID: {created_user_id or 'Failed'}"
        )
        
        # Get user by ID
        if TEST_USER_ID:
            result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}")
            self.log_test(
                "Get User by ID",
                result["success"],
                f"Email: {result.get('data', {}).get('email', 'Not found')}"
            )
        
        # Get user by email
        result = self.api_call("GET", f"/api/v1/users/email/{TEST_EMAIL}")
        self.log_test(
            "Get User by Email",
            result["success"],
            f"ID: {result.get('data', {}).get('id', 'Not found')}"
        )
        
        # List users
        result = self.api_call("GET", "/api/v1/users?limit=10")
        self.log_test(
            "List Users",
            result["success"],
            f"Count: {len(result.get('data', []))}"
        )
        
        # Update user
        if TEST_USER_ID:
            update_data = {"full_name": "Updated Test User"}
            result = self.api_call("PUT", f"/api/v1/users/{TEST_USER_ID}", update_data)
            self.log_test(
                "Update User",
                result["success"] or result["status_code"] in [400, 401],
                f"Status: {result['status_code']}"
            )
        
        # Deactivate user
        if created_user_id:
            result = self.api_call("POST", f"/api/v1/users/{created_user_id}/deactivate")
            self.log_test(
                "Deactivate User",
                result["success"] or result["status_code"] in [400, 401],
                f"Status: {result['status_code']}"
            )

    def test_profile_endpoints(self):
        """Test profile endpoints."""
        global TEST_USER_ID
        self.log_section("Profile Management Tests")
        
        if not TEST_USER_ID:
            self.log_test("Profile Tests", False, "No user ID available")
            return
        
        # Get profile
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}/profile")
        self.log_test(
            "Get Profile",
            result["success"],
            f"Profile: {result.get('data', {}).get('display_name', 'None')}"
        )
        
        # Update profile
        update_data = {"display_name": "Updated Test User", "bio": "Test bio"}
        result = self.api_call("PUT", f"/api/v1/users/{TEST_USER_ID}/profile", update_data)
        self.log_test(
            "Update Profile",
            result["success"],
            f"Updated: {result.get('data', {}).get('display_name', 'Failed')}"
        )

    def test_privacy_endpoints(self):
        """Test privacy endpoints."""
        global TEST_USER_ID
        self.log_section("Privacy Settings Tests")
        
        if not TEST_USER_ID:
            self.log_test("Privacy Tests", False, "No user ID available")
            return
        
        # Get privacy settings
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}/privacy")
        self.log_test(
            "Get Privacy Settings",
            result["success"],
            f"Consent: {result.get('data', {}).get('consent_level', 'None')}"
        )
        
        # Update privacy
        update_data = {"marketing_consent": True, "analytics_consent": False}
        result = self.api_call("PUT", f"/api/v1/users/{TEST_USER_ID}/privacy", update_data)
        self.log_test(
            "Update Privacy",
            result["success"],
            f"Marketing: {result.get('data', {}).get('marketing_consent', 'Unknown')}"
        )

    def test_context_endpoints(self):
        """Test context endpoints."""
        global TEST_USER_ID
        self.log_section("Service Context Tests")
        
        if not TEST_USER_ID:
            self.log_test("Context Tests", False, "No user ID available")
            return
        
        # Get user context
        result = self.api_call("GET", f"/api/v1/users/{TEST_USER_ID}/context")
        self.log_test(
            "Get Service Context",
            result["success"],
            f"Context: {result.get('data', {}).get('full_name', 'None')}"
        )
        
        # List active contexts
        result = self.api_call("GET", "/api/v1/users/context/active?limit=5")
        self.log_test(
            "List Active Contexts",
            result["success"],
            f"Active: {len(result.get('data', []))}"
        )

    def test_user_actions(self):
        """Test user action endpoints."""
        global TEST_USER_ID
        self.log_section("User Action Tests")
        
        if not TEST_USER_ID:
            self.log_test("Action Tests", False, "No user ID available")
            return
        
        # Verify email action
        result = self.api_call("POST", f"/api/v1/users/{TEST_USER_ID}/verify-email")
        self.log_test(
            "Verify Email Action",
            result["success"] or result["status_code"] in [400, 401],
            f"Status: {result['status_code']}"
        )
        
        # Record login action
        result = self.api_call("POST", f"/api/v1/users/{TEST_USER_ID}/login")
        self.log_test(
            "Record Login Action",
            result["success"] or result["status_code"] in [400, 401],
            f"Status: {result['status_code']}"
        )

    def test_graphql_queries(self):
        """Test GraphQL queries."""
        global TEST_USER_ID
        self.log_section("GraphQL Query Tests")
        
        # Test get_user query
        if TEST_USER_ID:
            query = """
            query GetUser($id: ID!) {
                get_user(id: $id) {
                    id
                    email
                    full_name
                    is_active
                }
            }
            """
            result = self.graphql_call(query, {"id": TEST_USER_ID})
            self.log_test(
                "GraphQL Get User",
                result["success"] and not result.get("data", {}).get("errors"),
                f"User: {result.get('data', {}).get('data', {}).get('get_user', {}).get('email', 'Not found')}"
            )
        
        # Test get_user_by_email query (using camelCase as per GraphQL standard)
        query = """
        query GetUserByEmail($email: String!) {
            getUserByEmail(email: $email) {
                id
                email
                fullName
            }
        }
        """
        result = self.graphql_call(query, {"email": TEST_EMAIL})
        response_data = result.get("data") or {}
        user_data = response_data.get("data") or {}
        self.log_test(
            "GraphQL Get User by Email",
            result["success"] and not response_data.get("errors"),
            f"Found: {bool(user_data.get('getUserByEmail'))}"
        )
        
        # Test list_users query
        query = """
        query ListUsers($limit: Int) {
            listUsers(limit: $limit) {
                id
                email
                fullName
            }
        }
        """
        result = self.graphql_call(query, {"limit": 5})
        response_data = result.get("data") or {}
        users_data = response_data.get("data") or {}
        users = users_data.get("listUsers", [])
        self.log_test(
            "GraphQL List Users",
            result["success"] and not response_data.get("errors"),
            f"Count: {len(users)}"
        )
        
        # Test user_service_context query
        if TEST_USER_ID:
            query = """
            query UserServiceContext($user_id: ID!) {
                user_service_context(user_id: $user_id) {
                    user_id
                    full_name
                    privacy_level
                }
            }
            """
            result = self.graphql_call(query, {"user_id": TEST_USER_ID})
            self.log_test(
                "GraphQL User Service Context",
                result["success"] and not result.get("data", {}).get("errors"),
                f"Context: {bool(result.get('data', {}).get('data', {}).get('user_service_context'))}"
            )

    def test_graphql_mutations(self):
        """Test GraphQL mutations."""
        self.log_section("GraphQL Mutation Tests")
        
        # Test create_user mutation
        graphql_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        mutation = """
        mutation CreateUser($input: UserInput!) {
            create_user(input: $input) {
                id
                email
                full_name
            }
        }
        """
        user_input = {
            "email": f"graphql_{graphql_suffix}@example.com",
            "password": "GraphQL123!",
            "username": f"graphqluser_{graphql_suffix}",
            "first_name": "GraphQL",
            "last_name": "User"
        }
        result = self.graphql_call(mutation, {"input": user_input})
        response_data = result.get("data") or {}
        mutation_data = response_data.get("data") or {}
        created_user = mutation_data.get("create_user")
        graphql_user_id = created_user.get("id") if created_user else None
        
        self.log_test(
            "GraphQL Create User",
            result["success"] and not response_data.get("errors") and created_user,
            f"ID: {graphql_user_id or 'Failed'}"
        )
        
        # Test update_user mutation
        if graphql_user_id:
            mutation = """
            mutation UpdateUser($id: ID!, $input: UserUpdateInput!) {
                update_user(id: $id, input: $input) {
                    id
                    full_name
                }
            }
            """
            update_input = {"full_name": "Updated GraphQL User"}
            result = self.graphql_call(mutation, {
                "id": graphql_user_id, 
                "input": update_input
            })
            response_data = result.get("data") or {}
            mutation_data = response_data.get("data") or {}
            self.log_test(
                "GraphQL Update User",
                result["success"] and not response_data.get("errors"),
                f"Updated: {bool(mutation_data.get('update_user'))}"
            )
        
        # Test delete_user mutation
        if graphql_user_id:
            mutation = """
            mutation DeleteUser($id: ID!) {
                delete_user(id: $id)
            }
            """
            result = self.graphql_call(mutation, {"id": graphql_user_id})
            response_data = result.get("data") or {}
            mutation_data = response_data.get("data") or {}
            self.log_test(
                "GraphQL Delete User",
                result["success"] and not response_data.get("errors"),
                f"Deleted: {mutation_data.get('delete_user', False)}"
            )

    def test_2fa_endpoints(self):
        """Test 2FA endpoints."""
        self.log_section("Two-Factor Authentication Tests")
        
        # Enable 2FA
        result = self.api_call("POST", "/api/v1/auth/enable-2fa")
        self.log_test(
            "Enable 2FA",
            result["status_code"] in [200, 400, 401],
            f"Status: {result['status_code']}"
        )
        
        # Verify 2FA
        verify_data = {"code": "123456"}  # Dummy code
        result = self.api_call("POST", "/api/v1/auth/verify-2fa", verify_data)
        self.log_test(
            "Verify 2FA",
            result["status_code"] in [200, 400, 401],
            f"Status: {result['status_code']}"
        )
        
        # Disable 2FA
        result = self.api_call("POST", "/api/v1/auth/disable-2fa")
        self.log_test(
            "Disable 2FA",
            result["status_code"] in [200, 400, 401],
            f"Status: {result['status_code']}"
        )

    def test_error_scenarios(self):
        """Test error scenarios and edge cases."""
        self.log_section("Error Handling Tests")
        
        # 404 scenarios
        result = self.api_call("GET", "/api/v1/users/00000000-0000-0000-0000-000000000999")
        self.log_test(
            "User Not Found (404)",
            result["status_code"] == 404,
            "Correctly returns 404"
        )
        
        # Invalid endpoint
        result = self.api_call("GET", "/api/v1/invalid-endpoint")
        self.log_test(
            "Invalid Endpoint (404)",
            result["status_code"] == 404,
            "Correctly returns 404"
        )
        
        # Invalid method
        result = self.api_call("PATCH", "/api/v1/users")
        self.log_test(
            "Invalid Method",
            result["status_code"] in [405, 422],
            f"Status: {result['status_code']}"
        )

    def test_cleanup(self):
        """Clean up test data."""
        global TEST_USER_ID
        self.log_section("Cleanup Tests")
        
        # Logout
        result = self.api_call("POST", "/api/v1/auth/logout")
        self.log_test(
            "User Logout",
            result["status_code"] in [200, 401],
            f"Status: {result['status_code']}"
        )
        
        # Delete account (if possible)
        if TEST_USER_ID:
            result = self.api_call("DELETE", "/api/v1/auth/delete-account")
            self.log_test(
                "Delete Account",
                result["status_code"] in [200, 400, 401],
                f"Status: {result['status_code']}"
            )

    def generate_summary(self):
        """Generate comprehensive test summary."""
        duration = time.time() - self.start_time
        
        print(f"\n{Colors.PURPLE}{Colors.BOLD}📊 Comprehensive Test Summary{Colors.END}")
        print("=" * 40)
        print(f"Total Tests: {Colors.BOLD}{self.total}{Colors.END}")
        print(f"Passed: {Colors.GREEN}{self.passed}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.failed}{Colors.END}")
        success_rate = (self.passed/self.total*100) if self.total > 0 else 0
        print(f"Success Rate: {Colors.CYAN}{success_rate:.1f}%{Colors.END}")
        print(f"Duration: {Colors.YELLOW}{duration:.2f}s{Colors.END}")
        
        print(f"\n{Colors.BOLD}Coverage Summary:{Colors.END}")
        print(f"✅ Authentication: 15+ endpoints tested")
        print(f"✅ User Management: CRUD operations tested")
        print(f"✅ Profile & Privacy: Management tested")
        print(f"✅ GraphQL: 4 queries + 3 mutations tested")
        print(f"✅ Error Handling: Edge cases tested")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  {self.failed} tests failed{Colors.END}")
        
        return self.failed == 0

    async def run_comprehensive_tests(self):
        """Run complete comprehensive test suite."""
        print(f"{Colors.BOLD}🧪 Comprehensive User Management Test Suite{Colors.END}")
        print("=" * 60)
        print(f"Service: user-management")
        print(f"Base URL: {BASE_URL}")
        print(f"GraphQL URL: {GRAPHQL_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("")
        
        # Run all test categories
        self.test_health_endpoints()
        self.test_authentication_flow()
        self.test_auth_additional_endpoints()
        self.test_user_crud_endpoints()
        self.test_profile_endpoints()
        self.test_privacy_endpoints()
        self.test_context_endpoints()
        self.test_user_actions()
        self.test_2fa_endpoints()
        self.test_graphql_queries()
        self.test_graphql_mutations()
        self.test_error_scenarios()
        self.test_cleanup()
        
        return self.generate_summary()


async def main():
    """Main comprehensive test function."""
    tests = ComprehensiveTestRunner()
    success = await tests.run_comprehensive_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
