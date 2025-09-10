#!/usr/bin/env python3
"""
GraphQL Test Suite for User Management Service
==============================================
Comprehensive tests for GraphQL endpoints including queries, mutations,
and federation features.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
import requests
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:8001"
GRAPHQL_ENDPOINT = f"{BASE_URL}/graphql"
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


class GraphQLTestRunner:
    """GraphQL test runner for user management service."""
    
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
    
    def log_info(self, message: str):
        """Log informational message."""
        print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")
    
    def graphql_query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute GraphQL query."""
        try:
            payload = {"query": query}
            if variables:
                payload["variables"] = variables
            
            response = requests.post(
                GRAPHQL_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            result = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.text else None
            }
            
            # Check for GraphQL errors
            if result["data"] and "errors" in result["data"]:
                result["success"] = False
                result["errors"] = result["data"]["errors"]
            
            return result
            
        except Exception as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def test_graphql_introspection(self):
        """Test GraphQL schema introspection."""
        self.log_section("GraphQL Schema Introspection")
        
        # Test basic introspection
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
        """
        
        result = self.graphql_query(introspection_query)
        self.log_test(
            "Schema Introspection",
            result["success"] and "data" in result["data"],
            f"Found {len(result.get('data', {}).get('data', {}).get('__schema', {}).get('types', []))} types"
        )
        
        # Test Query type introspection
        query_introspection = """
        query QueryIntrospection {
            __type(name: "Query") {
                name
                fields {
                    name
                    type {
                        name
                    }
                }
            }
        }
        """
        
        result = self.graphql_query(query_introspection)
        fields = result.get("data", {}).get("data", {}).get("__type", {}).get("fields", [])
        field_names = [f["name"] for f in fields] if fields else []
        
        self.log_test(
            "Query Type Introspection",
            result["success"] and "getUser" in field_names,
            f"Available fields: {', '.join(field_names[:5])}..."
        )
    
    def test_user_queries(self):
        """Test user-related GraphQL queries."""
        self.log_section("User GraphQL Queries")
        
        # Test get user by ID
        get_user_query = """
        query GetUser($id: ID!) {
            getUser(id: $id) {
                id
                email
                username
                fullName
                isActive
                createdAt
            }
        }
        """
        
        result = self.graphql_query(get_user_query, {"id": TEST_USER_ID})
        user_data = result.get("data", {}).get("data", {}).get("getUser")
        
        self.log_test(
            "Get User by ID",
            result["success"] and user_data is not None,
            f"User: {user_data.get('email') if user_data else 'Not found'}"
        )
        
        # Test get user by email
        get_user_by_email_query = """
        query GetUserByEmail($email: String!) {
            getUserByEmail(email: $email) {
                id
                email
                username
                fullName
                isActive
            }
        }
        """
        
        result = self.graphql_query(get_user_by_email_query, {"email": TEST_EMAIL})
        user_data = result.get("data", {}).get("data", {}).get("getUserByEmail")
        
        self.log_test(
            "Get User by Email",
            result["success"] and user_data is not None,
            f"Found user: {user_data.get('username') if user_data else 'None'}"
        )
        
        # Test list users
        list_users_query = """
        query ListUsers($limit: Int, $offset: Int, $isActive: Boolean) {
            listUsers(limit: $limit, offset: $offset, isActive: $isActive) {
                success
                message
                total
                data {
                    id
                    email
                    username
                    isActive
                }
            }
        }
        """
        
        result = self.graphql_query(list_users_query, {
            "limit": 5,
            "offset": 0,
            "isActive": True
        })
        list_data = result.get("data", {}).get("data", {}).get("listUsers")
        
        self.log_test(
            "List Users",
            result["success"] and list_data and list_data.get("success"),
            f"Found {list_data.get('total', 0)} users, showing {len(list_data.get('data', []))}"
        )
        
        # Test user service context (for Federation)
        context_query = """
        query UserServiceContext($userId: ID!) {
            userServiceContext(userId: $userId) {
                id
                email
                username
                fullName
                isActive
                createdAt
                updatedAt
            }
        }
        """
        
        result = self.graphql_query(context_query, {"userId": TEST_USER_ID})
        context_data = result.get("data", {}).get("data", {}).get("userServiceContext")
        
        self.log_test(
            "User Service Context (Federation)",
            result["success"] and context_data is not None,
            f"Context: {context_data.get('fullName') if context_data else 'None'}"
        )
    
    def test_graphql_errors(self):
        """Test GraphQL error handling."""
        self.log_section("GraphQL Error Handling")
        
        # Test invalid query syntax
        invalid_query = """
        query InvalidQuery {
            getUser(id: "invalid") {
                invalidField
            }
        }
        """
        
        result = self.graphql_query(invalid_query)
        has_errors = "errors" in result.get("data", {})
        
        self.log_test(
            "Invalid Query Syntax",
            has_errors or not result["success"],
            "Correctly handles syntax errors"
        )
        
        # Test non-existent user
        get_missing_user_query = """
        query GetMissingUser {
            getUser(id: "00000000-0000-0000-0000-000000000999") {
                id
                email
            }
        }
        """
        
        result = self.graphql_query(get_missing_user_query)
        user_data = result.get("data", {}).get("data", {}).get("getUser")
        
        self.log_test(
            "Non-existent User",
            result["success"] and user_data is None,
            "Correctly returns null for missing user"
        )
        
        # Test invalid email format
        get_invalid_email_query = """
        query GetInvalidEmail {
            getUserByEmail(email: "invalid-email") {
                id
                email
            }
        }
        """
        
        result = self.graphql_query(get_invalid_email_query)
        user_data = result.get("data", {}).get("data", {}).get("getUserByEmail")
        
        self.log_test(
            "Invalid Email Format",
            result["success"] and user_data is None,
            "Correctly handles invalid email"
        )
    
    def test_graphql_federation(self):
        """Test GraphQL Federation features."""
        self.log_section("GraphQL Federation Features")
        
        # Test Federation service metadata
        service_query = """
        query ServiceInfo {
            _service {
                sdl
            }
        }
        """
        
        result = self.graphql_query(service_query)
        service_data = result.get("data", {}).get("data", {}).get("_service")
        
        self.log_test(
            "Federation Service SDL",
            result["success"] and service_data is not None,
            f"SDL available: {bool(service_data.get('sdl')) if service_data else False}"
        )
        
        # Test entity reference resolution
        entity_query = """
        query EntityReference {
            _entities(representations: [{__typename: "UserType", id: "%s"}]) {
                ... on UserType {
                    id
                    email
                    username
                }
            }
        }
        """ % TEST_USER_ID
        
        result = self.graphql_query(entity_query)
        entities = result.get("data", {}).get("data", {}).get("_entities", [])
        
        self.log_test(
            "Entity Reference Resolution",
            result["success"] and len(entities) > 0,
            f"Resolved {len(entities)} entity reference(s)"
        )
    
    def test_graphql_performance(self):
        """Test GraphQL query performance."""
        self.log_section("GraphQL Performance Tests")
        
        # Test simple query performance
        simple_query = """
        query SimplePerformance {
            getUser(id: "%s") {
                id
                email
            }
        }
        """ % TEST_USER_ID
        
        start_time = time.time()
        result = self.graphql_query(simple_query)
        query_time = time.time() - start_time
        
        self.log_test(
            "Simple Query Performance",
            result["success"] and query_time < 1.0,
            f"Query time: {query_time:.3f}s (target: < 1.0s)"
        )
        
        # Test complex query with nested data
        complex_query = """
        query ComplexPerformance {
            listUsers(limit: 5) {
                success
                total
                data {
                    id
                    email
                    username
                    fullName
                    isActive
                    createdAt
                }
            }
        }
        """
        
        start_time = time.time()
        result = self.graphql_query(complex_query)
        query_time = time.time() - start_time
        
        self.log_test(
            "Complex Query Performance",
            result["success"] and query_time < 2.0,
            f"Query time: {query_time:.3f}s (target: < 2.0s)"
        )
    
    def test_graphiql_interface(self):
        """Test GraphiQL playground interface."""
        self.log_section("GraphiQL Interface")
        
        # Test GraphiQL endpoint availability
        try:
            response = requests.get(f"{BASE_URL}/graphql", timeout=5)
            has_graphiql = "GraphiQL" in response.text or "GraphQL Playground" in response.text
            
            self.log_test(
                "GraphiQL Interface",
                response.status_code == 200 and has_graphiql,
                f"Interface available at {BASE_URL}/graphql"
            )
        except Exception as e:
            self.log_test(
                "GraphiQL Interface",
                False,
                f"Error accessing GraphiQL: {str(e)}"
            )
    
    def generate_summary(self):
        """Generate test summary."""
        duration = time.time() - self.start_time
        
        print(f"\n{Colors.PURPLE}{Colors.BOLD}📊 GraphQL Test Summary{Colors.END}")
        print("=" * 25)
        print(f"Total: {Colors.BOLD}{self.total}{Colors.END}")
        print(f"Passed: {Colors.GREEN}{self.passed}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.failed}{Colors.END}")
        success_rate = (self.passed/self.total*100) if self.total > 0 else 0
        print(f"Success: {Colors.CYAN}{success_rate:.1f}%{Colors.END}")
        print(f"Duration: {Colors.YELLOW}{duration:.2f}s{Colors.END}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All GraphQL tests passed!{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  {self.failed} GraphQL tests failed{Colors.END}")
        
        return self.failed == 0
    
    def run_all_tests(self):
        """Run complete GraphQL test suite."""
        print(f"{Colors.BOLD}🚀 GraphQL Test Suite - User Management{Colors.END}")
        print("=" * 50)
        print(f"GraphQL Endpoint: {GRAPHQL_ENDPOINT}")
        print(f"Test User: {TEST_EMAIL} ({TEST_USER_ID})")
        print("")
        
        # Wait for service to be ready
        self.log_info("Waiting for GraphQL endpoint...")
        time.sleep(1)
        
        # Run all test suites
        self.test_graphql_introspection()
        self.test_user_queries()
        self.test_graphql_errors()
        self.test_graphql_federation()
        self.test_graphql_performance()
        self.test_graphiql_interface()
        
        return self.generate_summary()


def main():
    """Main test function."""
    tests = GraphQLTestRunner()
    success = tests.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
