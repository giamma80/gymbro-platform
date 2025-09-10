#!/usr/bin/env python3
"""
Quick endpoint test
"""

import requests

def main():
    print("Testing User Management Service Endpoints")
    print("========================================")
    
    # Test health
    try:
        health = requests.get("http://localhost:8001/health")
        print(f"Health: {health.status_code}")
    except:
        print("Health: ERROR")
    
    # Test users list
    try:
        users = requests.get("http://localhost:8001/api/v1/users")
        print(f"List Users: {users.status_code}")
    except:
        print("List Users: ERROR")
    
    # Test auth register
    try:
        reg = requests.post("http://localhost:8001/api/v1/auth/register", json={
            "email": "quicktest@example.com", 
            "username": "quicktest", 
            "password": "Test123!"
        })
        print(f"Register: {reg.status_code}")
    except:
        print("Register: ERROR")
    
    # Test auth login
    try:
        login = requests.post("http://localhost:8001/api/v1/auth/login", json={
            "email": "test@nutrifit.com", 
            "password": "password123"
        })
        print(f"Login: {login.status_code}")
    except:
        print("Login: ERROR")
    
    # Test GraphQL
    try:
        gql = requests.post("http://localhost:8001/graphql", json={
            "query": "query { listUsers { id email } }"
        })
        print(f"GraphQL: {gql.status_code}")
    except:
        print("GraphQL: ERROR")

if __name__ == "__main__":
    main()
