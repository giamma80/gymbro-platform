"""
Test per models/schemas
"""
import pytest
from pydantic import ValidationError
from models import (
    UserRegistration,
    UserProfile,
    UserPreferences,
    Gender,
    ActivityLevel,
    UserRole,
)
from datetime import datetime


class TestUserModels:
    """Test per Pydantic models."""

    def test_user_registration_valid(self):
        """Test valid user registration."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "height_cm": 180,
            "weight_kg": 75.5,
            "activity_level": "moderately_active",
        }
        
        user = UserRegistration(**user_data)
        assert user.email == "test@example.com"
        assert user.gender == Gender.MALE
        assert user.activity_level == ActivityLevel.MODERATELY_ACTIVE

    def test_user_registration_invalid_email(self):
        """Test invalid email in registration."""
        user_data = {
            "email": "invalid-email",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "gender": "MALE",
            "height_cm": 180,
            "weight_kg": 75.5,
            "activity_level": "MODERATELY_ACTIVE",
        }
        
        with pytest.raises(ValidationError):
            UserRegistration(**user_data)

    def test_user_preferences_defaults(self):
        """Test user preferences with defaults."""
        prefs = UserPreferences()
        
        assert prefs.timezone == "Europe/Rome"
        assert prefs.language == "it"
        assert prefs.push_notifications is True
        assert prefs.weight_unit == "kg"
        assert prefs.distance_unit == "km"

    def test_enum_values(self):
        """Test enum values."""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert ActivityLevel.SEDENTARY.value == "sedentary"
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"
