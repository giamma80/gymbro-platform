#!/usr/bin/env python3
"""
Calorie Balance Service - Comprehensive GraphQL Test Suite
==========================================================
Service: calorie-balance
Schema: calorie_balance 
Date: 17 settembre 2025

Test suite completo per tutti gli endpoint GraphQL utilizzando
i dati preparati in 009_test_data_preparation.sql

Usage:
    python test_graphql_comprehensive.py [local|prod]
"""

import requests
import json
import sys
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List

# Environment Configuration
ENVIRONMENTS = {
    "local": "http://localhost:8002",
    "prod": "https://nutrifit-calorie-balance.onrender.com"
}

# Determine environment
env_profile = sys.argv[1].lower() if len(sys.argv) > 1 else "local"
if env_profile not in ENVIRONMENTS:
    print(f"❌ Invalid profile: {env_profile}")
    sys.exit(1)

BASE_URL = ENVIRONMENTS[env_profile]
GRAPHQL_ENDPOINT = f"{BASE_URL}/graphql"

# Test user from 009_test_data_preparation.sql
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

print("🧪 Calorie Balance GraphQL - Comprehensive Test Suite")
print("=" * 60)
print(f"Service: calorie-balance")
print(f"Environment: {env_profile.upper()}")
print(f"GraphQL Endpoint: {GRAPHQL_ENDPOINT}")
print(f"Test User ID: {TEST_USER_ID}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()


def execute_graphql_query(query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
    """Execute GraphQL query with error handling."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-User-ID": TEST_USER_ID
            },
            timeout=10
        )
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "error": response.text if response.status_code != 200 else None
        }
    except Exception as e:
        return {"status_code": 0, "data": None, "error": str(e)}


def test_query(name: str, query: str, variables: Optional[Dict] = None, 
               expected_fields: Optional[List[str]] = None) -> bool:
    """Execute and validate GraphQL query."""
    print(f"🧪 Testing: {name}")
    
    result = execute_graphql_query(query, variables)
    
    if result["status_code"] != 200:
        print(f"❌ FAIL {name}")
        print(f"     Status: {result['status_code']}, Error: {result['error']}")
        return False
    
    if result["data"] and "errors" in result["data"]:
        print(f"❌ FAIL {name}")
        print(f"     GraphQL Errors: {result['data']['errors']}")
        return False
    
    if result["data"] and "data" in result["data"]:
        data = result["data"]["data"]
        
        # Check expected fields if provided
        if expected_fields:
            for field in expected_fields:
                if field not in data:
                    print(f"❌ FAIL {name}")
                    print(f"     Missing expected field: {field}")
                    return False
        
        print(f"✅ PASS {name}")
        # Print summary info for debugging
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"     {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"     {key}: {len(value)} fields")
                else:
                    print(f"     {key}: {value}")
        return True
    
    print(f"❌ FAIL {name}")
    print(f"     No data returned")
    return False


def run_comprehensive_graphql_tests():
    """Run all GraphQL tests using 009_test_data_preparation.sql data."""
    
    tests_passed = 0
    tests_total = 0
    
    print("📋 GraphQL Schema & Introspection Tests")
    print("=" * 40)
    
    # Test 1: Schema Introspection
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
    tests_total += 1
    if test_query("Schema Introspection", introspection_query):
        tests_passed += 1
    
    print()
    print("📋 Core Entity Queries (Using Test Data)")
    print("=" * 40)
    
    # Test 2: getCurrentCalorieGoal - Should return active goal (2000 cal target)
    current_goal_query = """
    query GetCurrentGoal($userId: String!) {
        getCurrentCalorieGoal(userId: $userId) {
            id
            goalType
            dailyCalorieTarget
            weeklyWeightChangeKg
            startDate
            endDate
            isActive
            aiOptimized
            createdAt
        }
    }
    """
    tests_total += 1
    if test_query(
        "Get Current Calorie Goal", 
        current_goal_query, 
        {"userId": TEST_USER_ID},
        ["getCurrentCalorieGoal"]
    ):
        tests_passed += 1
    
    # Test 3: getUserDailyBalances - Should return 9 days of balances
    daily_balances_query = """
    query GetDailyBalances($userId: String!, $startDate: String!, $endDate: String!) {
        getUserDailyBalances(userId: $userId, startDate: $startDate, endDate: $endDate) {
            id
            userId
            date
            caloriesConsumed
            caloriesBurnedExercise
            dailyCalorieTarget
            morningWeightKg
            progressPercentage
            netCalories
            createdAt
        }
    }
    """
    # Test range covers our prepared data (2025-09-09 to 2025-09-17)
    tests_total += 1
    if test_query(
        "Get User Daily Balances", 
        daily_balances_query,
        {
            "userId": TEST_USER_ID,
            "startDate": "2025-09-09",
            "endDate": "2025-09-17"
        },
        ["getUserDailyBalances"]
    ):
        tests_passed += 1
    
    # Test 4: getUserMetabolicProfile - Should return test metabolic profile
    metabolic_profile_query = """
    query GetMetabolicProfile($userId: String!) {
        getUserMetabolicProfile(userId: $userId) {
            id
            userId
            bmrCalories
            tdeeCalories
            rmrCalories
            calculationMethod
            accuracyScore
            activityLevel
            aiAdjusted
            adjustmentFactor
            learningIterations
            calculatedAt
            expiresAt
            isActive
        }
    }
    """
    tests_total += 1
    if test_query(
        "Get User Metabolic Profile", 
        metabolic_profile_query,
        {"userId": TEST_USER_ID},
        ["getUserMetabolicProfile"]
    ):
        tests_passed += 1
    
    # Test 5: getCalorieEvents - Should return events from test data
    calorie_events_query = """
    query GetCalorieEvents($userId: String!, $startDate: String!, $endDate: String!, $eventType: String) {
        getCalorieEvents(userId: $userId, startDate: $startDate, endDate: $endDate, eventType: $eventType) {
            id
            userId
            eventType
            value
            source
            confidenceScore
            metadata
            eventTimestamp
            createdAt
        }
    }
    """
    tests_total += 1
    if test_query(
        "Get Calorie Events", 
        calorie_events_query,
        {
            "userId": TEST_USER_ID,
            "startDate": "2025-09-09",
            "endDate": "2025-09-17",
            "eventType": "consumed"
        },
        ["getCalorieEvents"]
    ):
        tests_passed += 1
    
    print()
    print("📋 Advanced Analytics Queries")
    print("=" * 40)
    
    # Test 6: getBehavioralPatterns - 🔥 KEY TEST using prepared realistic data
    behavioral_patterns_query = """
    query GetBehavioralPatterns($userId: String!, $startDate: String!, $endDate: String!) {
        getBehavioralPatterns(userId: $userId, startDate: $startDate, endDate: $endDate) {
            userId
            dateRange {
                startDate
                endDate
            }
            dailyPatterns {
                date
                caloriesConsumed
                targetCalories
                progressPercentage
                netCalories
                mealTimings {
                    mealType
                    averageTime
                    calorieRange
                }
                exercisePattern {
                    hasExercise
                    averageTime
                    caloriesBurned
                    activityTypes
                }
                consistencyScore
            }
            weeklyTrends {
                week
                averageConsumption
                averageProgress
                consistencyScore
                bestDay
                challengingDay
            }
            insights {
                consistentMealTimes
                regularExerciser
                weekendPattern
                goalAdherence
                recommendations
            }
            overallScore
            dataQuality {
                completeDays
                totalDays
                dataSourceDiversity
                reliability
            }
        }
    }
    """
    tests_total += 1
    if test_query(
        "Get Behavioral Patterns (CRITICAL TEST)", 
        behavioral_patterns_query,
        {
            "userId": TEST_USER_ID,
            "startDate": "2025-09-09",
            "endDate": "2025-09-17"
        },
        ["getBehavioralPatterns"]
    ):
        tests_passed += 1
    
    # Test 7: getWeeklyAnalytics - Weekly aggregation
    weekly_analytics_query = """
    query GetWeeklyAnalytics($userId: String!, $startDate: String!, $endDate: String!) {
        getWeeklyAnalytics(userId: $userId, startDate: $startDate, endDate: $endDate) {
            userId
            weekStart
            weekEnd
            totalCaloriesConsumed
            totalCaloriesBurned
            averageDailyConsumption
            averageProgressPercentage
            activeDays
            exerciseSessions
            weightChange
            weeklyScore
            highlights
        }
    }
    """
    tests_total += 1
    if test_query(
        "Get Weekly Analytics", 
        weekly_analytics_query,
        {
            "userId": TEST_USER_ID,
            "startDate": "2025-09-09",
            "endDate": "2025-09-17"
        },
        ["getWeeklyAnalytics"]
    ):
        tests_passed += 1
    
    # Test 8: getHourlyAnalytics - Intraday patterns  
    hourly_analytics_query = """
    query GetHourlyAnalytics($userId: String!, $date: String!) {
        getHourlyAnalytics(userId: $userId, date: $date) {
            userId
            date
            hourlyBreakdown {
                hour
                caloriesConsumed
                caloriesBurned
                eventCount
                primaryActivity
            }
            peakHours {
                consumptionPeak
                exercisePeak
                metabolicPeak
            }
            patterns {
                mealTiming
                exerciseTiming
                consistencyScore
            }
        }
    }
    """
    tests_total += 1
    if test_query(
        "Get Hourly Analytics", 
        hourly_analytics_query,
        {
            "userId": TEST_USER_ID,
            "date": "2025-09-17"  # Today in our test data
        },
        ["getHourlyAnalytics"]
    ):
        tests_passed += 1
    
    print()
    print("📋 Mutations (Create/Update Operations)")
    print("=" * 40)
    
    # Test 9: createCalorieGoal - Test goal creation via GraphQL
    create_goal_mutation = """
    mutation CreateGoal($input: CalorieGoalInput!) {
        createCalorieGoal(input: $input) {
            id
            goalType
            dailyCalorieTarget
            weeklyWeightChangeKg
            startDate
            endDate
            isActive
            aiOptimized
            createdAt
        }
    }
    """
    tests_total += 1
    if test_query(
        "Create Calorie Goal (GraphQL)", 
        create_goal_mutation,
        {
            "input": {
                "goalType": "WEIGHT_LOSS",
                "targetWeightKg": 72.0,
                "weeklyWeightChangeKg": -0.3,
                "activityLevel": "MODERATE",
                "userWeightKg": 75.0,
                "userHeightCm": 175,
                "userAge": 32,
                "userGender": "male"
            }
        },
        ["createCalorieGoal"]
    ):
        tests_passed += 1
    
    # Test 10: createCalorieEvent - Test event creation
    create_event_mutation = """
    mutation CreateEvent($input: CalorieEventInput!) {
        createCalorieEvent(input: $input) {
            id
            eventType
            value
            source
            confidenceScore
            metadata
            eventTimestamp
            createdAt
        }
    }
    """
    tests_total += 1
    if test_query(
        "Create Calorie Event", 
        create_event_mutation,
        {
            "input": {
                "eventType": "CONSUMED",
                "value": 350.0,
                "source": "MANUAL",
                "confidenceScore": 1.0,
                "metadata": "{\"meal\": \"breakfast\", \"description\": \"Test breakfast\"}",
                "eventTimestamp": "2025-09-17T09:00:00Z"
            }
        },
        ["createCalorieEvent"]
    ):
        tests_passed += 1
    
    # Test 11: updateCalorieGoal - Test goal update
    update_goal_mutation = """
    mutation UpdateGoal($goalId: String!, $input: CalorieGoalUpdateInput!) {
        updateCalorieGoal(goalId: $goalId, input: $input) {
            id
            goalType
            dailyCalorieTarget
            weeklyWeightChangeKg
            isActive
            updatedAt
        }
    }
    """
    # Note: This would need a real goal ID, so we'll use a placeholder
    tests_total += 1
    if test_query(
        "Update Calorie Goal", 
        update_goal_mutation,
        {
            "goalId": "550e8400-e29b-41d4-a716-446655440001",  # Placeholder
            "input": {
                "dailyCalorieTarget": 1800.0,
                "weeklyWeightChangeKg": -0.4
            }
        },
        ["updateCalorieGoal"]
    ):
        tests_passed += 1
    
    print()
    print("📋 Data Source Analysis (Multi-Source Test Data)")
    print("=" * 40)
    
    # Test 12: Source diversity analysis using our test data
    source_analysis_query = """
    query GetSourceAnalysis($userId: String!, $startDate: String!, $endDate: String!) {
        getCalorieEvents(userId: $userId, startDate: $startDate, endDate: $endDate) {
            source
            confidenceScore
            metadata
        }
    }
    """
    tests_total += 1
    if test_query(
        "Data Source Diversity Analysis", 
        source_analysis_query,
        {
            "userId": TEST_USER_ID,
            "startDate": "2025-09-09",
            "endDate": "2025-09-17"
        },
        ["getCalorieEvents"]
    ):
        tests_passed += 1
    
    print()
    print("📊 Test Summary")
    print("=" * 20)
    success_rate = (tests_passed / tests_total) * 100 if tests_total > 0 else 0
    print(f"Total Tests: {tests_total}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_total - tests_passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if tests_passed == tests_total:
        print("🎉 ALL GRAPHQL TESTS PASSED! Test data preparation working perfectly!")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed. Check GraphQL implementation.")
        return False


if __name__ == "__main__":
    run_comprehensive_graphql_tests()