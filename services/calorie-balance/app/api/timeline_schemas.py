"""
Analytics Response Schemas - Calorie Balance Service

Response models for timeline analytics endpoints.
Follows the established pattern from existing schemas.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date as DateType
from decimal import Decimal
from pydantic import BaseModel, Field


class BaseAnalyticsResponse(BaseModel):
    """Base response model for analytics endpoints."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


class HourlyDataPoint(BaseModel):
    """Single hour data point for analytics."""
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    date: DateType = Field(..., description="Date for this hour")
    calories_consumed: Decimal = Field(Decimal("0"), description="Calories consumed")
    calories_burned_exercise: Decimal = Field(Decimal("0"), description="Exercise calories")
    calories_burned_bmr: Decimal = Field(Decimal("0"), description="BMR calories")
    net_calories: Decimal = Field(..., description="Net calorie balance")
    weight_kg: Optional[Decimal] = Field(None, description="Weight measurement")
    event_count: int = Field(0, description="Number of events in this hour")
    data_quality: Decimal = Field(Decimal("1.0"), description="Data completeness score")


class HourlyAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for hourly analytics."""
    data: List[HourlyDataPoint] = Field(..., description="Hourly data points")


class DailyDataPoint(BaseModel):
    """Single day data point for analytics."""
    date: DateType = Field(..., description="Date")
    calories_consumed: Decimal = Field(Decimal("0"), description="Total calories consumed")
    calories_burned_exercise: Decimal = Field(Decimal("0"), description="Exercise calories")
    calories_burned_bmr: Decimal = Field(Decimal("0"), description="BMR calories")
    net_calories: Decimal = Field(..., description="Net calorie balance")
    morning_weight_kg: Optional[Decimal] = Field(None, description="Morning weight")
    evening_weight_kg: Optional[Decimal] = Field(None, description="Evening weight")
    goal_target: Optional[Decimal] = Field(None, description="Daily calorie target")
    goal_deviation: Optional[Decimal] = Field(None, description="Deviation from goal")
    trend_direction: Optional[str] = Field(None, description="Trend direction indicator")
    active_hours: int = Field(0, description="Hours with recorded activity")


class DailyAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for daily analytics."""
    data: List[DailyDataPoint] = Field(..., description="Daily data points")


class WeeklyDataPoint(BaseModel):
    """Single week data point for analytics."""
    week_start: DateType = Field(..., description="Week start date (Monday)")
    week_end: DateType = Field(..., description="Week end date (Sunday)")
    avg_daily_consumed: Decimal = Field(Decimal("0"), description="Average daily consumed")
    avg_daily_burned: Decimal = Field(Decimal("0"), description="Average daily burned")
    avg_net_calories: Decimal = Field(..., description="Average net calories")
    total_weight_change: Optional[Decimal] = Field(None, description="Weight change for week")
    active_days: int = Field(0, description="Days with recorded activity")
    goal_adherence_pct: Optional[Decimal] = Field(None, description="Goal adherence percentage")
    weekday_patterns: Optional[Dict[str, Decimal]] = Field(None, description="Weekday patterns")


class WeeklyAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for weekly analytics."""
    data: List[WeeklyDataPoint] = Field(..., description="Weekly data points")


class MonthlyDataPoint(BaseModel):
    """Single month data point for analytics."""
    month: int = Field(..., ge=1, le=12, description="Month number")
    year: int = Field(..., description="Year")
    avg_daily_consumed: Decimal = Field(Decimal("0"), description="Average daily consumed")
    avg_daily_burned: Decimal = Field(Decimal("0"), description="Average daily burned")
    avg_net_calories: Decimal = Field(..., description="Average net calories")
    total_weight_change: Optional[Decimal] = Field(None, description="Weight change for month")
    active_days: int = Field(0, description="Days with recorded activity")
    weekly_consistency: Optional[Decimal] = Field(None, description="Weekly consistency score")
    seasonal_factor: Optional[Decimal] = Field(None, description="Seasonal adjustment factor")


class MonthlyAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for monthly analytics."""
    data: List[MonthlyDataPoint] = Field(..., description="Monthly data points")


class BalanceTimelinePoint(BaseModel):
    """Balance timeline data point."""
    timestamp: datetime = Field(..., description="Data point timestamp")
    net_calories: Decimal = Field(..., description="Net calorie balance")
    goal_target: Optional[Decimal] = Field(None, description="Goal target for period")
    cumulative_balance: Decimal = Field(..., description="Cumulative balance")
    trend_coefficient: Optional[Decimal] = Field(None, description="Trend coefficient")


class BalanceTimelineResponse(BaseAnalyticsResponse):
    """Response model for balance timeline."""
    data: List[BalanceTimelinePoint] = Field(..., description="Balance timeline points")


class IntradayDataPoint(BaseModel):
    """High-resolution intraday data point."""
    time_slot: str = Field(..., description="Time slot (HH:MM format)")
    calories_consumed: Decimal = Field(Decimal("0"), description="Calories consumed")
    calories_burned: Decimal = Field(Decimal("0"), description="Calories burned")
    cumulative_balance: Decimal = Field(..., description="Cumulative balance")
    activity_intensity: Optional[str] = Field(None, description="Activity intensity level")


class IntradayAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for intraday analytics."""
    data: List[IntradayDataPoint] = Field(..., description="Intraday data points")


class BehavioralPattern(BaseModel):
    """Behavioral pattern detection result."""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    pattern_type: str = Field(..., description="Type of pattern detected")
    description: str = Field(..., description="Human-readable pattern description")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Pattern confidence")
    frequency: str = Field(..., description="Pattern frequency (daily/weekly/monthly)")
    impact_score: Optional[Decimal] = Field(None, description="Pattern impact on goals")
    recommendations: Optional[List[str]] = Field(None, description="AI recommendations")


class PatternAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for pattern analytics."""
    data: List[BehavioralPattern] = Field(..., description="Detected patterns")


class RealTimeMetrics(BaseModel):
    """Real-time metrics for live dashboard."""
    current_balance: Decimal = Field(..., description="Current day balance")
    projected_end_of_day: Optional[Decimal] = Field(None, description="EOD projection")
    calories_remaining: Optional[Decimal] = Field(None, description="Calories remaining today")
    burn_rate_per_hour: Decimal = Field(Decimal("0"), description="Current burn rate")
    consumption_rate_per_hour: Decimal = Field(Decimal("0"), description="Current consumption rate")
    goal_achievement_probability: Optional[Decimal] = Field(None, description="Goal achievement probability")
    next_meal_recommendation: Optional[str] = Field(None, description="Next meal recommendation")


class RealTimeAnalyticsResponse(BaseAnalyticsResponse):
    """Response model for real-time analytics."""
    data: RealTimeMetrics = Field(..., description="Real-time metrics")


class TimelineExportData(BaseModel):
    """Timeline export data structure."""
    export_format: str = Field(..., description="Export format used")
    data_url: Optional[str] = Field(None, description="URL to download export file")
    inline_data: Optional[Union[Dict, List, str]] = Field(None, description="Inline export data")
    record_count: int = Field(..., description="Number of records exported")
    export_timestamp: datetime = Field(..., description="Export generation timestamp")


class TimelineExportResponse(BaseAnalyticsResponse):
    """Response model for timeline export."""
    data: TimelineExportData = Field(..., description="Export data and metadata")