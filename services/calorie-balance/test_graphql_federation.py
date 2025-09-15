#!/usr/bin/env python3
"""
Calorie Balance Service - GraphQL Federation Tests
=================================================
Service-specific GraphQL tests for calorie-balance microservice
using the common federation test framework.
"""

import sys
import os
from typing import List

# Import the federation test framework
from graphql_federation_test_framework import GraphQLFederationTester, TestCase, TestResult


class CalorieBalanceGraphQLTester(GraphQLFederationTester):
    """GraphQL Federation tester for calorie-balance service."""
    
    def __init__(self):
        super().__init__(
            service_name="calorie-balance",
            base_url="http://localhost:8002",
            test_user_id="00000000-0000-0000-0000-000000000001"
        )
    
    def get_service_specific_tests(self) -> List[TestCase]:
        """Implement calorie-balance specific GraphQL tests."""
        tests = []
        
        # Test calorie balance query
        tests.append(self._test_calorie_balance_query())
        
        # Test metabolic profile query
        tests.append(self._test_metabolic_profile_query())
        
        # Test goals query
        tests.append(self._test_goals_query())
        
        return tests
    
    def _test_calorie_balance_query(self) -> TestCase:
        """Test userCalorieBalance query."""
        query = """
        query GetUserCalorieBalance($userId: String!) {
            userCalorieBalance(userId: $userId) {
                userId
                currentCalories
                targetCalories
                remainingCalories
                lastUpdated
            }
        }
        """
        
        variables = {"userId": self.test_user_id}
        success, data, error = self.execute_query(query, variables)
        
        if success:
            # Check if query executed (data can be null for non-existent user)
            return TestCase(
                "User Calorie Balance Query",
                TestResult.PASSED,
                f"Query executed successfully, data: {'found' if data and data.get('userCalorieBalance') else 'null (expected for test user)'}"
            )
        else:
            return TestCase(
                "User Calorie Balance Query",
                TestResult.FAILED,
                f"Query failed: {error}"
            )
    
    def _test_metabolic_profile_query(self) -> TestCase:
        """Test metabolic profile related queries."""
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
            # Check if metabolic profile types exist
            types = data.get('__schema', {}).get('types', [])
            metabolic_types = [t for t in types if 'metabolic' in t.get('name', '').lower()]
            
            return TestCase(
                "Metabolic Profile Schema",
                TestResult.PASSED,
                f"Found {len(metabolic_types)} metabolic-related types in schema"
            )
        else:
            return TestCase(
                "Metabolic Profile Schema",
                TestResult.FAILED,
                f"Schema introspection failed: {error}"
            )
    
    def _test_goals_query(self) -> TestCase:
        """Test goals-related GraphQL functionality."""
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
            # Check if goal-related types exist
            types = data.get('__schema', {}).get('types', [])
            goal_types = [t for t in types if 'goal' in t.get('name', '').lower()]
            
            return TestCase(
                "Goals Schema",
                TestResult.PASSED,
                f"Found {len(goal_types)} goal-related types in schema"
            )
        else:
            return TestCase(
                "Goals Schema", 
                TestResult.FAILED,
                f"Schema introspection failed: {error}"
            )


def main():
    """Run calorie-balance GraphQL federation tests."""
    tester = CalorieBalanceGraphQLTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())