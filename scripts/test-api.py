#!/usr/bin/env python3
"""
🏋️ GymBro Platform - API Test Script
====================================

Script per testare le API della piattaforma GymBro.
Verifica registrazione, login, profilo e funzionalità base.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Optional

# Configurazione
BASE_URL = "http://localhost:8001"
TEST_USER = {
    "email": "test@gymbro.app",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "date_of_birth": "1990-01-15T00:00:00Z",
    "gender": "male",
    "height_cm": 175.0,
    "weight_kg": 70.0,
    "activity_level": "moderately_active"
}

class Colors:
    """ANSI color codes per output colorato"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = Colors.NC):
    """Stampa messaggio colorato"""
    print(f"{color}{message}{Colors.NC}")

def print_test_header(test_name: str):
    """Stampa header del test"""
    print_colored(f"\n🧪 Testing: {test_name}", Colors.BLUE)
    print_colored("=" * (len(test_name) + 12), Colors.BLUE)

def print_success(message: str):
    """Stampa messaggio di successo"""
    print_colored(f"✅ {message}", Colors.GREEN)

def print_error(message: str):
    """Stampa messaggio di errore"""
    print_colored(f"❌ {message}", Colors.RED)

def print_warning(message: str):
    """Stampa messaggio di warning"""
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_info(message: str):
    """Stampa messaggio informativo"""
    print_colored(f"ℹ️  {message}", Colors.CYAN)

def make_request(method: str, endpoint: str, data: Optional[Dict] = None, 
                headers: Optional[Dict] = None) -> requests.Response:
    """Effettua una richiesta HTTP con gestione errori"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed to {url}")
        print_info("Make sure the service is running: make start")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print_error(f"Request timeout for {url}")
        sys.exit(1)

def test_health_check():
    """Test health check endpoint"""
    print_test_header("Health Check")
    
    response = make_request("GET", "/health")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Service is healthy: {data.get('status', 'unknown')}")
        print_info(f"Version: {data.get('version', 'unknown')}")
        return True
    else:
        print_error(f"Health check failed: {response.status_code}")
        return False

def test_user_registration():
    """Test user registration"""
    print_test_header("User Registration")
    
    response = make_request("POST", "/auth/register", TEST_USER)
    
    if response.status_code == 201:
        data = response.json()
        print_success("User registered successfully")
        print_info(f"User ID: {data['user']['id']}")
        print_info(f"Email: {data['user']['email']}")
        print_info(f"Token expires in: {data['expires_in']} seconds")
        return data['access_token']
    elif response.status_code == 400:
        error_data = response.json()
        if "già registrata" in error_data.get('detail', ''):
            print_warning("User already exists, will try login")
            return None
        else:
            print_error(f"Registration failed: {error_data.get('detail', 'Unknown error')}")
            return False
    else:
        print_error(f"Registration failed: {response.status_code}")
        return False

def test_user_login():
    """Test user login"""
    print_test_header("User Login")
    
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    response = make_request("POST", "/auth/login", login_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Login successful")
        print_info(f"Token type: {data['token_type']}")
        print_info(f"User role: {data['user']['role']}")
        print_info(f"Is premium: {data['user']['is_premium']}")
        return data['access_token']
    else:
        error_data = response.json()
        print_error(f"Login failed: {error_data.get('detail', 'Unknown error')}")
        return False

def test_profile_access(token: str):
    """Test accessing user profile with token"""
    print_test_header("Profile Access")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = make_request("GET", "/profile", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Profile access successful")
        print_info(f"Name: {data['first_name']} {data['last_name']}")
        print_info(f"Age: {data['age']} years")
        print_info(f"BMI: {calculate_bmi(data['height_cm'], data['weight_kg'])}")
        print_info(f"Activity level: {data['activity_level']}")
        return True
    else:
        print_error(f"Profile access failed: {response.status_code}")
        return False

def test_profile_update(token: str):
    """Test updating user profile"""
    print_test_header("Profile Update")
    
    update_data = {
        "weight_kg": 72.5,
        "activity_level": "very_active"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = make_request("PUT", "/profile", update_data, headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Profile updated successfully")
        print_info(f"New weight: {data['weight_kg']} kg")
        print_info(f"New activity level: {data['activity_level']}")
        return True
    else:
        print_error(f"Profile update failed: {response.status_code}")
        return False

def test_user_stats(token: str):
    """Test getting user statistics"""
    print_test_header("User Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = make_request("GET", "/profile/stats", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Statistics retrieved successfully")
        print_info(f"Total calories burned: {data['total_calories_burned']}")
        print_info(f"Current streak: {data['current_streak']} days")
        print_info(f"BMI: {data['bmi']}")
        print_info(f"Days active: {data['days_active']}")
        return True
    else:
        print_error(f"Statistics access failed: {response.status_code}")
        return False

def test_preferences(token: str):
    """Test user preferences"""
    print_test_header("User Preferences")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get preferences
    response = make_request("GET", "/preferences", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Preferences retrieved successfully")
        print_info(f"Language: {data['language']}")
        print_info(f"Timezone: {data['timezone']}")
        print_info(f"Push notifications: {data['push_notifications']}")
        
        # Update preferences
        update_data = data.copy()
        update_data["push_notifications"] = not data["push_notifications"]
        update_data["meal_reminders"] = True
        
        update_response = make_request("PUT", "/preferences", update_data, headers)
        
        if update_response.status_code == 200:
            print_success("Preferences updated successfully")
            return True
        else:
            print_error("Preferences update failed")
            return False
    else:
        print_error(f"Preferences access failed: {response.status_code}")
        return False

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calcola BMI"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def print_summary(results: Dict[str, bool]):
    """Stampa riepilogo dei test"""
    print_colored("\n🏁 Test Summary", Colors.PURPLE)
    print_colored("=" * 20, Colors.PURPLE)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print_colored(f"\n📊 Results: {passed}/{total} tests passed", Colors.WHITE)
    
    if passed == total:
        print_colored("🎉 All tests passed! GymBro Platform is working correctly!", Colors.GREEN)
        return True
    else:
        print_colored("⚠️  Some tests failed. Check the errors above.", Colors.YELLOW)
        return False

def main():
    """Funzione principale"""
    print_colored("🏋️ GymBro Platform API Tests", Colors.WHITE)
    print_colored("=" * 35, Colors.WHITE)
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test health check
    results["Health Check"] = test_health_check()
    if not results["Health Check"]:
        print_error("Health check failed, stopping tests")
        sys.exit(1)
    
    # Test registration (or get existing token)
    token = test_user_registration()
    if token is False:
        results["User Registration"] = False
        sys.exit(1)
    elif token is None:
        # User exists, try login
        token = test_user_login()
        results["User Registration"] = True  # Existing user is OK
        if not token:
            results["User Login"] = False
            sys.exit(1)
        else:
            results["User Login"] = True
    else:
        results["User Registration"] = True
        results["User Login"] = True  # Registration includes login
    
    # Test authenticated endpoints
    results["Profile Access"] = test_profile_access(token)
    results["Profile Update"] = test_profile_update(token)
    results["User Statistics"] = test_user_stats(token)
    results["User Preferences"] = test_preferences(token)
    
    # Print summary
    success = print_summary(results)
    
    if success:
        print_colored("\n💡 Next steps:", Colors.CYAN)
        print_info("1. Open GraphQL playground: http://localhost:8000/docs")
        print_info("2. Explore n8n workflows: http://localhost:5678")
        print_info("3. Check monitoring: make monitor")
        print_info("4. Run integration tests: make test-integration")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
