"""
Domain Entities - Calorie Balance Service

Core business entities for the event-driven calorie tracking domain.
Event-driven architecture with high-frequency smartphone data collection.

Cross-Schema Architecture:
- User entities managed by user-management service (single source of truth)
- Local entities use UUID foreign keys to user_management.users
- Focus on calorie events, goals, and metabolic calculations
"""

from datetime import date as DateType  # Avoid name conflict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class BaseEntity(BaseModel):
    """Base entity with common fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# ENUMS - Domain Value Objects
# =============================================================================


class EventType(str, Enum):
    """Types of calorie events for event-driven tracking."""

    CONSUMED = "consumed"
    BURNED_EXERCISE = "burned_exercise"
    BURNED_BMR = "burned_bmr"
    WEIGHT = "weight"


class EventSource(str, Enum):
    """Sources of calorie event data."""

    MANUAL = "manual"
    FITNESS_TRACKER = "fitness_tracker"
    SMART_SCALE = "smart_scale"
    NUTRITION_SCAN = "nutrition_scan"
    HEALTHKIT = "healthkit"
    GOOGLE_FIT = "google_fit"


class GenderType(str, Enum):
    """Gender types for metabolic calculations."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    """Activity levels for TDEE calculations."""

    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class GoalType(str, Enum):
    """Types of calorie goals."""

    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTAIN_WEIGHT = "maintain_weight"
    MUSCLE_GAIN = "muscle_gain"
    PERFORMANCE = "performance"


# =============================================================================
# CORE ENTITIES - Event-Driven Architecture
# =============================================================================
# NOTE: User entity is managed by user-management service (cross-schema FK)
# This service focuses on calorie events and metabolic calculations


class CalorieEvent(BaseEntity):
    """🔥 HIGH-FREQUENCY EVENT - Core of event-driven architecture."""

    user_id: UUID = Field(
        ..., description="User ID (cross-schema FK to user_management.users)"
    )
    event_type: EventType = Field(..., description="Type of calorie event")
    event_timestamp: datetime = Field(
        ..., description="Precise event timestamp (second precision)"
    )
    value: Decimal = Field(..., ge=0, description="Calorie value or weight measurement")

    # Data quality and provenance
    source: EventSource = Field(EventSource.MANUAL, description="Data source")
    confidence_score: Decimal = Field(
        Decimal("1.0"), ge=0, le=1, description="Data quality score 0.0-1.0"
    )

    # Additional context
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional event context"
    )

    @validator("value")
    def validate_value_by_type(cls, v, values):
        """Validate value ranges based on event type."""
        event_type = values.get("event_type")
        if event_type == EventType.CONSUMED and v > 3000:
            raise ValueError("Single meal calories cannot exceed 3000")
        elif (
            event_type in [EventType.BURNED_EXERCISE, EventType.BURNED_BMR] and v > 2000
        ):
            raise ValueError("Burned calories per event cannot exceed 2000")
        elif event_type == EventType.WEIGHT and (v < 20 or v > 500):
            raise ValueError("Weight must be between 20kg and 500kg")
        return v


class CalorieGoal(BaseEntity):
    """Dynamic calorie goals with AI optimization support."""

    user_id: UUID = Field(
        ..., description="User ID (cross-schema FK to user_management.users)"
    )
    goal_type: GoalType = Field(..., description="Type of calorie goal")
    daily_calorie_target: Decimal = Field(
        ..., ge=800, le=5000, description="Daily calorie target"
    )
    daily_deficit_target: Optional[Decimal] = Field(
        None, ge=-1500, le=1500, description="Daily deficit/surplus"
    )
    weekly_weight_change_kg: Optional[Decimal] = Field(
        None, ge=-2, le=2, description="Target weight change per week"
    )

    # Timeline
    start_date: DateType = Field(..., description="Goal start date")
    end_date: Optional[DateType] = Field(
        None, description="Goal end date (None for ongoing)"
    )
    is_active: bool = Field(True, description="Whether goal is currently active")

    # AI optimization
    ai_optimized: bool = Field(False, description="Whether goal is AI-optimized")
    optimization_metadata: Optional[Dict[str, Any]] = Field(
        None, description="AI optimization data"
    )

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Ensure end_date is after start_date."""
        start_date = values.get("start_date")
        if v and start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v


class DailyBalance(BaseEntity):
    """Daily aggregated balance for performance optimization."""

    user_id: UUID = Field(
        ..., description="User ID (cross-schema FK to user_management.users)"
    )
    date: DateType = Field(..., description="Balance date")

    # Calorie aggregations
    calories_consumed: Decimal = Field(
        Decimal("0"), ge=0, description="Total calories consumed"
    )
    calories_burned_exercise: Decimal = Field(
        Decimal("0"), ge=0, description="Calories burned through exercise"
    )
    calories_burned_bmr: Decimal = Field(
        Decimal("0"), ge=0, description="BMR calories burned"
    )
    net_calories: Decimal = Field(
        ..., description="Net calorie balance (consumed - burned)"
    )

    # Weight tracking
    morning_weight_kg: Optional[Decimal] = Field(
        None, description="Morning weight measurement"
    )
    evening_weight_kg: Optional[Decimal] = Field(
        None, description="Evening weight measurement"
    )

    # Event metadata
    events_count: int = Field(0, ge=0, description="Number of events aggregated")
    last_event_timestamp: Optional[datetime] = Field(
        None, description="Last event processed"
    )

    # Data quality
    data_completeness_score: Decimal = Field(
        Decimal("0"), ge=0, le=1, description="Completeness score"
    )

    @property
    def total_calories_burned(self) -> Decimal:
        """Calculate total calories burned (exercise + BMR)."""
        return self.calories_burned_exercise + self.calories_burned_bmr


class MetabolicProfile(BaseModel):
    """Metabolic profile matching database schema."""

    id: UUID
    user_id: UUID = Field(
        ..., description="User ID (cross-schema FK to user_management.users)"
    )

    # Calculated metabolic rates
    bmr_calories: Decimal = Field(..., gt=0, description="Basal Metabolic Rate")
    tdee_calories: Decimal = Field(
        ..., gt=0, description="Total Daily Energy Expenditure"
    )
    rmr_calories: Optional[Decimal] = Field(
        None, gt=0, description="Resting Metabolic Rate (if measured)"
    )

    # Calculation method and accuracy
    calculation_method: str = Field(
        default="mifflin_st_jeor", description="BMR calculation method"
    )
    accuracy_score: Decimal = Field(
        default=Decimal("0.8"), ge=0, le=1, description="Estimated accuracy (0.0-1.0)"
    )

    # Activity multipliers for different levels (from 001_initial_schema.sql)
    sedentary_multiplier: Decimal = Field(
        default=Decimal("1.2"), gt=0, le=2, description="Sedentary activity multiplier"
    )
    light_multiplier: Decimal = Field(
        default=Decimal("1.375"), gt=0, le=2, description="Light activity multiplier"
    )
    moderate_multiplier: Decimal = Field(
        default=Decimal("1.55"), gt=0, le=2, description="Moderate activity multiplier"
    )
    high_multiplier: Decimal = Field(
        default=Decimal("1.725"), gt=0, le=2, description="High activity multiplier"
    )
    extreme_multiplier: Decimal = Field(
        default=Decimal("1.9"), gt=0, le=2, description="Extreme activity multiplier"
    )

    # Activity level (added in 006_fix_schema_task_1_1.sql)
    activity_level: Optional[str] = Field(
        None, description=("Activity level: sedentary, light, moderate, high, extreme")
    )

    # AI learning data (from 001_initial_schema.sql)
    ai_adjusted: bool = Field(
        default=False, description="Whether AI has adjusted the calculations"
    )
    adjustment_factor: Decimal = Field(
        default=Decimal("1.000"), ge=0.5, le=2, description="AI correction factor"
    )
    learning_iterations: int = Field(
        default=0, ge=0, description="Number of AI learning iterations"
    )

    # Validity period (from 001_initial_schema.sql)
    calculated_at: datetime = Field(
        default_factory=datetime.now, description="When calculation was performed"
    )
    expires_at: Optional[datetime] = Field(
        None, description="When this profile expires"
    )
    is_active: bool = Field(
        default=True, description="Whether this profile is currently active"
    )


# =============================================================================
# ANALYTICS VALUE OBJECTS - Read-Only Projections
# =============================================================================


class HourlyCalorieSummary(BaseModel):
    """Hourly calorie aggregation from temporal view."""

    user_id: UUID
    date: DateType
    hour: int
    calories_consumed: Decimal
    calories_burned_exercise: Decimal
    calories_burned_bmr: Decimal
    net_calories: Decimal
    weight_kg: Optional[Decimal]
    event_count: int
    avg_confidence: Optional[Decimal]


class DailyCalorieSummary(BaseModel):
    """Daily calorie aggregation from temporal view."""

    user_id: UUID
    date: DateType
    calories_consumed: Decimal
    calories_burned_exercise: Decimal
    calories_burned_bmr: Decimal
    net_calories: Decimal
    morning_weight_kg: Optional[Decimal]
    evening_weight_kg: Optional[Decimal]
    event_count: int
    active_hours: int
    daily_calorie_target: Optional[Decimal]


class WeeklyCalorieSummary(BaseModel):
    """Weekly calorie aggregation from temporal view."""

    user_id: UUID
    week_start: DateType
    week_end: DateType
    year: int
    week_number: int
    weekly_calories_consumed: Decimal
    weekly_calories_burned_exercise: Decimal
    weekly_calories_burned_bmr: Decimal
    weekly_net_calories: Decimal
    avg_daily_consumed: Decimal
    avg_daily_burned: Decimal
    week_start_weight: Optional[Decimal]
    week_end_weight: Optional[Decimal]
    active_days: int


class MonthlyCalorieSummary(BaseModel):
    """Monthly calorie aggregation from temporal view."""

    user_id: UUID
    month_start: DateType
    month_end: DateType
    year: int
    month: int
    month_label: str
    monthly_calories_consumed: Decimal
    monthly_calories_burned_exercise: Decimal
    monthly_calories_burned_bmr: Decimal
    monthly_net_calories: Decimal
    avg_daily_consumed: Decimal
    avg_weekly_consumed: Decimal
    month_start_weight: Optional[Decimal]
    month_end_weight: Optional[Decimal]
    active_days: int
    active_weeks: int


class DailyBalanceSummary(BaseModel):
    """Daily balance with goal comparison from temporal view."""

    user_id: UUID
    date: DateType
    calories_consumed: Decimal
    calories_burned_exercise: Decimal
    calories_burned_bmr: Decimal
    net_calories: Decimal
    morning_weight: Optional[Decimal]
    evening_weight: Optional[Decimal]
    avg_weight: Optional[Decimal]
    daily_weight_change: Optional[Decimal]
    daily_calorie_target: Optional[Decimal]
    daily_deficit_target: Optional[Decimal]
    goal_type: Optional[str]
    target_deviation: Optional[Decimal]
    goal_achieved: Optional[bool]
    data_completeness_score: Decimal
