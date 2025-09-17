"""
Extended GraphQL Types for Calorie Balance Service

Complete GraphQL schema including Goals, Events, Balance, and Analytics types
for Apollo Federation v2.5.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

import strawberry

# =============================================================================
# CALORIE GOALS GRAPHQL TYPES
# =============================================================================


@strawberry.enum
class GoalTypeEnum(Enum):
    """GraphQL enum for goal types."""

    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTAIN_WEIGHT = "maintain_weight"
    MUSCLE_GAIN = "muscle_gain"
    PERFORMANCE = "performance"


@strawberry.federation.type(keys=["id"])
class CalorieGoalType:
    """GraphQL type for calorie goals with federation support."""

    id: strawberry.ID
    user_id: str
    goal_type: GoalTypeEnum
    daily_calorie_target: float
    daily_deficit_target: Optional[float] = None
    weekly_weight_change_kg: Optional[float] = None

    # Timeline
    start_date: str  # ISO date string
    end_date: Optional[str] = None
    is_active: bool

    # AI optimization
    ai_optimized: bool
    optimization_metadata: Optional[str] = None  # JSON string

    # Timestamps
    created_at: datetime
    updated_at: datetime

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve entity reference for Apollo Federation."""
        pass


@strawberry.input
class CreateCalorieGoalInput:
    """Input type for creating calorie goals."""

    goal_type: GoalTypeEnum
    daily_calorie_target: float
    daily_deficit_target: Optional[float] = None
    weekly_weight_change_kg: Optional[float] = None
    start_date: str
    end_date: Optional[str] = None


@strawberry.input
class UpdateCalorieGoalInput:
    """Input type for updating calorie goals."""

    goal_type: Optional[GoalTypeEnum] = None
    daily_calorie_target: Optional[float] = None
    daily_deficit_target: Optional[float] = None
    weekly_weight_change_kg: Optional[float] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.type
class CalorieGoalResponse:
    """Response type for calorie goal operations."""

    success: bool
    message: str
    data: Optional[CalorieGoalType] = None


@strawberry.type
class CalorieGoalListResponse:
    """Response type for calorie goal list operations."""

    success: bool
    message: str
    data: List[CalorieGoalType]
    total: int


# =============================================================================
# CALORIE EVENTS GRAPHQL TYPES
# =============================================================================


@strawberry.enum
class EventTypeEnum(Enum):
    """GraphQL enum for event types."""

    CONSUMED = "consumed"
    BURNED_EXERCISE = "burned_exercise"
    BURNED_BMR = "burned_bmr"
    WEIGHT = "weight"


@strawberry.enum
class EventSourceEnum(Enum):
    """GraphQL enum for event sources."""

    MANUAL = "manual"
    FITNESS_TRACKER = "fitness_tracker"
    SMART_SCALE = "smart_scale"
    NUTRITION_SCAN = "nutrition_scan"
    HEALTHKIT = "healthkit"
    GOOGLE_FIT = "google_fit"


@strawberry.federation.type(keys=["id"])
class CalorieEventType:
    """GraphQL type for calorie events with federation support."""

    id: strawberry.ID
    user_id: str
    event_type: EventTypeEnum
    event_timestamp: datetime
    value: float

    # Data quality
    source: EventSourceEnum
    confidence_score: float

    # Context
    metadata: Optional[str] = None  # JSON string

    # Timestamps (updated_at added in 004_alter_tables.sql)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve entity reference for Apollo Federation."""
        pass


@strawberry.input
class CreateCalorieEventInput:
    """Input type for creating calorie events."""

    event_type: EventTypeEnum
    value: float
    event_timestamp: Optional[str] = None  # ISO datetime string
    source: EventSourceEnum = EventSourceEnum.MANUAL
    confidence_score: Optional[float] = None
    metadata: Optional[str] = None  # JSON string


@strawberry.type
class CalorieEventResponse:
    """Response type for calorie event operations."""

    success: bool
    message: str
    data: Optional[CalorieEventType] = None


@strawberry.type
class CalorieEventListResponse:
    """Response type for calorie event list operations."""

    success: bool
    message: str
    data: List[CalorieEventType]
    total: int


# =============================================================================
# DAILY BALANCE GRAPHQL TYPES
# =============================================================================


@strawberry.federation.type(keys=["id"])
class DailyBalanceType:
    """GraphQL type for daily balance with federation support."""

    id: strawberry.ID
    user_id: str
    date: str  # ISO date string

    # Calorie aggregations
    calories_consumed: float
    calories_burned_exercise: float
    calories_burned_bmr: float
    net_calories: float

    # Weight tracking
    morning_weight_kg: Optional[float] = None
    evening_weight_kg: Optional[float] = None

    # Event metadata
    events_count: int
    last_event_timestamp: Optional[datetime] = None
    data_completeness_score: float

    # Goal tracking
    daily_calorie_target: Optional[float] = None
    target_deviation: Optional[float] = None
    progress_percentage: Optional[float] = None  # Calculated progress

    # Timestamps
    created_at: datetime
    updated_at: datetime

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve entity reference for Apollo Federation."""
        pass


@strawberry.type
class DailyBalanceResponse:
    """Response type for daily balance operations."""

    success: bool
    message: str
    data: Optional[DailyBalanceType] = None


@strawberry.type
class DailyBalanceListResponse:
    """Response type for daily balance list operations."""

    success: bool
    message: str
    data: List[DailyBalanceType]
    total: int


# =============================================================================
# METABOLIC PROFILES GRAPHQL TYPES
# =============================================================================


@strawberry.enum
class ActivityLevelEnum(Enum):
    """GraphQL enum for activity levels."""

    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


@strawberry.federation.type(keys=["id"])
@strawberry.type
@strawberry.federation.type(keys=["id"])
class MetabolicProfileType:
    """GraphQL type for metabolic profiles - matches entity exactly."""

    # Base entity fields
    id: strawberry.ID
    created_at: datetime
    updated_at: datetime
    user_id: str

    # Calculated metabolic rates
    bmr_calories: float
    tdee_calories: float
    rmr_calories: Optional[float] = None

    # Calculation method and accuracy
    calculation_method: str
    accuracy_score: float

    # Activity multipliers for different levels
    sedentary_multiplier: float
    light_multiplier: float
    moderate_multiplier: float
    high_multiplier: float
    extreme_multiplier: float

    # Activity level (added in 006_fix_schema_task_1_1.sql)
    activity_level: Optional[str] = None

    # AI learning data
    ai_adjusted: bool
    adjustment_factor: float
    learning_iterations: int

    # Validity period
    calculated_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve entity reference for Apollo Federation."""
        pass


@strawberry.input
class MetabolicCalculationInput:
    """Input type for metabolic calculations."""

    weight_kg: float
    height_cm: float
    age: int
    gender: str  # male/female/other
    activity_level: ActivityLevelEnum


@strawberry.type
class MetabolicProfileResponse:
    """Response type for metabolic profile operations."""

    success: bool
    message: str
    data: Optional[MetabolicProfileType] = None


# =============================================================================
# TIMELINE ANALYTICS GRAPHQL TYPES
# =============================================================================


@strawberry.type
class HourlyDataPointType:
    """GraphQL type for hourly analytics data points."""

    hour: int
    date: str  # ISO date string
    calories_consumed: float
    calories_burned_exercise: float
    calories_burned_bmr: float
    net_calories: float
    weight_kg: Optional[float] = None
    event_count: int
    data_quality: float


@strawberry.type
class DailyDataPointType:
    """GraphQL type for daily analytics data points."""

    date: str  # ISO date string
    calories_consumed: float
    calories_burned_exercise: float
    calories_burned_bmr: float
    net_calories: float
    morning_weight_kg: Optional[float] = None
    evening_weight_kg: Optional[float] = None
    goal_target: Optional[float] = None
    goal_deviation: Optional[float] = None
    trend_direction: Optional[str] = None
    active_hours: int


@strawberry.type
class WeeklyDataPointType:
    """GraphQL type for weekly analytics data points."""

    week_start: str  # ISO date string
    week_end: str  # ISO date string
    avg_daily_consumed: float
    avg_daily_burned: float
    avg_net_calories: float
    total_weight_change: Optional[float] = None
    active_days: int
    goal_adherence_pct: Optional[float] = None


@strawberry.type
class BehavioralPatternType:
    """GraphQL type for behavioral patterns."""

    pattern_id: str
    pattern_type: str
    description: str
    confidence_score: float
    frequency: str
    impact_score: Optional[float] = None
    recommendations: Optional[List[str]] = None


@strawberry.type
class HourlyAnalyticsResponse:
    """GraphQL response for hourly analytics."""

    success: bool
    message: str
    data: List[HourlyDataPointType]
    metadata: Optional[str] = None  # JSON string


@strawberry.type
class DailyAnalyticsResponse:
    """GraphQL response for daily analytics."""

    success: bool
    message: str
    data: List[DailyDataPointType]
    metadata: Optional[str] = None  # JSON string


@strawberry.type
class WeeklyAnalyticsResponse:
    """GraphQL response for weekly analytics."""

    success: bool
    message: str
    data: List[WeeklyDataPointType]
    metadata: Optional[str] = None  # JSON string


@strawberry.type
class PatternAnalyticsResponse:
    """GraphQL response for pattern analytics."""

    success: bool
    message: str
    data: List[BehavioralPatternType]
    metadata: Optional[str] = None  # JSON string
