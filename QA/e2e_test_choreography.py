#!/usr/bin/env python3
"""
GymBro Platform - End-to-End Test Choreography Script
Implements comprehensive integration testing following E2E_TEST_CHOREOGRAPHY.md specification
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

# Test Configuration
USER_MANAGEMENT_URL = "http://localhost:8001"
CALORIE_BALANCE_URL = "http://localhost:8002"
APOLLO_GATEWAY_URL = "http://localhost:4000"

class TestResults:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
        self.execution_time = 0
        
    def add_result(self, test_name: str, success: bool, message: str = ""):
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            self.errors.append(f"{test_name}: {message}")
            print(f"❌ {test_name}: {message}")
            
    def summary(self):
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n{'='*60}")
        print(f"TEST EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Execution Time: {self.execution_time:.2f}s")
        
        if self.errors:
            print(f"\n❌ FAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.failed_tests == 0

class GymBroE2ETest:
    def __init__(self):
        self.results = TestResults()
        self.test_user_id = None
        self.test_user_data = {}
        self.metabolic_profile_id = None
        self.calorie_goal_id = None
        self.test_events = []
        self.timestamp = int(time.time())
        
        # Test dates
        self.day1_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        self.day2_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
    def check_service_health(self):
        """Verify all services are running"""
        print(f"\n🔍 PHASE 0: SERVICE HEALTH CHECKS")
        print(f"{'='*50}")
        
        services = [
            ("User Management", f"{USER_MANAGEMENT_URL}/health"),
            ("Calorie Balance", f"{CALORIE_BALANCE_URL}/health"),
            ("Apollo Gateway", f"{APOLLO_GATEWAY_URL}/health")
        ]
        
        for service_name, health_url in services:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    self.results.add_result(f"{service_name} Health Check", True)
                else:
                    self.results.add_result(f"{service_name} Health Check", False, f"HTTP {response.status_code}")
                    return False
            except Exception as e:
                self.results.add_result(f"{service_name} Health Check", False, str(e))
                return False
        
        return True
        
    def phase1_user_lifecycle(self):
        """Phase 1: User Lifecycle Management"""
        print(f"\n👤 PHASE 1: USER LIFECYCLE MANAGEMENT")
        print(f"{'='*50}")
        
        # Step 1.1: Create Test User
        user_data = {
            "email": f"qa-test-user-{self.timestamp}@gymbrotest.com",
            "username": f"qa_testuser_{self.timestamp}",
            "password": "TestPass123!",
            "is_active": True
        }
        
        try:
            response = requests.post(f"{USER_MANAGEMENT_URL}/users", json=user_data, timeout=10)
            
            if response.status_code == 201:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    self.test_user_id = response_data['data']['id']
                    self.test_user_data = response_data['data']
                    
                    # Validation checks
                    email_valid = self.test_user_data['email'] == user_data['email']
                    username_valid = self.test_user_data['username'] == user_data['username']
                    active_valid = self.test_user_data.get('is_active', False)
                    has_id = bool(self.test_user_id)
                    
                    if email_valid and username_valid and active_valid and has_id:
                        self.results.add_result("Create Test User", True)
                    else:
                        self.results.add_result("Create Test User", False, "Data validation failed")
                        return False
                else:
                    self.results.add_result("Create Test User", False, "Invalid response format")
                    return False
            else:
                self.results.add_result("Create Test User", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.results.add_result("Create Test User", False, str(e))
            return False
        
        # Step 1.2: Retrieve Created User
        try:
            response = requests.get(f"{USER_MANAGEMENT_URL}/users/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    retrieved_user = response_data['data']
                    
                    # Validation checks
                    id_match = retrieved_user['id'] == self.test_user_id
                    email_match = retrieved_user['email'] == user_data['email']
                    username_match = retrieved_user['username'] == user_data['username']
                    
                    if id_match and email_match and username_match:
                        self.results.add_result("Retrieve Created User", True)
                    else:
                        self.results.add_result("Retrieve Created User", False, "Data mismatch")
                        return False
                else:
                    self.results.add_result("Retrieve Created User", False, "Invalid response format")
                    return False
            else:
                self.results.add_result("Retrieve Created User", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.results.add_result("Retrieve Created User", False, str(e))
            return False
            
        # Step 1.3: GraphQL User Verification
        try:
            query = f'''
            query {{
                getUser(userId: "{self.test_user_id}") {{
                    id
                    email  
                    username
                    isActive
                    createdAt
                }}
            }}
            '''
            
            response = requests.post(
                f"{APOLLO_GATEWAY_URL}/graphql",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'errors' not in response_data and response_data.get('data', {}).get('getUser'):
                    graphql_user = response_data['data']['getUser']
                    
                    # Validation checks
                    id_match = graphql_user['id'] == self.test_user_id
                    email_match = graphql_user['email'] == user_data['email']
                    username_match = graphql_user['username'] == user_data['username']
                    
                    if id_match and email_match and username_match:
                        self.results.add_result("GraphQL User Verification", True)
                    else:
                        self.results.add_result("GraphQL User Verification", False, "Data mismatch")
                else:
                    error_msg = response_data.get('errors', [{}])[0].get('message', 'Unknown GraphQL error')
                    self.results.add_result("GraphQL User Verification", False, f"GraphQL error: {error_msg}")
            else:
                self.results.add_result("GraphQL User Verification", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("GraphQL User Verification", False, str(e))
            
        return self.test_user_id is not None
        
    def phase2_metabolic_profile(self):
        """Phase 2: Metabolic Profile Setup"""
        print(f"\n🧮 PHASE 2: METABOLIC PROFILE SETUP")
        print(f"{'='*50}")
        
        # Step 2.1: Calculate Metabolic Profile
        profile_data = {
            "user_id": self.test_user_id,
            "age": 30,
            "height": 175,
            "weight": 75,
            "gender": "male",
            "activity_level": "moderate"
        }
        
        try:
            response = requests.post(
                f"{CALORIE_BALANCE_URL}/metabolic-profiles/calculate",
                json=profile_data,
                timeout=10
            )
            
            if response.status_code == 201:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    profile = response_data['data']
                    self.metabolic_profile_id = profile.get('id')
                    
                    # Validation checks
                    bmr_reasonable = 1600 <= profile.get('bmr_calories', 0) <= 2000
                    tdee_higher = profile.get('tdee_calories', 0) > profile.get('bmr_calories', 0)
                    accuracy_good = profile.get('accuracy_score', 0) > 0.7
                    
                    if bmr_reasonable and tdee_higher and accuracy_good:
                        self.results.add_result("Calculate Metabolic Profile", True)
                    else:
                        self.results.add_result("Calculate Metabolic Profile", False, "Validation failed")
                else:
                    self.results.add_result("Calculate Metabolic Profile", False, "Invalid response format")
            else:
                self.results.add_result("Calculate Metabolic Profile", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.results.add_result("Calculate Metabolic Profile", False, str(e))
            
        # Step 2.2: Verify Metabolic Profile
        try:
            response = requests.get(
                f"{CALORIE_BALANCE_URL}/metabolic-profiles/user/{self.test_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    profile = response_data['data']
                    is_active = profile.get('is_active', False)
                    has_future_expiry = profile.get('expires_at') is not None
                    
                    if is_active and has_future_expiry:
                        self.results.add_result("Verify Metabolic Profile", True)
                    else:
                        self.results.add_result("Verify Metabolic Profile", False, "Profile validation failed")
                else:
                    self.results.add_result("Verify Metabolic Profile", False, "Invalid response format")
            else:
                self.results.add_result("Verify Metabolic Profile", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Verify Metabolic Profile", False, str(e))
            
        return self.metabolic_profile_id is not None
        
    def phase3_calorie_goals(self):
        """Phase 3: Calorie Goal Configuration"""
        print(f"\n🎯 PHASE 3: CALORIE GOAL CONFIGURATION")
        print(f"{'='*50}")
        
        # Step 3.1: Create Primary Calorie Goal
        goal_data = {
            "user_id": self.test_user_id,
            "goal_type": "weight_loss",
            "daily_calorie_target": 1800,
            "daily_deficit_target": 500,
            "weekly_weight_change_kg": -0.5,
            "start_date": self.current_date,
            "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "is_active": True
        }
        
        try:
            response = requests.post(
                f"{CALORIE_BALANCE_URL}/calorie-goals",
                json=goal_data,
                timeout=10
            )
            
            if response.status_code == 201:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    goal = response_data['data']
                    self.calorie_goal_id = goal.get('id')
                    
                    # Validation checks
                    target_reasonable = 1500 <= goal.get('daily_calorie_target', 0) <= 2000
                    deficit_reasonable = 300 <= goal.get('daily_deficit_target', 0) <= 700
                    weight_change_reasonable = -0.8 <= goal.get('weekly_weight_change_kg', 0) <= -0.3
                    
                    if target_reasonable and deficit_reasonable and weight_change_reasonable:
                        self.results.add_result("Create Primary Calorie Goal", True)
                    else:
                        self.results.add_result("Create Primary Calorie Goal", False, "Goal validation failed")
                else:
                    self.results.add_result("Create Primary Calorie Goal", False, "Invalid response format")
            else:
                self.results.add_result("Create Primary Calorie Goal", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.results.add_result("Create Primary Calorie Goal", False, str(e))
            
        return self.calorie_goal_id is not None
        
    def phase4_calorie_events_simulation(self):
        """Phase 4: Multi-Day Calorie Event Simulation"""
        print(f"\n📊 PHASE 4: MULTI-DAY CALORIE EVENT SIMULATION")
        print(f"{'='*50}")
        
        # Day 1 Scenario - "Baseline Day"
        day1_events = [
            # Morning Events (08:00-12:00)
            {"time": "08:00", "type": "consumed", "value": 650, "source": "manual_entry", "description": "Breakfast"},
            {"time": "09:30", "type": "burned_exercise", "value": 300, "source": "fitness_tracker", "description": "Exercise"},
            {"time": "11:00", "type": "consumed", "value": 150, "source": "manual_entry", "description": "Snack"},
            # Afternoon Events (12:00-18:00)
            {"time": "13:00", "type": "consumed", "value": 750, "source": "manual_entry", "description": "Lunch"},
            {"time": "15:30", "type": "burned_exercise", "value": 200, "source": "fitness_tracker", "description": "Light exercise"},
            {"time": "16:00", "type": "consumed", "value": 100, "source": "manual_entry", "description": "Snack"},
            # Evening Events (18:00-23:00)
            {"time": "19:30", "type": "consumed", "value": 800, "source": "manual_entry", "description": "Dinner"},
            {"time": "21:00", "type": "consumed", "value": 200, "source": "manual_entry", "description": "Dessert"}
        ]
        
        # Day 2 Scenario - "High Activity Day"
        day2_events = [
            # Morning Events
            {"time": "07:30", "type": "consumed", "value": 400, "source": "manual_entry", "description": "Light breakfast"},
            {"time": "08:00", "type": "burned_exercise", "value": 600, "source": "fitness_tracker", "description": "Intense workout"},
            {"time": "10:00", "type": "consumed", "value": 250, "source": "manual_entry", "description": "Post-workout snack"},
            # Afternoon Events
            {"time": "12:30", "type": "consumed", "value": 700, "source": "manual_entry", "description": "Lunch"},
            {"time": "14:00", "type": "burned_exercise", "value": 150, "source": "fitness_tracker", "description": "Walking"},
            {"time": "16:30", "type": "consumed", "value": 300, "source": "manual_entry", "description": "Protein shake"},
            # Evening Events
            {"time": "18:00", "type": "consumed", "value": 900, "source": "manual_entry", "description": "Large dinner"},
            {"time": "20:00", "type": "burned_exercise", "value": 200, "source": "fitness_tracker", "description": "Evening walk"}
        ]
        
        # Day 3 Scenario - "Current Day"
        day3_events = [
            {"time": "08:00", "type": "consumed", "value": 550, "source": "manual_entry", "description": "Breakfast"},
            {"time": "10:00", "type": "burned_exercise", "value": 400, "source": "fitness_tracker", "description": "Morning exercise"},
            {"time": "11:30", "type": "consumed", "value": 120, "source": "manual_entry", "description": "Snack"}
        ]
        
        # Create events for each day
        scenarios = [
            (self.day1_date, day1_events, "Day 1 - Baseline Day"),
            (self.day2_date, day2_events, "Day 2 - High Activity Day"),
            (self.current_date, day3_events, "Day 3 - Current Day")
        ]
        
        for date, events, scenario_name in scenarios:
            success_count = 0
            for event in events:
                event_data = {
                    "user_id": self.test_user_id,
                    "event_type": event["type"],
                    "event_timestamp": f"{date}T{event['time']}:00Z",
                    "value": event["value"],
                    "source": event["source"],
                    "confidence_score": 0.95,
                    "metadata": json.dumps({"description": event["description"]})
                }
                
                try:
                    response = requests.post(
                        f"{CALORIE_BALANCE_URL}/calorie-events",
                        json=event_data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        success_count += 1
                        self.test_events.append(event_data)
                    else:
                        print(f"   ⚠️  Failed to create event: {event['description']} - HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error creating event: {event['description']} - {str(e)}")
                    
            # Validate scenario creation
            expected_events = len(events)
            if success_count == expected_events:
                self.results.add_result(f"Create {scenario_name} Events", True)
            else:
                self.results.add_result(f"Create {scenario_name} Events", False, f"Only {success_count}/{expected_events} events created")
                
        return len(self.test_events) > 0
        
    def phase5_daily_balance_validation(self):
        """Phase 5: Daily Balance Validation"""
        print(f"\n⚖️  PHASE 5: DAILY BALANCE VALIDATION")
        print(f"{'='*50}")
        
        # Expected totals for validation
        expected_balances = {
            self.day1_date: {"consumed": 1650, "burned": 500, "net": 1150, "events": 8},
            self.day2_date: {"consumed": 2550, "burned": 950, "net": 1600, "events": 8},
            self.current_date: {"consumed": 670, "burned": 400, "net": 270, "events": 3}
        }
        
        for date, expected in expected_balances.items():
            day_name = {
                self.day1_date: "Day 1",
                self.day2_date: "Day 2", 
                self.current_date: "Current Day"
            }[date]
            
            try:
                if date == self.current_date:
                    # Use current endpoint for today
                    response = requests.get(
                        f"{CALORIE_BALANCE_URL}/daily-balances/user/{self.test_user_id}/current",
                        timeout=10
                    )
                else:
                    # Use date-specific endpoint
                    response = requests.get(
                        f"{CALORIE_BALANCE_URL}/daily-balances/user/{self.test_user_id}/date/{date}",
                        timeout=10
                    )
                    
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('success') and response_data.get('data'):
                        balance = response_data['data']
                        
                        # Validation checks with tolerance
                        consumed_ok = abs(balance.get('calories_consumed', 0) - expected['consumed']) <= 50
                        burned_ok = abs(balance.get('calories_burned_exercise', 0) - expected['burned']) <= 50
                        net_ok = abs(balance.get('net_calories', 0) - expected['net']) <= 50
                        events_ok = balance.get('events_count', 0) == expected['events']
                        completeness_ok = balance.get('data_completeness_score', 0) > 0.5
                        
                        if consumed_ok and burned_ok and net_ok and events_ok and completeness_ok:
                            self.results.add_result(f"Validate {day_name} Balance", True)
                        else:
                            details = f"consumed:{balance.get('calories_consumed')}/{expected['consumed']}, net:{balance.get('net_calories')}/{expected['net']}"
                            self.results.add_result(f"Validate {day_name} Balance", False, f"Validation failed - {details}")
                    else:
                        self.results.add_result(f"Validate {day_name} Balance", False, "Invalid response format")
                else:
                    self.results.add_result(f"Validate {day_name} Balance", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results.add_result(f"Validate {day_name} Balance", False, str(e))
                
    def phase6_timeline_analytics(self):
        """Phase 6: Timeline Analytics Validation"""
        print(f"\n📈 PHASE 6: TIMELINE ANALYTICS VALIDATION")
        print(f"{'='*50}")
        
        # Step 6.1: Hourly Analytics
        try:
            response = requests.get(
                f"{CALORIE_BALANCE_URL}/analytics/hourly",
                params={"user_id": self.test_user_id, "date": self.day1_date},
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    hourly_data = response_data['data']
                    
                    # Validation checks
                    has_24_hours = len(hourly_data) == 24
                    has_activity_hours = any(hour['calories_consumed'] > 0 for hour in hourly_data)
                    has_zero_hours = any(hour['calories_consumed'] == 0 for hour in hourly_data)
                    
                    if has_24_hours and has_activity_hours and has_zero_hours:
                        self.results.add_result("Hourly Analytics Validation", True)
                    else:
                        self.results.add_result("Hourly Analytics Validation", False, "Data structure validation failed")
                else:
                    self.results.add_result("Hourly Analytics Validation", False, "Invalid response format")
            else:
                self.results.add_result("Hourly Analytics Validation", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Hourly Analytics Validation", False, str(e))
            
        # Step 6.2: Daily Analytics Comparison
        try:
            response = requests.get(
                f"{CALORIE_BALANCE_URL}/analytics/daily",
                params={
                    "user_id": self.test_user_id, 
                    "start_date": self.day1_date,
                    "end_date": self.current_date
                },
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    daily_data = response_data['data']
                    
                    # Validation checks
                    has_multiple_days = len(daily_data) >= 3
                    has_trend_analysis = all('trend_direction' in day for day in daily_data if isinstance(day, dict))
                    has_goal_data = all('goal_target' in day for day in daily_data if isinstance(day, dict))
                    
                    if has_multiple_days and (has_trend_analysis or has_goal_data):
                        self.results.add_result("Daily Analytics Comparison", True)
                    else:
                        self.results.add_result("Daily Analytics Comparison", False, "Analytics validation failed")
                else:
                    self.results.add_result("Daily Analytics Comparison", False, "Invalid response format")
            else:
                self.results.add_result("Daily Analytics Comparison", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Daily Analytics Comparison", False, str(e))
            
        # Step 6.3: Weekly Analytics
        try:
            response = requests.get(
                f"{CALORIE_BALANCE_URL}/analytics/weekly",
                params={"user_id": self.test_user_id, "weeks": 1},
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    weekly_data = response_data['data']
                    
                    # Validation checks
                    has_data = len(weekly_data) > 0
                    has_averages = any('avg_daily_consumed' in week for week in weekly_data if isinstance(week, dict))
                    has_activity_days = any('active_days' in week for week in weekly_data if isinstance(week, dict))
                    
                    if has_data and (has_averages or has_activity_days):
                        self.results.add_result("Weekly Analytics Validation", True)
                    else:
                        self.results.add_result("Weekly Analytics Validation", False, "Weekly data validation failed")
                else:
                    self.results.add_result("Weekly Analytics Validation", False, "Invalid response format")
            else:
                self.results.add_result("Weekly Analytics Validation", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Weekly Analytics Validation", False, str(e))
            
        # Step 6.4: Behavioral Pattern Detection
        try:
            response = requests.get(
                f"{CALORIE_BALANCE_URL}/analytics/patterns",
                params={
                    "user_id": self.test_user_id, 
                    "pattern_type": "eating_schedule"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') and response_data.get('data'):
                    pattern_data = response_data['data']
                    
                    # Validation checks
                    has_patterns = len(pattern_data) > 0
                    has_confidence = any('confidence_score' in pattern for pattern in pattern_data if isinstance(pattern, dict))
                    good_confidence = any(
                        pattern.get('confidence_score', 0) > 0.6 
                        for pattern in pattern_data 
                        if isinstance(pattern, dict)
                    )
                    
                    if has_patterns and has_confidence and good_confidence:
                        self.results.add_result("Behavioral Pattern Detection", True)
                    else:
                        self.results.add_result("Behavioral Pattern Detection", False, "Pattern detection validation failed")
                else:
                    self.results.add_result("Behavioral Pattern Detection", False, "Invalid response format")
            else:
                self.results.add_result("Behavioral Pattern Detection", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Behavioral Pattern Detection", False, str(e))
            
    def phase7_graphql_federation(self):
        """Phase 7: GraphQL Federation End-to-End"""
        print(f"\n🔗 PHASE 7: GRAPHQL FEDERATION END-TO-END")
        print(f"{'='*50}")
        
        # Step 7.1: Cross-Service User Profile Query
        try:
            query = f'''
            query {{
                getUser(userId: "{self.test_user_id}") {{
                    id
                    email
                    username
                }}
                getUserMetabolicProfile(userId: "{self.test_user_id}") {{
                    success
                    data {{
                        userId
                        bmrCalories
                        tdeeCalories
                        accuracyScore
                        isActive
                    }}
                }}
            }}
            '''
            
            response = requests.post(
                f"{APOLLO_GATEWAY_URL}/graphql",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'errors' not in response_data:
                    user_data = response_data.get('data', {}).get('getUser')
                    metabolic_data = response_data.get('data', {}).get('getUserMetabolicProfile')
                    
                    # Validation checks
                    has_user_data = user_data and user_data.get('id') == self.test_user_id
                    has_metabolic_data = metabolic_data and metabolic_data.get('success')
                    cross_service_working = has_user_data and has_metabolic_data
                    
                    if cross_service_working:
                        self.results.add_result("Cross-Service GraphQL Query", True)
                    else:
                        self.results.add_result("Cross-Service GraphQL Query", False, "Federation data validation failed")
                else:
                    error_msg = response_data.get('errors', [{}])[0].get('message', 'Unknown GraphQL error')
                    self.results.add_result("Cross-Service GraphQL Query", False, f"GraphQL errors: {error_msg}")
            else:
                self.results.add_result("Cross-Service GraphQL Query", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Cross-Service GraphQL Query", False, str(e))
            
        # Step 7.2: Timeline Analytics via GraphQL
        try:
            query = f'''
            query {{
                getDailyAnalytics(userId: "{self.test_user_id}", startDate: "{self.day1_date}", endDate: "{self.current_date}") {{
                    success
                    data {{
                        date
                        caloriesConsumed
                        caloriesBurnedExercise
                        netCalories
                        goalTarget
                        goalDeviation
                        trendDirection
                        activeHours
                    }}
                    metadata
                }}
            }}
            '''
            
            response = requests.post(
                f"{APOLLO_GATEWAY_URL}/graphql", 
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'errors' not in response_data:
                    analytics_data = response_data.get('data', {}).get('getDailyAnalytics')
                    
                    if analytics_data and analytics_data.get('success') and analytics_data.get('data'):
                        self.results.add_result("Timeline Analytics via GraphQL", True)
                    else:
                        self.results.add_result("Timeline Analytics via GraphQL", False, "No analytics data returned")
                else:
                    error_msg = response_data.get('errors', [{}])[0].get('message', 'Unknown GraphQL error')
                    self.results.add_result("Timeline Analytics via GraphQL", False, f"GraphQL errors: {error_msg}")
            else:
                self.results.add_result("Timeline Analytics via GraphQL", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_result("Timeline Analytics via GraphQL", False, str(e))
            
    def phase8_data_consistency(self):
        """Phase 8: Data Consistency Cross-Validation"""
        print(f"\n🔍 PHASE 8: DATA CONSISTENCY CROSS-VALIDATION")
        print(f"{'='*50}")
        
        # Step 8.1: REST vs GraphQL Consistency
        try:
            # Get user via REST
            rest_response = requests.get(f"{USER_MANAGEMENT_URL}/users/{self.test_user_id}", timeout=10)
            
            # Get user via GraphQL
            graphql_query = f'''query {{ getUser(userId: "{self.test_user_id}") {{ id email username isActive }} }}'''
            graphql_response = requests.post(
                f"{APOLLO_GATEWAY_URL}/graphql",
                json={"query": graphql_query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if rest_response.status_code == 200 and graphql_response.status_code == 200:
                rest_data = rest_response.json().get('data', {})
                graphql_data = graphql_response.json().get('data', {}).get('getUser', {})
                
                # Compare key fields
                id_match = rest_data.get('id') == graphql_data.get('id')
                email_match = rest_data.get('email') == graphql_data.get('email')
                username_match = rest_data.get('username') == graphql_data.get('username')
                
                if id_match and email_match and username_match:
                    self.results.add_result("REST vs GraphQL Consistency", True)
                else:
                    self.results.add_result("REST vs GraphQL Consistency", False, "Data mismatch between REST and GraphQL")
            else:
                self.results.add_result("REST vs GraphQL Consistency", False, "API call failures")
                
        except Exception as e:
            self.results.add_result("REST vs GraphQL Consistency", False, str(e))
            
        # Step 8.2: Aggregation Consistency  
        try:
            # Get daily balance
            daily_response = requests.get(
                f"{CALORIE_BALANCE_URL}/daily-balances/user/{self.test_user_id}/date/{self.day1_date}",
                timeout=10
            )
            
            # Get hourly data
            hourly_response = requests.get(
                f"{CALORIE_BALANCE_URL}/analytics/hourly",
                params={"user_id": self.test_user_id, "date": self.day1_date},
                timeout=10
            )
            
            if daily_response.status_code == 200 and hourly_response.status_code == 200:
                daily_data = daily_response.json().get('data', {})
                hourly_data = hourly_response.json().get('data', [])
                
                # Sum hourly data
                hourly_consumed_sum = sum(hour.get('calories_consumed', 0) for hour in hourly_data if isinstance(hour, dict))
                hourly_burned_sum = sum(hour.get('calories_burned_exercise', 0) for hour in hourly_data if isinstance(hour, dict))
                
                # Compare with daily totals (with tolerance)
                daily_consumed = daily_data.get('calories_consumed', 0)
                daily_burned = daily_data.get('calories_burned_exercise', 0)
                
                consumed_match = abs(hourly_consumed_sum - daily_consumed) <= 50
                burned_match = abs(hourly_burned_sum - daily_burned) <= 50
                
                if consumed_match and burned_match:
                    self.results.add_result("Aggregation Consistency", True)
                else:
                    details = f"consumed: {hourly_consumed_sum} vs {daily_consumed}, burned: {hourly_burned_sum} vs {daily_burned}"
                    self.results.add_result("Aggregation Consistency", False, f"Aggregation mismatch - {details}")
            else:
                self.results.add_result("Aggregation Consistency", False, "Failed to retrieve comparison data")
                
        except Exception as e:
            self.results.add_result("Aggregation Consistency", False, str(e))
            
    def cleanup_test_data(self):
        """Clean up test data"""
        print(f"\n🧹 CLEANUP: REMOVING TEST DATA")
        print(f"{'='*50}")
        
        cleanup_success = True
        
        # Delete test user (cascades to related data)
        if self.test_user_id:
            try:
                response = requests.delete(f"{USER_MANAGEMENT_URL}/users/{self.test_user_id}", timeout=10)
                if response.status_code in [200, 204, 404]:  # 404 is OK (already deleted)
                    print(f"✅ Test user {self.test_user_id} cleaned up")
                else:
                    print(f"⚠️  Failed to delete test user: HTTP {response.status_code}")
                    cleanup_success = False
            except Exception as e:
                print(f"⚠️  Error during user cleanup: {str(e)}")
                cleanup_success = False
                
        return cleanup_success
        
    def run_complete_test_suite(self):
        """Execute the complete E2E test choreography"""
        print(f"\n{'='*80}")
        print(f"GYMBRO PLATFORM - END-TO-END TEST CHOREOGRAPHY")
        print(f"{'='*80}")
        print(f"Test User ID Suffix: {self.timestamp}")
        print(f"Test Dates: {self.day1_date} → {self.day2_date} → {self.current_date}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # Execute test phases
            if not self.check_service_health():
                print("❌ Service health checks failed. Aborting test suite.")
                return False
                
            if not self.phase1_user_lifecycle():
                print("❌ Phase 1 failed. Aborting test suite.")
                return False
                
            if not self.phase2_metabolic_profile():
                print("⚠️  Phase 2 failed. Continuing with remaining tests.")
                
            if not self.phase3_calorie_goals():
                print("⚠️  Phase 3 failed. Continuing with remaining tests.")
                
            if not self.phase4_calorie_events_simulation():
                print("⚠️  Phase 4 failed. Continuing with remaining tests.")
            else:
                # Only run validation phases if we have data
                self.phase5_daily_balance_validation()
                self.phase6_timeline_analytics()
                
            self.phase7_graphql_federation()
            self.phase8_data_consistency()
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Test suite interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error during test execution: {str(e)}")
        finally:
            # Always attempt cleanup
            self.cleanup_test_data()
            
            # Calculate execution time
            self.results.execution_time = time.time() - start_time
            
            # Show final results
            success = self.results.summary()
            
            if success:
                print(f"\n🎉 ALL TESTS PASSED! GymBro Platform is functioning correctly.")
            else:
                print(f"\n⚠️  Some tests failed. Review the results above.")
                
            return success

if __name__ == "__main__":
    print("Starting GymBro Platform E2E Test Suite...")
    
    # Initialize and run tests
    test_suite = GymBroE2ETest()
    success = test_suite.run_complete_test_suite()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)