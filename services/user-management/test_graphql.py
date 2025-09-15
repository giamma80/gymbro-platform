#!/usr/bin/env python3
"""
GraphQL Endpoint Tests - User Management Service
Tests specifically for GraphQL functionality
"""

import requests

# Test Configuration
BASE_URL = "http://localhost:8001"
GRAPHQL_URL = f"{BASE_URL}/graphql"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"


def test_graphql_schema_introspection():
    """Test GraphQL schema introspection query."""
    print("🔍 Testing GraphQL Schema Introspection...")
    
    query = {
        "query": """
        {
            __schema {
                queryType {
                    name
                }
                mutationType {
                    name
                }
            }
        }
        """
    }
    
    try:
        response = requests.post(GRAPHQL_URL, json=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and '__schema' in data['data']:
                print("✅ GraphQL Schema Introspection - SUCCESS")
                return True
            else:
                print("❌ GraphQL Schema Introspection - Invalid format")
                return False
        else:
            print(f"❌ GraphQL Schema Introspection - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GraphQL Schema Introspection - Exception: {e}")
        return False


def test_graphql_federation():
    """Test GraphQL Federation service info."""
    print("🌐 Testing GraphQL Federation Service...")
    
    query = {
        "query": """
        {
            _service {
                sdl
            }
        }
        """
    }
    
    try:
        response = requests.post(GRAPHQL_URL, json=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if ('data' in data and '_service' in data['data'] 
                and 'sdl' in data['data']['_service']):
                print("✅ GraphQL Federation Service - SUCCESS")
                return True
            else:
                print("❌ GraphQL Federation Service - Invalid format")
                return False
        else:
            print(f"❌ GraphQL Federation Service - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GraphQL Federation Service - Exception: {e}")
        return False


def test_graphql_user_query():
    """Test GraphQL user query."""
    print("👤 Testing GraphQL User Query...")
    
    query = {
        "query": """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
                fullName
                isActive
                createdAt
            }
        }
        """,
        "variables": {
            "id": TEST_USER_ID
        }
    }
    
    try:
        response = requests.post(GRAPHQL_URL, json=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                if data['data'].get('user'):
                    print("✅ GraphQL User Query - SUCCESS (with data)")
                else:
                    print("✅ GraphQL User Query - SUCCESS (no data, expected)")
                return True
            else:
                print("❌ GraphQL User Query - Invalid response format")
                return False
        else:
            print(f"❌ GraphQL User Query - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GraphQL User Query - Exception: {e}")
        return False


def test_graphql_error_handling():
    """Test GraphQL error handling with invalid query."""
    print("🚨 Testing GraphQL Error Handling...")
    
    query = {
        "query": """
        {
            invalidField {
                nonExistentField
            }
        }
        """
    }
    
    try:
        response = requests.post(GRAPHQL_URL, json=query, timeout=10)
        if response.status_code == 400:
            data = response.json()
            if 'errors' in data:
                print("✅ GraphQL Error Handling - SUCCESS")
                return True
            else:
                print("❌ GraphQL Error Handling - Missing errors array")
                return False
        else:
            print(f"❌ GraphQL Error Handling - Expected 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GraphQL Error Handling - Exception: {e}")
        return False


def main():
    """Run all GraphQL tests."""
    print("🚀 Starting User Management GraphQL Endpoint Tests")
    print(f"GraphQL URL: {GRAPHQL_URL}")
    print(f"Test User ID: {TEST_USER_ID}\n")
    
    tests = [
        test_graphql_schema_introspection,
        test_graphql_federation,
        test_graphql_user_query,
        test_graphql_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("="*60)
    print(f"📊 GraphQL Test Results:")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("🎉 ALL GRAPHQL TESTS PASSED!")
        return 0
    else:
        print("⚠️ SOME GRAPHQL TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())