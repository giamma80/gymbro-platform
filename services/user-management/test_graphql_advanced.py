#!/usr/bin/env python3
"""Advanced GraphQL Tests for User Management Service"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
GRAPHQL_ENDPOINT = f"{BASE_URL}/graphql"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"

class GraphQLTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        
    def test_query(self, name, query, variables=None, expected_fields=None):
        """Test a GraphQL query and validate response."""
        print(f"\n🧪 Testing: {name}")
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                self.failed += 1
                return
                
            result = response.json()
            
            if "errors" in result:
                print(f"❌ GraphQL Errors: {result['errors']}")
                self.failed += 1
                return
                
            if "data" not in result:
                print(f"❌ No data in response")
                self.failed += 1
                return
                
            # Validate expected fields if provided
            if expected_fields:
                data = result["data"]
                for field in expected_fields:
                    if field not in data or data[field] is None:
                        print(f"❌ Missing field: {field}")
                        self.failed += 1
                        return
                        
            print(f"✅ Success: {json.dumps(result['data'], indent=2)[:200]}...")
            self.passed += 1
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.failed += 1
    
    def run_tests(self):
        """Run all GraphQL tests."""
        print("🚀 Advanced GraphQL Test Suite")
        print("=" * 40)
        
        # Test 1: Basic introspection
        self.test_query(
            "Schema Introspection",
            """
            {
                __schema {
                    queryType {
                        name
                    }
                }
            }
            """,
            expected_fields=["__schema"]
        )
        
        # Test 2: Query type fields
        self.test_query(
            "Query Type Fields",
            """
            {
                __type(name: "Query") {
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
            """,
            expected_fields=["__type"]
        )
        
        # Test 3: Get user by ID
        self.test_query(
            "Get User by ID",
            """
            query GetUser($id: ID!) {
                getUser(id: $id) {
                    id
                    email
                    username
                    isActive
                }
            }
            """,
            variables={"id": TEST_USER_ID},
            expected_fields=["getUser"]
        )
        
        # Test 4: List users
        self.test_query(
            "List Users",
            """
            query ListUsers {
                listUsers(limit: 5) {
                    success
                    total
                    data {
                        id
                        email
                    }
                }
            }
            """,
            expected_fields=["listUsers"]
        )
        
        # Test 5: Get user by email
        self.test_query(
            "Get User by Email",
            """
            query GetUserByEmail($email: String!) {
                getUserByEmail(email: $email) {
                    id
                    email
                    username
                }
            }
            """,
            variables={"email": "test@nutrifit.com"},
            expected_fields=["getUserByEmail"]
        )
        
        # Test 6: User service context
        self.test_query(
            "User Service Context",
            """
            query UserServiceContext($userId: ID!) {
                userServiceContext(userId: $userId) {
                    id
                    email
                    fullName
                    isActive
                }
            }
            """,
            variables={"userId": TEST_USER_ID},
            expected_fields=["userServiceContext"]
        )
        
        # Test 7: Invalid query (should handle gracefully)
        self.test_query(
            "Non-existent User",
            """
            query {
                getUser(id: "00000000-0000-0000-0000-000000000999") {
                    id
                    email
                }
            }
            """,
            expected_fields=["getUser"]  # Should return null, not error
        )
        
        # Results
        total = self.passed + self.failed
        print(f"\n📊 Test Results:")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if self.failed == 0:
            print("🎉 All GraphQL tests passed!")
        else:
            print("⚠️  Some tests failed - check GraphQL implementation")

if __name__ == "__main__":
    tester = GraphQLTester()
    tester.run_tests()
