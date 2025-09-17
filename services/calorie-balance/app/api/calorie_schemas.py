"""
Calorie Balance API Schemas - Pydantic Models
=============================================
Service: calorie-balance
Schema: calorie_balance
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities import (
    CalorieEvent,
    CalorieGoal,
    DailyBalance,
    EventSource,
    EventType,
    GoalType,
)

# =============================================================================
# DAILY BALANCE SCHEMAS
# =============================================================================


class DailyBalanceResponse(BaseModel):
    """Daily balance response schema."""

    user_id: str
    date: date
    calories_consumed: Decimal
    calories_burned: Decimal
    net_calories: Decimal
    daily_goal: Decimal
    progress_percentage: float
    weight_kg: Optional[Decimal] = None
    metabolic_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        json_encoders = {Decimal: str}

    @classmethod
    def from_entity(cls, balance: DailyBalance) -> "DailyBalanceResponse":
        """Create response from DailyBalance entity."""
        return cls(
            user_id=balance.user_id,
            date=balance.date,
            calories_consumed=balance.calories_consumed,
            calories_burned=balance.calories_burned,
            net_calories=balance.net_calories,
            daily_goal=balance.daily_goal or Decimal("0"),
            progress_percentage=balance.progress_percentage or 0.0,
            weight_kg=balance.weight_kg,
            metabolic_data=balance.metadata or {},
        )


class ProgressResponse(BaseModel):
    """Progress tracking response schema."""

    date: date
    calories_consumed: Decimal
    calories_burned: Decimal
    net_calories: Decimal
    daily_goal: Decimal
    progress_percentage: float
    weight_kg: Optional[Decimal] = None

    class Config:
        from_attributes = True
        json_encoders = {Decimal: str}


# =============================================================================
# CALORIE GOAL SCHEMAS
# =============================================================================


class GoalTypeEnum(str, Enum):
    """Goal type for API responses."""

    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"


class CalorieGoalResponse(BaseModel):
    """Calorie goal response schema."""

    id: str
    user_id: str
    goal_type: GoalTypeEnum
    daily_calorie_target: Decimal
    daily_deficit_target: Optional[Decimal] = None
    weekly_weight_change_kg: Optional[Decimal] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    ai_optimized: bool
    optimization_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        }

    @classmethod
    def from_entity(cls, goal: CalorieGoal) -> "CalorieGoalResponse":
        """Create response from CalorieGoal entity."""
        return cls(
            id=str(goal.id),
            user_id=str(goal.user_id),
            goal_type=GoalTypeEnum(goal.goal_type.value),
            daily_calorie_target=goal.daily_calorie_target,
            daily_deficit_target=goal.daily_deficit_target,
            weekly_weight_change_kg=goal.weekly_weight_change_kg,
            start_date=goal.start_date,
            end_date=goal.end_date,
            is_active=goal.is_active,
            ai_optimized=goal.ai_optimized,
            optimization_metadata=goal.optimization_metadata or {},
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )


class CalorieGoalCreateRequest(BaseModel):
    """Request schema for creating calorie goal with Parameter Passing support."""

    goal_type: GoalTypeEnum
    target_weight_kg: Optional[Decimal] = None
    target_date: Optional[date] = None
    weekly_weight_change_kg: Optional[Decimal] = None
    activity_level: str = "moderate"
    custom_calorie_target: Optional[Decimal] = None

    # Parameter Passing - User metrics provided by client (optional)
    user_weight_kg: Optional[Decimal] = Field(None, description="Current weight in kg")
    user_height_cm: Optional[Decimal] = Field(None, description="Height in cm")
    user_age: Optional[int] = Field(None, description="Age in years")
    user_gender: Optional[str] = Field(None, description="Gender: male, female, other")

    class Config:
        json_schema_extra = {
            "example": {
                "goal_type": "weight_loss",
                "target_weight_kg": "70.0",
                "target_date": "2025-12-31",
                "weekly_weight_change_kg": "0.5",
                "activity_level": "moderate",
                "user_weight_kg": "80.0",
                "user_height_cm": "175.0",
                "user_age": 30,
                "user_gender": "male",
            }
        }


class CalorieGoalUpdateRequest(BaseModel):
    """Request schema for updating calorie goal."""

    goal_type: Optional[GoalTypeEnum] = None
    daily_calorie_target: Optional[Decimal] = None
    daily_deficit_target: Optional[Decimal] = None
    weekly_weight_change_kg: Optional[Decimal] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "daily_calorie_target": "2000.0",
                "weekly_weight_change_kg": "0.3",
                "is_active": True,
            }
        }


# =============================================================================
# ERROR AND UTILITY SCHEMAS
# =============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str = "healthy"
    service: str = "calorie-balance"
    timestamp: datetime
    database_status: str = "connected"

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "calorie-balance",
                "timestamp": "2025-09-12T00:00:00Z",
                "database_status": "connected",
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Invalid input data",
                "code": 400,
                "details": {"field": "value"},
            }
        }
