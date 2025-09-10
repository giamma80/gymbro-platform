#!/usr/bin/env python3
"""
Verifica rapida degli endpoint implementati
"""

import requests
import json
import uuid
from datetime import datetime

def test_endpoint(method, url, data=None, headers=None):
    """Test di un singolo endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers or {})
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers or {})
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers or {})
        elif method == "DELETE":
            response = requests.delete(url, headers=headers or {})
        
        return {
            "status": response.status_code,
            "response": response.text[:200] if response.text else "",
            "success": 200 <= response.status_code < 300
        }
    except Exception as e:
        return {"status": "ERROR", "response": str(e), "success": False}

def main():
    base_url = "http://localhost:8001"
    
    print("🔍 ENDPOINT DISCOVERY - User Management Service")
    print("=" * 60)
    
    # Health endpoints
    print("\n📊 Health & System:")
    endpoints = [
        ("GET", "/health", None),
        ("GET", "/health/ready", None),
    ]
    
    for method, path, data in endpoints:
        result = test_endpoint(method, base_url + path, data)
        status_icon = "✅" if result["success"] else "❌"
        print(f"  {status_icon} {method} {path}: {result['status']}")
    
    # User endpoints
    print("\n👥 User Management:")
    endpoints = [
        ("GET", "/api/v1/users", None),
        ("POST", "/api/v1/users", {"email": "test@example.com", "username": "test", "password": "Test123!"}),
        ("GET", "/api/v1/users/test@example.com", None),
        ("PUT", "/api/v1/users/test@example.com", {"first_name": "Test"}),
        ("DELETE", "/api/v1/users/test@example.com", None),
    ]
    
    for method, path, data in endpoints:
        result = test_endpoint(method, base_url + path, data)
        status_icon = "✅" if result["success"] else "❌"
        print(f"  {status_icon} {method} {path}: {result['status']}")
    
    # Auth endpoints
    print("\n🔐 Authentication:")
    unique_id = str(uuid.uuid4())[:8]
    test_user = {
        "email": f"test_{unique_id}@example.com",
        "username": f"test_{unique_id}",
        "password": "TestPass123!"
    }
    
    endpoints = [
        ("POST", "/api/v1/auth/register", test_user),
        ("POST", "/api/v1/auth/login", {"email": "test@nutrifit.com", "password": "password123"}),
        ("POST", "/api/v1/auth/logout", None),
        ("POST", "/api/v1/auth/refresh", None),
        ("POST", "/api/v1/auth/password-reset", {"email": "test@nutrifit.com"}),
        ("POST", "/api/v1/auth/password-reset/confirm", {"token": "test", "new_password": "newpass"}),
        ("POST", "/api/v1/auth/verify-email", {"token": "test"}),
        ("GET", "/api/v1/auth/me", None),
        ("GET", "/api/v1/auth/verify-token", None),
    ]
    
    for method, path, data in endpoints:
        result = test_endpoint(method, base_url + path, data)
        status_icon = "✅" if result["success"] else "❌"
        status_text = result['status']
        if result['status'] == 404:
            status_icon = "🚫"  # Not implemented
        elif result['status'] in [400, 401, 403]:
            status_icon = "⚠️"   # Implemented but error
        print(f"  {status_icon} {method} {path}: {status_text}")
    
    # GraphQL endpoints
    print("\n🔗 GraphQL:")
    graphql_queries = [
        ("Query: getUser", {
            "query": "query GetUser($email: String!) { getUserByEmail(email: $email) { id email username } }",
            "variables": {"email": "test@nutrifit.com"}
        }),
        ("Query: listUsers", {
            "query": "query { listUsers { id email username } }"
        }),
        ("Mutation: createUser", {
            "query": f"mutation {{ createUser(email: \"test_{str(uuid.uuid4())[:8]}@example.com\", username: \"test_{str(uuid.uuid4())[:8]}\", password: \"Test123!\") {{ id email }} }}"
        }),
    ]
    
    for name, query_data in graphql_queries:
        result = test_endpoint("POST", base_url + "/graphql", query_data)
        status_icon = "✅" if result["success"] else "❌"
        print(f"  {status_icon} {name}: {result['status']}")
        if result["response"] and "errors" not in result["response"]:
            print(f"    Response: {result['response'][:100]}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY: Tutti gli endpoint sopra sono stati testati")
    print("✅ = Funziona (200-299)")
    print("⚠️  = Implementato ma errore (400-499)")  
    print("🚫 = Non implementato (404)")
    print("❌ = Errore del server (500+)")

if __name__ == "__main__":
    main()
