from typing import Optional
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import date as date_type, datetime
from decimal import Decimal
import re

from ..domain.entities import ActivityLevel, Gender, GoalType


# User Schemas
class UserCreateRequest(BaseModel):
    """Request schema for creating a user"""
    user_id: str = Field(..., description="User unique identifier")
    username: str = Field(..., min_length=3, max_length=100, description="Username (unique, min 3 chars)")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        if not v:
            raise ValueError('Email is required')
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        
        return v.lower()


class UserUpdateRequest(BaseModel):
    """Request schema for updating user profile"""
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[Gender] = None
    height_cm: Optional[Decimal] = Field(None, ge=50, le=300)
    weight_kg: Optional[Decimal] = Field(None, ge=20, le=500)
    activity_level: Optional[ActivityLevel] = None

    @validator('gender', pre=True)
    def validate_gender(cls, v):
        """Accept case-insensitive gender values"""
        if v is None:
            return v
        if isinstance(v, str):
            # Convert common variations to proper enum values
            gender_map = {
                'male': Gender.MALE,
                'MALE': Gender.MALE,
                'Male': Gender.MALE,
                'female': Gender.FEMALE,
                'FEMALE': Gender.FEMALE,
                'Female': Gender.FEMALE,
                'other': Gender.OTHER,
                'OTHER': Gender.OTHER,
                'Other': Gender.OTHER,
            }
            return gender_map.get(v, v)
        return v

    @validator('activity_level', pre=True)
    def validate_activity_level(cls, v):
        """Accept case-insensitive and common variations for activity level"""
        if v is None:
            return v
        if isinstance(v, str):
            # Convert common variations to proper enum values
            activity_map = {
                'sedentary': ActivityLevel.SEDENTARY,
                'SEDENTARY': ActivityLevel.SEDENTARY,
                'Sedentary': ActivityLevel.SEDENTARY,
                'lightly_active': ActivityLevel.LIGHTLY_ACTIVE,
                'LIGHTLY_ACTIVE': ActivityLevel.LIGHTLY_ACTIVE,
                'Lightly_Active': ActivityLevel.LIGHTLY_ACTIVE,
                'light': ActivityLevel.LIGHTLY_ACTIVE,
                'LIGHT': ActivityLevel.LIGHTLY_ACTIVE,
                'moderately_active': ActivityLevel.MODERATELY_ACTIVE,
                'MODERATELY_ACTIVE': ActivityLevel.MODERATELY_ACTIVE,
                'Moderately_Active': ActivityLevel.MODERATELY_ACTIVE,
                'moderate': ActivityLevel.MODERATELY_ACTIVE,
                'MODERATE': ActivityLevel.MODERATELY_ACTIVE,
                'Moderate': ActivityLevel.MODERATELY_ACTIVE,
                'very_active': ActivityLevel.VERY_ACTIVE,
                'VERY_ACTIVE': ActivityLevel.VERY_ACTIVE,
                'Very_Active': ActivityLevel.VERY_ACTIVE,
                'high': ActivityLevel.VERY_ACTIVE,
                'HIGH': ActivityLevel.VERY_ACTIVE,
                'extra_active': ActivityLevel.EXTRA_ACTIVE,
                'EXTRA_ACTIVE': ActivityLevel.EXTRA_ACTIVE,
                'Extra_Active': ActivityLevel.EXTRA_ACTIVE,
                'extreme': ActivityLevel.EXTRA_ACTIVE,
                'EXTREME': ActivityLevel.EXTRA_ACTIVE,
            }
            return activity_map.get(v, v)
        return v


class UserResponse(BaseModel):
    """Response schema for user data"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[Gender]
    height_cm: Optional[Decimal]
    weight_kg: Optional[Decimal]
    activity_level: Optional[ActivityLevel]
    is_active: bool

    class Config:
        from_attributes = True


# Calorie Goal Schemas
class CalorieGoalCreateRequest(BaseModel):
    """Request schema for creating a calorie goal"""
    goal_type: GoalType
    target_weight_kg: Optional[Decimal] = Field(None, ge=20, le=500)
    weekly_weight_change_kg: Decimal = Field(Decimal('0.0'), ge=-2, le=2)
    start_date: Optional[date_type] = None


class CalorieGoalResponse(BaseModel):
    """Response schema for calorie goal data"""
    id: str
    user_id: str
    goal_type: GoalType
    target_calories: Decimal
    target_weight_kg: Optional[Decimal]
    weekly_weight_change_kg: Decimal
    start_date: date_type
    end_date: Optional[date_type]
    is_active: bool

    class Config:
        from_attributes = True


# Daily Balance Schemas
class DailyBalanceUpdateRequest(BaseModel):
    """Request schema for updating daily balance"""
    date: Optional[date_type] = None
    calories_consumed: Optional[Decimal] = Field(None, ge=0, le=10000)
    calories_burned_exercise: Optional[Decimal] = Field(None, ge=0, le=5000)
    weight_kg: Optional[Decimal] = Field(None, ge=20, le=500)
    notes: Optional[str] = Field(None, max_length=500)


class DailyBalanceResponse(BaseModel):
    """Response schema for daily balance data"""
    id: str
    user_id: str
    date: date_type
    calories_consumed: Decimal
    calories_burned_exercise: Decimal
    calories_burned_bmr: Optional[Decimal]
    net_calories: Decimal
    weight_kg: Optional[Decimal]
    notes: Optional[str]

    class Config:
        from_attributes = True


# Progress Schemas
class ProgressRequest(BaseModel):
    """Request schema for progress data"""
    start_date: date_type
    end_date: date_type


class MetabolicProfileResponse(BaseModel):
    """Response schema for metabolic profile"""
    id: str
    user_id: str
    bmr: Decimal
    tdee: Decimal
    calculated_at: date_type
    valid_until: date_type
    is_valid: bool = True

    class Config:
        from_attributes = True


# Calorie Event Schemas
class CalorieEventCreate(BaseModel):
    """Request schema for creating a calorie event (consumed, burned, weight, batch)"""
    user_id: str
    event_type: str  # 'consumed', 'burned', 'weight', 'batch'
    calories: Optional[Decimal] = Field(None, ge=0, le=10000)
    weight_kg: Optional[Decimal] = Field(None, ge=20, le=500)
    timestamp: datetime
    notes: Optional[str] = Field(None, max_length=500)


class CalorieEventRead(BaseModel):
    """Response schema for reading a calorie event"""
    id: str
    user_id: str
    event_type: str
    calories: Optional[Decimal]
    weight_kg: Optional[Decimal]
    timestamp: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True
