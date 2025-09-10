#!/usr/bin/env python3
"""
GraphQL Quick Test for User Management
======================================
Basic test to verify GraphQL functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8001"
GRAPHQL_ENDPOINT = f"{BASE_URL}/graphql"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"

def test_graphql_basic():
    """Test basic GraphQL functionality."""
    print("🚀 Testing GraphQL Basic Functionality")
    print("=" * 40)
    
    # Test 1: Schema introspection
    print("\n📋 Test 1: Schema Introspection")
    introspection_query = {
        "query": """
        {
            __schema {
                queryType {
                    name
                    fields {
                        name
                        description
                    }
                }
            }
        }
        """
    }
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json=introspection_query, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"❌ GraphQL Errors: {data['errors']}")
            else:
                query_type = data.get("data", {}).get("__schema", {}).get("queryType", {})
                fields = query_type.get("fields", [])
                print(f"✅ Query type: {query_type.get('name')}")
                print(f"✅ Available fields: {len(fields)}")
                for field in fields[:3]:  # Show first 3 fields
                    print(f"   - {field['name']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Simple user query
    print("\n📋 Test 2: Get User Query")
    user_query = {
        "query": """
        query GetUser($id: ID!) {
            getUser(id: $id) {
                id
                email
                username
                isActive
            }
        }
        """,
        "variables": {"id": TEST_USER_ID}
    }
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json=user_query, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"❌ GraphQL Errors: {data['errors']}")
            else:
                user = data.get("data", {}).get("getUser")
                if user:
                    print(f"✅ User found: {user['email']}")
                    print(f"   Username: {user['username']}")
                    print(f"   Active: {user['isActive']}")
                else:
                    print("❌ User not found")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: List users query
    print("\n📋 Test 3: List Users Query")
    list_query = {
        "query": """
        query ListUsers {
            listUsers(limit: 2) {
                success
                message
                total
                data {
                    id
                    email
                    username
                }
            }
        }
        """
    }
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json=list_query, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"❌ GraphQL Errors: {data['errors']}")
            else:
                result = data.get("data", {}).get("listUsers")
                if result and result.get("success"):
                    print(f"✅ Users found: {result['total']}")
                    print(f"   Message: {result['message']}")
                    for user in result.get("data", []):
                        print(f"   - {user['email']} ({user['username']})")
                else:
                    print(f"❌ Query failed: {result.get('message') if result else 'No data'}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: GraphiQL interface
    print("\n📋 Test 4: GraphiQL Interface")
    try:
        response = requests.get(GRAPHQL_ENDPOINT, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "GraphiQL" in content or "graphql" in content.lower():
                print("✅ GraphiQL interface available")
                print(f"   Access at: {GRAPHQL_ENDPOINT}")
            else:
                print("❌ GraphiQL interface not detected")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 GraphQL Testing Complete!")
    print(f"💡 Try GraphiQL at: {GRAPHQL_ENDPOINT}")

if __name__ == "__main__":
    test_graphql_basic()
