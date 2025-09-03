"""
Pydantic Models for Analytics Service
Shared models between REST and GraphQL APIs - DUAL ARCHITECTURE
"""

from datetime import date as date_type, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ===== ENUMS =====

class TimeRangeType(str, Enum):
    """Time range types for analytics queries"""
    TODAY = "TODAY"
    YESTERDAY = "YESTERDAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"
    ALL_TIME = "ALL_TIME"


class TrendDirection(str, Enum):
    """Trend direction indicators"""
    UP = "UP"
    DOWN = "DOWN"
    STABLE = "STABLE"
    NO_DATA = "NO_DATA"


class ActivityIntensity(str, Enum):
    """Activity intensity levels"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


# ===== BASE MODELS =====

class BaseAnalyticsModel(BaseModel):
    """Base model with standard configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )


# ===== CORE MODELS =====

class DailyStatsRecord(BaseAnalyticsModel):
    """Daily statistics record - granular fitness data"""
    user_id: str = Field(..., description="User identifier")
    date: date_type = Field(..., description="Statistics date")
    
    # Calorie tracking
    calories_burned: float = Field(0, ge=0, description="Calories burned")
    calories_consumed: float = Field(0, ge=0, description="Calories consumed")
    calories_deficit: float = Field(0, description="Calorie deficit/surplus")
    
    # Activity tracking
    active_minutes: int = Field(0, ge=0, description="Active minutes")
    steps_count: int = Field(0, ge=0, description="Daily steps")
    workouts_completed: int = Field(0, ge=0, description="Workouts completed")
    activity_intensity: ActivityIntensity = Field(
        ActivityIntensity.LOW,
        description="Activity intensity level"
    )
    
    # Optional metrics
    weight_kg: Optional[float] = Field(None, gt=0, description="Weight in kg")
    sleep_hours: Optional[float] = Field(
        None, 
        ge=0, 
        le=24, 
        description="Sleep hours"
    )
    
    # Data quality
    data_completeness: float = Field(
        0, 
        ge=0, 
        le=1, 
        description="Data completeness score"
    )
    is_active_day: bool = Field(False, description="Active day flag")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TimeRangeStats(BaseAnalyticsModel):
    """Aggregated statistics for time periods"""
    time_range: TimeRangeType = Field(..., description="Time range type")
    start_date: date_type = Field(..., description="Period start date")
    end_date: date_type = Field(..., description="Period end date")
    total_days: int = Field(..., ge=1, description="Total days in period")
    
    # Calorie aggregates
    total_calories_burned: float = Field(0, ge=0)
    total_calories_consumed: float = Field(0, ge=0)
    avg_daily_calories_burned: float = Field(0, ge=0)
    avg_daily_calories_consumed: float = Field(0, ge=0)
    avg_daily_deficit: float = Field(0)
    
    # Activity aggregates
    total_active_minutes: int = Field(0, ge=0)
    total_steps: int = Field(0, ge=0)
    total_workouts: int = Field(0, ge=0)
    active_days_count: int = Field(0, ge=0)
    activity_percentage: float = Field(0, ge=0, le=1)
    avg_daily_steps: float = Field(0, ge=0)
    
    # Weight tracking
    weight_start_kg: Optional[float] = Field(None, gt=0)
    weight_end_kg: Optional[float] = Field(None, gt=0)
    weight_change_kg: Optional[float] = None
    
    # Sleep
    avg_sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    
    # Trends
    calories_trend: TrendDirection = TrendDirection.NO_DATA
    weight_trend: TrendDirection = TrendDirection.NO_DATA
    activity_trend: TrendDirection = TrendDirection.NO_DATA
    
    # Data quality
    data_completeness: float = Field(0, ge=0, le=1)
    days_with_data: int = Field(0, ge=0)


class UserDashboard(BaseAnalyticsModel):
    """Complete user dashboard with multi-timeframe analytics"""
    user_id: str = Field(..., description="User identifier")
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Dashboard generation timestamp"
    )
    
    # Current status
    current_weight_kg: Optional[float] = Field(None, gt=0)
    current_bmi: Optional[float] = Field(None, gt=0)
    current_streak: int = Field(0, ge=0, description="Active days streak")
    
    # Time-based analytics
    today: TimeRangeStats
    yesterday: TimeRangeStats
    this_week: TimeRangeStats
    last_week: TimeRangeStats
    this_month: TimeRangeStats
    last_month: TimeRangeStats
    this_year: TimeRangeStats
    all_time: TimeRangeStats
    
    # Performance indicators
    weekly_goal_progress: float = Field(
        0, 
        ge=0, 
        le=100, 
        description="Weekly goal completion %"
    )
    monthly_goal_progress: float = Field(
        0, 
        ge=0, 
        le=100, 
        description="Monthly goal completion %"
    )
    consistency_score: float = Field(
        0, 
        ge=0, 
        le=100, 
        description="Activity consistency score"
    )
    improvement_score: float = Field(
        0, 
        ge=0, 
        le=100, 
        description="Week-over-week improvement score"
    )


# ===== REQUEST/RESPONSE MODELS =====

class DashboardFilters(BaseAnalyticsModel):
    """Dashboard generation filters"""
    include_weight: bool = True
    include_sleep: bool = True
    include_trends: bool = True
    time_ranges: Optional[List[TimeRangeType]] = None


class DateRangeFilter(BaseAnalyticsModel):
    """Date range filter for queries"""
    start_date: date_type
    end_date: date_type


class AnalyticsQuery(BaseAnalyticsModel):
    """Base analytics query"""
    user_id: str
    date_range: Optional[DateRangeFilter] = None
    time_range: Optional[TimeRangeType] = None


class DailyStatsQuery(AnalyticsQuery):
    """Daily statistics query"""
    include_inactive_days: bool = False


class TrendsQuery(AnalyticsQuery):
    """Trends analysis query"""
    metric: str = Field("calories_burned", description="Metric to analyze")
    days: int = Field(30, ge=1, le=365, description="Days to analyze")


# ===== API RESPONSE MODELS =====

class APIResponse(BaseAnalyticsModel):
    """Standard API response wrapper"""
    success: bool = True
    message: str = "OK"
    data: Optional[dict] = None
    errors: Optional[List[str]] = None


class DailyStatsResponse(APIResponse):
    """Daily statistics API response"""
    data: Optional[List[DailyStatsRecord]] = None


class TimeRangeStatsResponse(APIResponse):
    """Time range statistics API response"""
    data: Optional[TimeRangeStats] = None


class DashboardResponse(APIResponse):
    """Dashboard API response"""
    data: Optional[UserDashboard] = None


# ===== HEALTH CHECK MODELS =====

class HealthCheck(BaseAnalyticsModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "analytics-service"
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.now)


class DetailedHealthCheck(HealthCheck):
    """Detailed health check with dependencies"""
    database: Optional[dict] = None
    redis: Optional[dict] = None
    external_services: Optional[dict] = None
