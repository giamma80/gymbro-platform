"""
Timeline Analytics API Router - Calorie Balance Service

Real-time analytics endpoints for mobile dashboard optimization.
Uses pre-computed temporal views for sub-second response times.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, date as DateType
from decimal import Decimal
import logging

# Pydantic models for request/response
from app.api.timeline_schemas import (
    HourlyAnalyticsResponse,
    DailyAnalyticsResponse,
    WeeklyAnalyticsResponse,
    MonthlyAnalyticsResponse,
    BalanceTimelineResponse,
    IntradayAnalyticsResponse,
    PatternAnalyticsResponse,
    RealTimeAnalyticsResponse,
    TimelineExportResponse
)

# Domain entities and services
from app.application.services import (
    AnalyticsService,
    CalorieEventService
)

# Dependencies
from app.core.dependencies import (
    get_analytics_service,
    get_calorie_event_service
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/users/{user_id}/hourly", response_model=HourlyAnalyticsResponse)
async def get_hourly_analytics(
    user_id: str,
    date: Optional[DateType] = Query(None, description="Specific date (default: today)"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours to look back"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> HourlyAnalyticsResponse:
    """Get hourly calorie analytics for real-time dashboard."""
    try:
        target_date = date or DateType.today()
        
        # Get hourly data from temporal view
        hourly_data = await analytics_service.get_hourly_analytics(
            user_id=user_id,
            date=target_date,
            hours_back=hours_back
        )
        
        return HourlyAnalyticsResponse(
            success=True,
            message="Hourly analytics retrieved successfully",
            data=hourly_data,
            metadata={
                "date": target_date.isoformat(),
                "hours_back": hours_back,
                "total_hours": len(hourly_data)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get hourly analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve hourly analytics"
        )


@router.get("/users/{user_id}/daily", response_model=DailyAnalyticsResponse)
async def get_daily_analytics(
    user_id: str,
    start_date: Optional[DateType] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[DateType] = Query(None, description="End date (default: today)"),
    include_trends: bool = Query(True, description="Include trend calculations"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> DailyAnalyticsResponse:
    """Get daily calorie analytics with trend analysis."""
    try:
        # Default date range: last 30 days
        end_dt = end_date or DateType.today()
        start_dt = start_date or DateType.fromordinal(end_dt.toordinal() - 30)
        
        daily_data = await analytics_service.get_daily_analytics(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            include_trends=include_trends
        )
        
        return DailyAnalyticsResponse(
            success=True,
            message="Daily analytics retrieved successfully",
            data=daily_data,
            metadata={
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat(),
                "total_days": len(daily_data),
                "include_trends": include_trends
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get daily analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily analytics"
        )


@router.get("/users/{user_id}/weekly", response_model=WeeklyAnalyticsResponse)
async def get_weekly_analytics(
    user_id: str,
    weeks_back: int = Query(12, ge=1, le=52, description="Weeks to look back"),
    include_patterns: bool = Query(True, description="Include weekly patterns"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> WeeklyAnalyticsResponse:
    """Get weekly calorie analytics with pattern recognition."""
    try:
        weekly_data = await analytics_service.get_weekly_analytics(
            user_id=user_id,
            weeks_back=weeks_back,
            include_patterns=include_patterns
        )
        
        return WeeklyAnalyticsResponse(
            success=True,
            message="Weekly analytics retrieved successfully",
            data=weekly_data,
            metadata={
                "weeks_back": weeks_back,
                "total_weeks": len(weekly_data),
                "include_patterns": include_patterns
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get weekly analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weekly analytics"
        )


@router.get("/users/{user_id}/monthly", response_model=MonthlyAnalyticsResponse)
async def get_monthly_analytics(
    user_id: str,
    months_back: int = Query(12, ge=1, le=24, description="Months to look back"),
    include_yearly_trends: bool = Query(True, description="Include yearly trend analysis"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> MonthlyAnalyticsResponse:
    """Get monthly calorie analytics with long-term trends."""
    try:
        monthly_data = await analytics_service.get_monthly_analytics(
            user_id=user_id,
            months_back=months_back,
            include_yearly_trends=include_yearly_trends
        )
        
        return MonthlyAnalyticsResponse(
            success=True,
            message="Monthly analytics retrieved successfully",
            data=monthly_data,
            metadata={
                "months_back": months_back,
                "total_months": len(monthly_data),
                "include_yearly_trends": include_yearly_trends
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get monthly analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monthly analytics"
        )


@router.get("/users/{user_id}/balance", response_model=BalanceTimelineResponse)
async def get_balance_timeline(
    user_id: str,
    period: str = Query("week", regex="^(day|week|month|quarter)$", description="Timeline period"),
    include_goals: bool = Query(True, description="Include goal comparisons"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> BalanceTimelineResponse:
    """Get calorie balance timeline with goal tracking."""
    try:
        balance_data = await analytics_service.get_balance_timeline(
            user_id=user_id,
            period=period,
            include_goals=include_goals
        )
        
        return BalanceTimelineResponse(
            success=True,
            message="Balance timeline retrieved successfully",
            data=balance_data,
            metadata={
                "period": period,
                "include_goals": include_goals,
                "data_points": len(balance_data)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get balance timeline for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve balance timeline"
        )


@router.get("/users/{user_id}/intraday", response_model=IntradayAnalyticsResponse)
async def get_intraday_analytics(
    user_id: str,
    date: Optional[DateType] = Query(None, description="Target date (default: today)"),
    resolution_minutes: int = Query(15, ge=5, le=60, description="Data resolution in minutes"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> IntradayAnalyticsResponse:
    """Get intraday calorie analytics with high resolution."""
    try:
        target_date = date or DateType.today()
        
        intraday_data = await analytics_service.get_intraday_analytics(
            user_id=user_id,
            date=target_date,
            resolution_minutes=resolution_minutes
        )
        
        return IntradayAnalyticsResponse(
            success=True,
            message="Intraday analytics retrieved successfully",
            data=intraday_data,
            metadata={
                "date": target_date.isoformat(),
                "resolution_minutes": resolution_minutes,
                "data_points": len(intraday_data)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get intraday analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve intraday analytics"
        )


@router.get("/users/{user_id}/patterns", response_model=PatternAnalyticsResponse)
async def get_pattern_analytics(
    user_id: str,
    analysis_type: str = Query("behavioral", regex="^(behavioral|seasonal|weekly|daily)$"),
    lookback_days: int = Query(90, ge=30, le=365, description="Days to analyze for patterns"),
    min_confidence: float = Query(0.7, ge=0.5, le=1.0, description="Minimum pattern confidence"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> PatternAnalyticsResponse:
    """Get behavioral pattern analytics with AI insights."""
    try:
        patterns = await analytics_service.get_pattern_analytics(
            user_id=user_id,
            analysis_type=analysis_type,
            lookback_days=lookback_days,
            min_confidence=min_confidence
        )
        
        return PatternAnalyticsResponse(
            success=True,
            message="Pattern analytics retrieved successfully",
            data=patterns,
            metadata={
                "analysis_type": analysis_type,
                "lookback_days": lookback_days,
                "min_confidence": min_confidence,
                "patterns_found": len(patterns)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get pattern analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pattern analytics"
        )


@router.get("/users/{user_id}/real-time", response_model=RealTimeAnalyticsResponse)
async def get_real_time_analytics(
    user_id: str,
    last_hours: int = Query(1, ge=1, le=24, description="Hours for real-time data"),
    include_predictions: bool = Query(True, description="Include real-time predictions"),
    event_service: CalorieEventService = Depends(get_calorie_event_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> RealTimeAnalyticsResponse:
    """Get real-time calorie analytics for live dashboard updates."""
    try:
        # Get recent events for real-time analysis
        recent_events = await event_service.get_recent_events(
            user_id=user_id,
            hours_back=last_hours
        )
        
        # Generate real-time analytics
        real_time_data = await analytics_service.generate_real_time_analytics(
            user_id=user_id,
            recent_events=recent_events,
            include_predictions=include_predictions
        )
        
        return RealTimeAnalyticsResponse(
            success=True,
            message="Real-time analytics retrieved successfully",
            data=real_time_data,
            metadata={
                "last_hours": last_hours,
                "include_predictions": include_predictions,
                "events_processed": len(recent_events),
                "generated_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get real-time analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve real-time analytics"
        )


@router.get("/users/{user_id}/export", response_model=TimelineExportResponse)
async def export_timeline_data(
    user_id: str,
    format: str = Query("json", regex="^(json|csv|xlsx)$", description="Export format"),
    start_date: Optional[DateType] = Query(None, description="Start date for export"),
    end_date: Optional[DateType] = Query(None, description="End date for export"),
    granularity: str = Query("daily", regex="^(hourly|daily|weekly)$", description="Data granularity"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> TimelineExportResponse:
    """Export timeline data for external analysis or backup."""
    try:
        # Default to last 3 months if no dates specified
        end_dt = end_date or DateType.today()
        start_dt = start_date or DateType.fromordinal(end_dt.toordinal() - 90)
        
        export_data = await analytics_service.export_timeline_data(
            user_id=user_id,
            format=format,
            start_date=start_dt,
            end_date=end_dt,
            granularity=granularity
        )
        
        return TimelineExportResponse(
            success=True,
            message="Timeline data exported successfully",
            data=export_data,
            metadata={
                "format": format,
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat(),
                "granularity": granularity,
                "export_size_mb": len(str(export_data)) / 1024 / 1024
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to export timeline data for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export timeline data"
        )