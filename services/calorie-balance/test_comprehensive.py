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
    "local": "http://localhost:8001",
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
    "user": {
        "id": TEST_USER_ID,
        "email": TEST_EMAIL,
        "age": 30,
        "gender": "male",
        "height_cm": 175.0,
        "current_weight_kg": 80.0,
        "target_weight_kg": 75.0,
        "activity_level": "moderate"
    },
    "calorie_events": [
        {
            "event_type": "consumed",
            "value": 350.0,
            "source": "manual",
            "confidence_score": 1.0
        },
        {
            "event_type": "burned_exercise", 
            "value": 200.0,
            "source": "fitness_tracker",
            "confidence_score": 0.9
        },
        {
            "event_type": "weight",
            "value": 79.5,
            "source": "smart_scale",
            "confidence_score": 0.95
        }
    ],
    "calorie_goal": {
        "goal_type": "weight_loss",
        "daily_calorie_target": 2000.0,
        "daily_deficit_target": -500.0,
        "weekly_weight_change_kg": -0.5
    }
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

    def test_user_management(self):
        """Test user management endpoints."""
        self.log_header("USER MANAGEMENT")
        self.total += 4

        # Create test user
        self.log_test("Creating test user")
        user_data = TEST_DATA["user"]
        created_user = self.post("/api/v1/users", user_data)
        if created_user and created_user.get("id"):
            self.log_success(f"Test user created: {created_user['id']}")
        else:
            self.log_error("Failed to create test user")

        # Get user profile
        self.log_test("Retrieving user profile")
        user_profile = self.get(f"/api/v1/users/{TEST_USER_ID}")
        if user_profile and user_profile.get("id") == TEST_USER_ID:
            self.log_success("User profile retrieved successfully")
        else:
            self.log_error("Failed to retrieve user profile")

        # Update metabolic profile
        self.log_test("Updating metabolic profile")
        metabolic_data = {
            "bmr_calories": 1800.0,
            "tdee_calories": 2300.0,
            "body_fat_percentage": 15.0
        }
        updated_profile = self.post(f"/api/v1/users/{TEST_USER_ID}/metabolic", metabolic_data)
        if updated_profile:
            self.log_success("Metabolic profile updated successfully")
        else:
            self.log_error("Failed to update metabolic profile")

        # List users (should include test user)
        self.log_test("Listing users")
        users_list = self.get("/api/v1/users")
        if users_list and isinstance(users_list, list):
            self.log_success(f"Users list retrieved ({len(users_list)} users)")
        else:
            self.log_error("Failed to retrieve users list")

    def test_calorie_events(self):
        """Test calorie event management."""
        self.log_header("CALORIE EVENT MANAGEMENT")
        self.total += 5

        # Create calorie events
        self.log_test("Creating calorie events")
        events_created = 0
        for event_data in TEST_DATA["calorie_events"]:
            event_payload = {
                **event_data,
                "user_id": TEST_USER_ID,
                "event_timestamp": datetime.now().isoformat()
            }
            created_event = self.post("/api/v1/events", event_payload)
            if created_event and created_event.get("id"):
                events_created += 1

        if events_created == len(TEST_DATA["calorie_events"]):
            self.log_success(f"All {events_created} calorie events created")
        else:
            self.log_error(f"Only {events_created}/{len(TEST_DATA['calorie_events'])} events created")

        # Get user events
        self.log_test("Retrieving user events")
        user_events = self.get(f"/api/v1/users/{TEST_USER_ID}/events")
        if user_events and isinstance(user_events, list) and len(user_events) > 0:
            self.log_success(f"Retrieved {len(user_events)} user events")
        else:
            self.log_error("Failed to retrieve user events")

        # Get events by date range
        self.log_test("Retrieving events by date range")
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        date_events = self.get(f"/api/v1/users/{TEST_USER_ID}/events?start_date={yesterday}&end_date={today}")
        if date_events and isinstance(date_events, list):
            self.log_success(f"Retrieved {len(date_events)} events in date range")
        else:
            self.log_error("Failed to retrieve events by date range")

        # Get events by type
        self.log_test("Retrieving events by type")
        consumed_events = self.get(f"/api/v1/users/{TEST_USER_ID}/events?event_type=consumed")
        if consumed_events and isinstance(consumed_events, list):
            self.log_success(f"Retrieved {len(consumed_events)} consumed events")
        else:
            self.log_error("Failed to retrieve events by type")

        # Delete an event
        if user_events and len(user_events) > 0:
            self.log_test("Deleting a calorie event")
            event_id = user_events[0]["id"]
            try:
                response = requests.delete(f"{BASE_URL}/api/v1/events/{event_id}", timeout=10)
                if response.status_code == 204:
                    self.log_success("Event deleted successfully")
                else:
                    self.log_error("Failed to delete event")
            except Exception as e:
                self.log_error(f"Event deletion failed: {e}")

    def test_goal_management(self):
        """Test calorie goal management."""
        self.log_header("GOAL MANAGEMENT")
        self.total += 3

        # Create calorie goal
        self.log_test("Creating calorie goal")
        goal_data = {
            **TEST_DATA["calorie_goal"],
            "user_id": TEST_USER_ID,
            "start_date": datetime.now().date().isoformat()
        }
        created_goal = self.post("/api/v1/goals", goal_data)
        if created_goal and created_goal.get("id"):
            self.log_success(f"Calorie goal created: {created_goal['id']}")
            goal_id = created_goal["id"]
        else:
            self.log_error("Failed to create calorie goal")
            return

        # Get user goals
        self.log_test("Retrieving user goals")
        user_goals = self.get(f"/api/v1/users/{TEST_USER_ID}/goals")
        if user_goals and isinstance(user_goals, list) and len(user_goals) > 0:
            self.log_success(f"Retrieved {len(user_goals)} user goals")
        else:
            self.log_error("Failed to retrieve user goals")

        # Update goal
        self.log_test("Updating calorie goal")
        update_data = {"daily_calorie_target": 1900.0}
        try:
            response = requests.patch(
                f"{BASE_URL}/api/v1/goals/{goal_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                self.log_success("Goal updated successfully")
            else:
                self.log_error("Failed to update goal")
        except Exception as e:
            self.log_error(f"Goal update failed: {e}")

    def test_analytics_views(self):
        """Test temporal analytics views."""
        self.log_header("TEMPORAL ANALYTICS")
        self.total += 5

        # Test daily summary
        self.log_test("Testing daily calorie summary")
        daily_summary = self.get(f"/api/v1/analytics/daily/{TEST_USER_ID}")
        if daily_summary:
            self.log_success("Daily summary retrieved")
        else:
            self.log_error("Failed to retrieve daily summary")

        # Test weekly summary  
        self.log_test("Testing weekly calorie summary")
        weekly_summary = self.get(f"/api/v1/analytics/weekly/{TEST_USER_ID}")
        if weekly_summary:
            self.log_success("Weekly summary retrieved")
        else:
            self.log_error("Failed to retrieve weekly summary")

        # Test monthly summary
        self.log_test("Testing monthly calorie summary")
        monthly_summary = self.get(f"/api/v1/analytics/monthly/{TEST_USER_ID}")
        if monthly_summary:
            self.log_success("Monthly summary retrieved")
        else:
            self.log_error("Failed to retrieve monthly summary")

        # Test balance summary
        self.log_test("Testing daily balance summary")
        balance_summary = self.get(f"/api/v1/analytics/balance/{TEST_USER_ID}")
        if balance_summary:
            self.log_success("Balance summary retrieved")
        else:
            self.log_error("Failed to retrieve balance summary")

        # Test trend analysis
        self.log_test("Testing trend analysis")
        trend_data = self.get(f"/api/v1/analytics/trends/{TEST_USER_ID}?period=7")
        if trend_data:
            self.log_success("Trend analysis retrieved")
        else:
            self.log_error("Failed to retrieve trend analysis")

    def cleanup_test_data(self):
        """Clean up test data."""
        self.log_header("TEST CLEANUP")
        
        self.log_info("Cleaning up test data...")
        
        # Delete test user (cascade should handle related data)
        try:
            response = requests.delete(f"{BASE_URL}/api/v1/users/{TEST_USER_ID}", timeout=10)
            if response.status_code == 204:
                self.log_success("Test user deleted successfully")
            else:
                self.log_error("Failed to delete test user")
        except Exception as e:
            self.log_error(f"Test cleanup failed: {e}")

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
            self.test_user_management()
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