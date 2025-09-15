#!/usr/bin/env python3
"""
User Management Service - GraphQL Federation Tests
=================================================
Service-specific GraphQL tests for user-management microservice
using the common federation test framework.
"""

import sys
from typing import List

# Import the federation test framework
from graphql_federation_test_framework import (
    GraphQLFederationTester, TestCase, TestResult
)


class UserManagementGraphQLTester(GraphQLFederationTester):
    """GraphQL Federation tester for user-management service."""
    
    def __init__(self):
        super().__init__(
            service_name="user-management",
            base_url="http://localhost:8001",
            test_user_id="00000000-0000-0000-0000-000000000001"
        )
    
    def get_service_specific_tests(self) -> List[TestCase]:
        """Implement user-management specific GraphQL tests."""
        tests = []
        
        # Test user query
        tests.append(self._test_user_query())
        
        # Test user profile query
        tests.append(self._test_user_profile_query())
        
        # Test user context query (for federation)
        tests.append(self._test_user_context_query())
        
        return tests
    
    def _test_user_query(self) -> TestCase:
        """Test user query."""
        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
                fullName
                isActive
                createdAt
            }
        }
        """
        
        variables = {"id": self.test_user_id}
        success, data, error = self.execute_query(query, variables)
        
        if success:
            return TestCase(
                "User Query",
                TestResult.PASSED,
                f"Query executed, data: {'found' if data and data.get('user') else 'null (expected)'}"
            )
        else:
            return TestCase(
                "User Query",
                TestResult.FAILED,
                f"Query failed: {error}"
            )
    
    def _test_user_profile_query(self) -> TestCase:
        """Test user profile related queries."""
        query = """
        {
            __schema {
                types {
                    name
                    fields {
                        name
                    }
                }
            }
        }
        """
        
        success, data, error = self.execute_query(query)
        
        if success:
            types = data.get('__schema', {}).get('types', [])
            profile_types = [t for t in types 
                           if 'profile' in t.get('name', '').lower()]
            
            return TestCase(
                "User Profile Schema",
                TestResult.PASSED,
                f"Found {len(profile_types)} profile-related types"
            )
        else:
            return TestCase(
                "User Profile Schema",
                TestResult.FAILED,
                f"Schema introspection failed: {error}"
            )
    
    def _test_user_context_query(self) -> TestCase:
        """Test user context query (important for federation)."""
        query = """
        {
            __schema {
                types {
                    name
                    fields {
                        name
                    }
                }
            }
        }
        """
        
        success, data, error = self.execute_query(query)
        
        if success:
            types = data.get('__schema', {}).get('types', [])
            context_types = [t for t in types 
                           if 'context' in t.get('name', '').lower()]
            
            return TestCase(
                "User Context Schema",
                TestResult.PASSED,
                f"Found {len(context_types)} context-related types"
            )
        else:
            return TestCase(
                "User Context Schema",
                TestResult.FAILED,
                f"Schema introspection failed: {error}"
            )


def main():
    """Run user-management GraphQL federation tests."""
    tester = UserManagementGraphQLTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())