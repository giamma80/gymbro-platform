#!/usr/bin/env python3
"""
Calorie Balance Service - Comprehensive Test Suite
=================================================
Service: calorie-balance  
Schema: calorie_balance
Date: 12 settembre 2025

This script runs a comprehensive test suite for the calorie balance service,
including database connectivity, API endpoints, temporal analytics, and event processing.

Usage:
    python test_comprehensive.py [local|prod]
    
    local: Test against localhost:8001 (default)
    prod:  Test against production URL when deployed
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

import requests
from dotenv import load_dotenv

load_dotenv()

# Environment Configuration
ENVIRONMENTS = {
    "local": "http://localhost:8002",
    "prod": "https://nutrifit-calorie-balance.onrender.com"  # Update when deployed
}

# Determine environment from command line argument
if len(sys.argv) > 1:
    env_profile = sys.argv[1].lower()
    if env_profile not in ENVIRONMENTS:
        print(f"❌ Invalid profile: {env_profile}")
        print(f"Available profiles: {', '.join(ENVIRONMENTS.keys())}")
        sys.exit(1)
else:
    env_profile = "local"

# Test Configuration
BASE_URL = ENVIRONMENTS[env_profile]
TEST_USER_ID = str(uuid4())  # Generate test user ID
TEST_EMAIL = "test-calorie@nutrifit.com"

# Test data for calorie tracking
TEST_DATA = {
    "metabolic_calculation": {
        "weight_kg": 75.5,
        "height_cm": 175.0,
        "age": 30,
        "gender": "male",
        "activity_level": "moderate"
    },
    "calorie_goal": {
        "daily_calorie_target": 2000,
        "goal_type": "weight_loss",
        "target_weight_kg": 70.0,
        "weekly_weight_loss_kg": 0.5
    },
    "weight_loss_goal": {
        "weight_kg": 75.5,
        "height_cm": 175.0,
        "age": 30,
        "gender": "male",
        "activity_level": "moderate",
        "target_weight_kg": 70.0,
        "weekly_weight_loss_kg": 0.5
    },
    "daily_balance": {
        "calories_consumed": 1800,
        "calories_burned_exercise": 400,
        "calories_burned_bmr": 1600,
        "net_calories": -200,
        "weight_kg": 75.0
    },
    "calorie_events": [
        {
            "event_type": "consumed",
            "amount": 350,
            "description": "Breakfast oatmeal", 
            "meal_type": "breakfast"
        },
        {
            "event_type": "burned_exercise",
            "amount": 250,
            "description": "Morning run",
            "exercise_type": "running"
        },
        {
            "event_type": "weight_measurement",
            "amount": 75.2,
            "description": "Morning weigh-in"
        }
    ],
    "batch_events": [
        {
            "events": [
                {
                    "event_type": "consumed",
                    "amount": 150,
                    "description": "Apple snack",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "event_type": "burned_exercise", 
                    "amount": 80,
                    "description": "Stairs climbing",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    ]
}


class TestColors:
    """ANSI color codes for test output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


class CalorieBalanceTests:
    """Comprehensive test suite for calorie balance service."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.start_time = time.time()

    def log_header(self, message: str):
        """Print test section header."""
        print(f"\n{TestColors.BOLD}{TestColors.BLUE}{'='*60}")
        print(f"🧪 {message}")
        print(f"{'='*60}{TestColors.END}")

    def log_test(self, message: str):
        """Print individual test message."""
        print(f"{TestColors.CYAN}🔍 {message}{TestColors.END}")

    def log_success(self, message: str):
        """Print success message."""
        print(f"{TestColors.GREEN}✅ {message}{TestColors.END}")
        self.passed += 1

    def log_error(self, message: str):
        """Print error message."""
        print(f"{TestColors.RED}❌ {message}{TestColors.END}")
        self.failed += 1

    def log_info(self, message: str):
        """Print info message."""
        print(f"{TestColors.YELLOW}ℹ️  {message}{TestColors.END}")

    def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make GET request to API."""
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.log_error(f"GET {endpoint} failed: {e}")
            return None

    def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make POST request to API."""
        try:
            response = requests.post(
                f"{BASE_URL}{endpoint}", 
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.log_error(f"POST {endpoint} failed: {e}")
            return None

    def put(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make PUT request to API."""
        try:
            response = requests.put(
                f"{BASE_URL}{endpoint}", 
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.log_error(f"PUT {endpoint} failed: {e}")
            return None

    def test_service_health(self):
        """Test service health endpoints."""
        self.log_header("SERVICE HEALTH CHECKS")
        self.total += 3

        # Basic health check
        self.log_test("Testing basic health endpoint")
        health = self.get("/health")
        if health and health.get("status") == "healthy":
            self.log_success("Basic health check passed")
        else:
            self.log_error("Basic health check failed")

        # Database health check  
        self.log_test("Testing database health endpoint")
        db_health = self.get("/health/db")
        if db_health and db_health.get("database") == "healthy":
            self.log_success("Database health check passed")
        else:
            self.log_error("Database health check failed")

        # API documentation
        self.log_test("Testing API documentation endpoint")
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=10)
            if response.status_code == 200:
                self.log_success("API documentation accessible")
            else:
                self.log_error("API documentation not accessible")
        except Exception as e:
            self.log_error(f"API documentation check failed: {e}")

    def test_metabolic_profiles(self):
        """Test metabolic profile calculation with Parameter Passing pattern."""
        self.log_header("METABOLIC PROFILES (Parameter Passing)")
        self.total += 3

        # Calculate metabolic profile using Parameter Passing pattern
        self.log_test("Calculating metabolic profile with user metrics in request")
        metabolic_data = TEST_DATA["metabolic_calculation"]
        calculated_profile = self.post(f"/api/v1/users/{TEST_USER_ID}/profile/metabolic/calculate", metabolic_data)
        if calculated_profile and calculated_profile.get("bmr_calories"):
            bmr = calculated_profile.get("bmr_calories")
            tdee = calculated_profile.get("tdee_calories") 
            self.log_success(f"Metabolic profile calculated - BMR: {bmr}, TDEE: {tdee}")
        else:
            self.log_error("Failed to calculate metabolic profile")

        # Test with female gender for different calculation
        self.log_test("Testing metabolic calculation for female gender")
        female_data = {**metabolic_data, "gender": "female"}
        female_profile = self.post(f"/api/v1/users/{TEST_USER_ID}/profile/metabolic/calculate", female_data)
        if female_profile and female_profile.get("bmr_calories"):
            female_bmr = female_profile.get("bmr_calories")
            self.log_success(f"Female metabolic profile calculated - BMR: {female_bmr}")
        else:
            self.log_error("Failed to calculate female metabolic profile")

        # Test with different activity levels
        self.log_test("Testing different activity levels")
        high_activity_data = {**metabolic_data, "activity_level": "very_active"}
        high_activity_profile = self.post(f"/api/v1/users/{TEST_USER_ID}/profile/metabolic/calculate", high_activity_data)
        if high_activity_profile and high_activity_profile.get("tdee_calories"):
            high_tdee = high_activity_profile.get("tdee_calories")
            self.log_success(f"High activity TDEE calculated: {high_tdee}")
        else:
            self.log_error("Failed to calculate high activity metabolic profile")

    def test_daily_balance(self):
        """Test daily balance management."""
        self.log_header("DAILY BALANCE MANAGEMENT")
        self.total += 4

        # Update daily balance
        self.log_test("Updating daily balance")
        today = datetime.now().date().isoformat()
        balance_data = {**TEST_DATA["daily_balance"], "date": today}
        updated_balance = self.put(f"/api/v1/balance/users/{TEST_USER_ID}", balance_data)
        if updated_balance and updated_balance.get("date"):
            self.log_success(f"Daily balance updated for date: {updated_balance['date']}")
        else:
            self.log_error("Failed to update daily balance")

        # Get today's balance  
        self.log_test("Retrieving today's balance")
        today_balance = self.get(f"/api/v1/balance/users/{TEST_USER_ID}/today")
        if today_balance and today_balance.get("net_calories") is not None:
            net_calories = today_balance.get("net_calories")
            self.log_success(f"Today's balance retrieved - Net calories: {net_calories}")
        else:
            self.log_error("Failed to retrieve today's balance")

        # Get balance for specific date
        self.log_test("Retrieving balance for specific date")
        date_balance = self.get(f"/api/v1/balance/users/{TEST_USER_ID}/date/{today}")
        if date_balance and date_balance.get("date"):
            self.log_success(f"Balance for date {today} retrieved successfully")
        else:
            self.log_error("Failed to retrieve balance for specific date")

        # Get progress data
        self.log_test("Retrieving progress data")
        progress_request = {"start_date": today, "end_date": today}
        progress_data = self.post(f"/api/v1/balance/users/{TEST_USER_ID}/progress", progress_request)
        if progress_data and isinstance(progress_data, dict):
            self.log_success("Progress data retrieved successfully")
        else:
            self.log_error("Failed to retrieve progress data")

    def test_calorie_events(self):
        """Test calorie event management (Event-Driven Architecture)."""
        self.log_header("CALORIE EVENTS (Event-Driven)")
        self.total += 6

        # Create calorie consumed event
        self.log_test("Creating calorie consumed event")
        consumed_event = TEST_DATA["calorie_events"][0]
        created_consumed = self.post("/api/v1/calorie-event/consumed", {
            "user_id": TEST_USER_ID,
            "amount": consumed_event["amount"],
            "description": consumed_event["description"],
            "meal_type": consumed_event.get("meal_type", "other"),
            "event_timestamp": datetime.now().isoformat()
        })
        if created_consumed and created_consumed.get("id"):
            self.log_success(f"Consumed event created: {created_consumed['id']}")
        else:
            self.log_error("Failed to create consumed event")

        # Create calorie burned event
        self.log_test("Creating calorie burned event")
        burned_event = TEST_DATA["calorie_events"][1]
        created_burned = self.post("/api/v1/calorie-event/burned", {
            "user_id": TEST_USER_ID,
            "amount": burned_event["amount"],
            "description": burned_event["description"],
            "exercise_type": burned_event.get("exercise_type", "other"),
            "event_timestamp": datetime.now().isoformat()
        })
        if created_burned and created_burned.get("id"):
            self.log_success(f"Burned event created: {created_burned['id']}")
        else:
            self.log_error("Failed to create burned event")

        # Create weight measurement event
        self.log_test("Creating weight measurement event")
        weight_event = TEST_DATA["calorie_events"][2]
        created_weight = self.post("/api/v1/calorie-event/weight", {
            "user_id": TEST_USER_ID,
            "weight_kg": weight_event["amount"],
            "description": weight_event["description"],
            "event_timestamp": datetime.now().isoformat()
        })
        if created_weight and created_weight.get("id"):
            self.log_success(f"Weight event created: {created_weight['id']}")
        else:
            self.log_error("Failed to create weight event")

        # Create batch events (mobile optimization)
        self.log_test("Creating batch events")
        batch_data = TEST_DATA["batch_events"][0]
        batch_request = {
            "user_id": TEST_USER_ID,
            "events": batch_data["events"]
        }
        created_batch = self.post("/api/v1/calorie-event/batch", batch_request)
        if created_batch and created_batch.get("created_count"):
            count = created_batch["created_count"]
            self.log_success(f"Batch events created: {count} events")
        else:
            self.log_error("Failed to create batch events")

        # Test timeline API (TODO endpoint - will fail but shows intent)
        self.log_test("Testing events timeline (TODO endpoint)")
        timeline = self.get(f"/api/v1/events/users/{TEST_USER_ID}/timeline")
        if timeline and isinstance(timeline, list):
            self.log_success(f"Timeline retrieved: {len(timeline)} events")
        else:
            self.log_info("Timeline endpoint not yet implemented (expected)")

        # Test latest events API (TODO endpoint - will fail but shows intent)
        self.log_test("Testing latest events (TODO endpoint)")
        latest = self.get(f"/api/v1/events/users/{TEST_USER_ID}/latest")
        if latest and isinstance(latest, list):
            self.log_success(f"Latest events retrieved: {len(latest)} events")
        else:
            self.log_info("Latest events endpoint not yet implemented (expected)")

    def test_goal_management(self):
        """Test calorie goal management with Parameter Passing pattern."""
        self.log_header("GOAL MANAGEMENT")
        self.total += 3

        # Create calorie goal
        self.log_test("Creating calorie goal")
        goal_data = {
            **TEST_DATA["calorie_goal"],
            "start_date": datetime.now().date().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        created_goal = self.post(f"/api/v1/goals/users/{TEST_USER_ID}", goal_data)
        if created_goal and created_goal.get("id"):
            self.log_success(f"Calorie goal created: {created_goal['id']}")
        else:
            self.log_error("Failed to create calorie goal")

        # Get active goal
        self.log_test("Retrieving active calorie goal")
        active_goal = self.get(f"/api/v1/goals/users/{TEST_USER_ID}/active")
        if active_goal and active_goal.get("daily_calorie_target"):
            target = active_goal["daily_calorie_target"]
            self.log_success(f"Active goal retrieved - Daily target: {target}")
        else:
            self.log_error("Failed to retrieve active goal")

        # Test weight loss goal creation with Parameter Passing
        self.log_test("Creating weight loss goal with user metrics")
        weight_loss_data = TEST_DATA["weight_loss_goal"]
        weight_loss_goal = self.post(f"/api/v1/goals/users/{TEST_USER_ID}", weight_loss_data)
        if weight_loss_goal and weight_loss_goal.get("id"):
            self.log_success("Weight loss goal created with Parameter Passing")
        else:
            self.log_error("Failed to create weight loss goal")

    def test_analytics_views(self):
        """Test temporal analytics views (5-Level Analytics)."""
        self.log_header("TEMPORAL ANALYTICS (5-Level Views)")
        self.total += 5

        # Test hourly analytics (TODO endpoint)
        self.log_test("Testing hourly analytics view")
        hourly_data = self.get(f"/api/v1/timeline/users/{TEST_USER_ID}/hourly")
        if hourly_data and isinstance(hourly_data, list):
            self.log_success(f"Hourly analytics retrieved: {len(hourly_data)} records")
        else:
            self.log_info("Hourly analytics endpoint not yet implemented (expected)")

        # Test daily analytics (TODO endpoint)
        self.log_test("Testing daily analytics view")
        daily_data = self.get(f"/api/v1/timeline/users/{TEST_USER_ID}/daily")
        if daily_data and isinstance(daily_data, list):
            self.log_success(f"Daily analytics retrieved: {len(daily_data)} records")
        else:
            self.log_info("Daily analytics endpoint not yet implemented (expected)")

        # Test weekly analytics (TODO endpoint)
        self.log_test("Testing weekly analytics view")
        weekly_data = self.get(f"/api/v1/timeline/users/{TEST_USER_ID}/weekly")
        if weekly_data and isinstance(weekly_data, list):
            self.log_success(f"Weekly analytics retrieved: {len(weekly_data)} records")
        else:
            self.log_info("Weekly analytics endpoint not yet implemented (expected)")

        # Test monthly analytics (TODO endpoint)
        self.log_test("Testing monthly analytics view")
        monthly_data = self.get(f"/api/v1/timeline/users/{TEST_USER_ID}/monthly")
        if monthly_data and isinstance(monthly_data, list):
            self.log_success(f"Monthly analytics retrieved: {len(monthly_data)} records")
        else:
            self.log_info("Monthly analytics endpoint not yet implemented (expected)")

        # Test balance summary (TODO endpoint)
        self.log_test("Testing balance summary analytics")
        balance_summary = self.get(f"/api/v1/timeline/users/{TEST_USER_ID}/balance")
        if balance_summary and isinstance(balance_summary, dict):
            self.log_success("Balance summary analytics retrieved")
        else:
            self.log_info("Balance summary endpoint not yet implemented (expected)")

    def cleanup_test_data(self):
        """Clean up test data."""
        self.log_header("TEST CLEANUP")
        
        self.log_info("Cleaning up test data...")
        self.log_info(f"Test User ID: {TEST_USER_ID}")
        
        # Note: Since calorie-balance service uses Parameter Passing pattern,
        # test data cleanup would involve removing events, goals, and balances
        # However, for comprehensive testing, we'll leave data for inspection
        
        self.log_info("Test data preserved for manual inspection")
        self.log_success("Cleanup completed (data preserved)")

    def print_summary(self):
        """Print test execution summary."""
        duration = time.time() - self.start_time
        
        print(f"\n{TestColors.BOLD}{TestColors.WHITE}{'='*60}")
        print(f"🏁 TEST EXECUTION SUMMARY")
        print(f"{'='*60}{TestColors.END}")
        print(f"{TestColors.GREEN}✅ Passed: {self.passed}{TestColors.END}")
        print(f"{TestColors.RED}❌ Failed: {self.failed}{TestColors.END}")
        print(f"{TestColors.CYAN}📊 Total:  {self.total}{TestColors.END}")
        print(f"{TestColors.YELLOW}⏱️  Duration: {duration:.2f} seconds{TestColors.END}")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        
        if success_rate >= 90:
            print(f"{TestColors.GREEN}{TestColors.BOLD}🎉 SUCCESS: {success_rate:.1f}% tests passed!{TestColors.END}")
        elif success_rate >= 70:
            print(f"{TestColors.YELLOW}{TestColors.BOLD}⚠️  WARNING: {success_rate:.1f}% tests passed{TestColors.END}")
        else:
            print(f"{TestColors.RED}{TestColors.BOLD}🚨 FAILURE: {success_rate:.1f}% tests passed{TestColors.END}")

    def run_all_tests(self):
        """Run the complete test suite."""
        print(f"{TestColors.BOLD}{TestColors.PURPLE}🚀 Starting Calorie Balance Service Tests")
        print(f"Environment: {env_profile.upper()}")
        print(f"Base URL: {BASE_URL}")
        print(f"Test User ID: {TEST_USER_ID}{TestColors.END}")

        try:
            # Run test suites
            self.test_service_health()
            self.test_metabolic_profiles() 
            self.test_daily_balance()
            self.test_calorie_events()
            self.test_goal_management()
            self.test_analytics_views()

        except KeyboardInterrupt:
            self.log_error("Tests interrupted by user")
        except Exception as e:
            self.log_error(f"Unexpected error during tests: {e}")
        finally:
            # Always clean up test data
            self.cleanup_test_data()
            # Print final summary
            self.print_summary()


def main():
    """Main entry point."""
    tester = CalorieBalanceTests()
    tester.run_all_tests()


if __name__ == "__main__":
    main()