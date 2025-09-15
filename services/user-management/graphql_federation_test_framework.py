#!/usr/bin/env python3
"""
GraphQL Federation Test Framework
=================================
Common test framework for all microservices in the gymbro-platform
that need to support Apollo Federation.

This framework provides:
1. Common federation tests (schema, SDL, introspection)
2. Base classes for service-specific tests
3. Standardized test reporting
4. Federation compliance validation
"""

import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class TestResult(Enum):
    """Test result enumeration."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class TestCase:
    """Individual test case result."""
    name: str
    result: TestResult
    details: str
    execution_time: float = 0.0


@dataclass
class TestSuite:
    """Test suite results."""
    name: str
    tests: List[TestCase]
    
    @property
    def passed(self) -> int:
        return len([t for t in self.tests if t.result == TestResult.PASSED])
    
    @property
    def failed(self) -> int:
        return len([t for t in self.tests if t.result == TestResult.FAILED])
    
    @property
    def total(self) -> int:
        return len(self.tests)
    
    @property
    def success_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0.0


class GraphQLFederationTester(ABC):
    """
    Base class for GraphQL Federation testing.
    
    Each microservice should extend this class and implement:
    - get_service_specific_tests()
    - Service-specific query/mutation tests
    """
    
    def __init__(self, service_name: str, base_url: str, test_user_id: str = None):
        self.service_name = service_name
        self.base_url = base_url
        self.graphql_url = f"{base_url}/graphql"
        self.test_user_id = test_user_id or "00000000-0000-0000-0000-000000000001"
        self.test_suites: List[TestSuite] = []
    
    def run_all_tests(self) -> bool:
        """Run complete test suite and return success status."""
        print(f"🚀 Starting GraphQL Federation Tests for {self.service_name}")
        print(f"Service URL: {self.base_url}")
        print(f"GraphQL Endpoint: {self.graphql_url}\n")
        
        # Run test suites
        self._run_federation_compliance_tests()
        self._run_service_specific_tests()
        
        # Generate report
        return self._generate_report()
    
    def _run_federation_compliance_tests(self):
        """Run common Apollo Federation compliance tests."""
        tests = []
        
        # Test 1: Schema Introspection
        tests.append(self._test_schema_introspection())
        
        # Test 2: Federation Service SDL
        tests.append(self._test_federation_service_sdl())
        
        # Test 3: Federation Schema Validation
        tests.append(self._test_federation_schema_validation())
        
        # Test 4: Error Handling
        tests.append(self._test_error_handling())
        
        self.test_suites.append(TestSuite("Federation Compliance", tests))
    
    def _run_service_specific_tests(self):
        """Run service-specific GraphQL tests."""
        tests = self.get_service_specific_tests()
        if tests:
            self.test_suites.append(TestSuite(f"{self.service_name} Domain", tests))
    
    @abstractmethod
    def get_service_specific_tests(self) -> List[TestCase]:
        """
        Override this method to provide service-specific tests.
        
        Returns:
            List[TestCase]: Service-specific test cases
        """
        pass
    
    def _test_schema_introspection(self) -> TestCase:
        """Test GraphQL schema introspection."""
        query = {
            "query": """
            {
                __schema {
                    queryType { name }
                    mutationType { name }
                    types {
                        name
                        kind
                    }
                }
            }
            """
        }
        
        try:
            response = requests.post(self.graphql_url, json=query, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and '__schema' in data['data']:
                    schema_data = data['data']['__schema']
                    types_count = len(schema_data.get('types', []))
                    return TestCase(
                        "Schema Introspection",
                        TestResult.PASSED,
                        f"Schema loaded with {types_count} types"
                    )
                else:
                    return TestCase(
                        "Schema Introspection", 
                        TestResult.FAILED,
                        "Invalid introspection response format"
                    )
            else:
                return TestCase(
                    "Schema Introspection",
                    TestResult.FAILED, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            return TestCase(
                "Schema Introspection",
                TestResult.FAILED,
                f"Exception: {str(e)[:100]}"
            )
    
    def _test_federation_service_sdl(self) -> TestCase:
        """Test Apollo Federation _service query for SDL."""
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
            response = requests.post(self.graphql_url, json=query, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if ('data' in data and '_service' in data['data'] 
                    and 'sdl' in data['data']['_service']):
                    sdl = data['data']['_service']['sdl']
                    sdl_length = len(sdl)
                    return TestCase(
                        "Federation Service SDL",
                        TestResult.PASSED,
                        f"SDL retrieved ({sdl_length} characters)"
                    )
                else:
                    return TestCase(
                        "Federation Service SDL",
                        TestResult.FAILED,
                        "SDL not found in response"
                    )
            else:
                return TestCase(
                    "Federation Service SDL",
                    TestResult.FAILED,
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            return TestCase(
                "Federation Service SDL",
                TestResult.FAILED,
                f"Exception: {str(e)[:100]}"
            )
    
    def _test_federation_schema_validation(self) -> TestCase:
        """Validate that schema contains federation directives."""
        try:
            # Get SDL first
            sdl_response = requests.post(
                self.graphql_url,
                json={"query": "{ _service { sdl } }"},
                timeout=10
            )
            
            if sdl_response.status_code != 200:
                return TestCase(
                    "Federation Schema Validation",
                    TestResult.FAILED,
                    "Could not retrieve SDL"
                )
            
            sdl_data = sdl_response.json()
            sdl = sdl_data['data']['_service']['sdl']
            
            # Check for federation directives/keywords
            federation_indicators = [
                'extend type Query',
                'extend type Mutation', 
                '@key',
                '@external',
                '@requires',
                '@provides'
            ]
            
            found_indicators = []
            for indicator in federation_indicators:
                if indicator in sdl:
                    found_indicators.append(indicator)
            
            if found_indicators:
                return TestCase(
                    "Federation Schema Validation",
                    TestResult.PASSED,
                    f"Found federation indicators: {', '.join(found_indicators)}"
                )
            else:
                return TestCase(
                    "Federation Schema Validation",
                    TestResult.FAILED,
                    "No federation directives found in SDL"
                )
        except Exception as e:
            return TestCase(
                "Federation Schema Validation",
                TestResult.FAILED,
                f"Exception: {str(e)[:100]}"
            )
    
    def _test_error_handling(self) -> TestCase:
        """Test GraphQL error handling."""
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
            response = requests.post(self.graphql_url, json=query, timeout=10)
            data = response.json()
            
            # GraphQL should return errors in response, not HTTP error codes
            if 'errors' in data and len(data['errors']) > 0:
                error_count = len(data['errors'])
                return TestCase(
                    "Error Handling",
                    TestResult.PASSED,
                    f"Properly handled {error_count} GraphQL errors"
                )
            else:
                return TestCase(
                    "Error Handling",
                    TestResult.FAILED,
                    f"Expected errors but got HTTP {response.status_code}"
                )
        except Exception as e:
            return TestCase(
                "Error Handling",
                TestResult.FAILED,
                f"Exception: {str(e)[:100]}"
            )
    
    def execute_query(self, query: str, variables: Dict = None) -> Tuple[bool, Any, str]:
        """
        Helper method to execute GraphQL queries.
        
        Returns:
            Tuple[bool, Any, str]: (success, data, error_message)
        """
        try:
            payload = {"query": query}
            if variables:
                payload["variables"] = variables
            
            response = requests.post(self.graphql_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return False, data, f"GraphQL errors: {data['errors']}"
                return True, data.get('data'), ""
            else:
                return False, None, f"HTTP {response.status_code}: {response.text[:100]}"
        except Exception as e:
            return False, None, f"Exception: {str(e)}"
    
    def _generate_report(self) -> bool:
        """Generate and print test report."""
        total_tests = sum(suite.total for suite in self.test_suites)
        total_passed = sum(suite.passed for suite in self.test_suites)
        total_failed = sum(suite.failed for suite in self.test_suites)
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("="*70)
        print(f"📊 GraphQL Federation Test Report - {self.service_name}")
        print("="*70)
        
        for suite in self.test_suites:
            print(f"\n📋 {suite.name}")
            print("-" * 50)
            
            for test in suite.tests:
                icon = "✅" if test.result == TestResult.PASSED else "❌"
                print(f"{icon} {test.name}: {test.details}")
            
            print(f"   Summary: {suite.passed}/{suite.total} passed ({suite.success_rate:.1f}%)")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        
        if total_failed == 0:
            print(f"\n🎉 ALL GRAPHQL FEDERATION TESTS PASSED for {self.service_name}!")
            return True
        else:
            print(f"\n⚠️  {total_failed} TESTS FAILED for {self.service_name}")
            return False