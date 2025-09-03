"""
REST API v1 Endpoints for Analytics Service
DUAL API ARCHITECTURE - REST + GraphQL
Following GymBro microservice template
Enhanced with HealthKit integration
"""

from datetime import date
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from app.models import (
    DailyStatsRecord,
    TimeRangeStats,
    UserDashboard,
    DailyStatsResponse,
    TimeRangeStatsResponse,
    DashboardResponse,
    APIResponse,
    TimeRangeType,
    DashboardFilters,
    DateRangeFilter,
    DailyStatsQuery,
    TrendsQuery
)
from app.services import AnalyticsService


# Create router
router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}}
)


# ===== DAILY STATISTICS ENDPOINTS =====

@router.get(
    "/users/{user_id}/daily-stats",
    response_model=DailyStatsResponse,
    summary="Get user daily statistics",
    description="Retrieve daily fitness statistics for a user within date range"
)
async def get_daily_stats(
    user_id: str = Path(..., description="User identifier"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    time_range: Optional[TimeRangeType] = Query(None, description="Predefined time range"),
    include_inactive_days: bool = Query(False, description="Include inactive days")
) -> DailyStatsResponse:
    """Get daily statistics for user"""
    
    try:
        service = AnalyticsService()
        
        # Build query
        date_range = None
        if start_date and end_date:
            date_range = DateRangeFilter(start_date=start_date, end_date=end_date)
        
        # Get daily stats
        records = await service.get_daily_stats(
            user_id=user_id,
            date_range=date_range,
            time_range=time_range
        )
        
        # Filter inactive days if requested
        if not include_inactive_days:
            records = [r for r in records if r.is_active_day]
        
        return DailyStatsResponse(
            success=True,
            message=f"Retrieved {len(records)} daily statistics records",
            data=records
        )
    
    except Exception as e:
        return DailyStatsResponse(
            success=False,
            message="Failed to retrieve daily statistics",
            errors=[str(e)]
        )


@router.post(
    "/users/{user_id}/daily-stats",
    response_model=APIResponse,
    summary="Record daily statistics",
    description="Record or update daily fitness statistics for user"
)
async def record_daily_stats(
    user_id: str = Path(..., description="User identifier"),
    stats_date: date = Query(..., description="Statistics date"),
    calories_burned: float = Query(..., ge=0, description="Calories burned"),
    calories_consumed: float = Query(..., ge=0, description="Calories consumed"),
    active_minutes: int = Query(..., ge=0, description="Active minutes"),
    steps_count: int = Query(..., ge=0, description="Steps count"),
    workouts_completed: int = Query(0, ge=0, description="Workouts completed"),
    weight_kg: Optional[float] = Query(None, gt=0, description="Weight in kg"),
    sleep_hours: Optional[float] = Query(None, ge=0, le=24, description="Sleep hours")
) -> APIResponse:
    """Record daily statistics for user"""
    
    try:
        service = AnalyticsService()
        
        record = await service.record_daily_stats(
            user_id=user_id,
            date=stats_date,
            calories_burned=calories_burned,
            calories_consumed=calories_consumed,
            active_minutes=active_minutes,
            steps_count=steps_count,
            workouts_completed=workouts_completed,
            weight_kg=weight_kg,
            sleep_hours=sleep_hours
        )
        
        return APIResponse(
            success=True,
            message="Daily statistics recorded successfully",
            data=record.model_dump()
        )
    
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to record daily statistics",
            errors=[str(e)]
        )


# ===== TIME RANGE ANALYTICS ENDPOINTS =====

@router.get(
    "/users/{user_id}/stats/{time_range}",
    response_model=TimeRangeStatsResponse,
    summary="Get time range statistics",
    description="Get aggregated statistics for specific time range"
)
async def get_time_range_stats(
    user_id: str = Path(..., description="User identifier"),
    time_range: TimeRangeType = Path(..., description="Time range type"),
    reference_date: Optional[date] = Query(None, description="Reference date for calculation")
) -> TimeRangeStatsResponse:
    """Get aggregated statistics for time range"""
    
    try:
        service = AnalyticsService()
        
        stats = await service.get_time_range_stats(
            user_id=user_id,
            time_range=time_range,
            reference_date=reference_date
        )
        
        return TimeRangeStatsResponse(
            success=True,
            message=f"Retrieved {time_range.value} statistics",
            data=stats
        )
    
    except Exception as e:
        return TimeRangeStatsResponse(
            success=False,
            message="Failed to retrieve time range statistics",
            errors=[str(e)]
        )


# ===== DASHBOARD ENDPOINTS =====

@router.get(
    "/users/{user_id}/dashboard",
    response_model=DashboardResponse,
    summary="Get user dashboard",
    description="Get complete analytics dashboard for user"
)
async def get_user_dashboard(
    user_id: str = Path(..., description="User identifier"),
    include_weight: bool = Query(True, description="Include weight tracking"),
    include_sleep: bool = Query(True, description="Include sleep data"),
    include_trends: bool = Query(True, description="Include trend analysis")
) -> DashboardResponse:
    """Get complete dashboard for user"""
    
    try:
        service = AnalyticsService()
        
        # Build filters
        filters = DashboardFilters(
            include_weight=include_weight,
            include_sleep=include_sleep,
            include_trends=include_trends
        )
        
        dashboard = await service.generate_dashboard(
            user_id=user_id,
            filters=filters
        )
        
        return DashboardResponse(
            success=True,
            message="Dashboard generated successfully",
            data=dashboard
        )
    
    except Exception as e:
        return DashboardResponse(
            success=False,
            message="Failed to generate dashboard",
            errors=[str(e)]
        )


# ===== TRENDS ANALYSIS ENDPOINTS =====

@router.get(
    "/users/{user_id}/trends/{metric}",
    response_model=DailyStatsResponse,
    summary="Get trends analysis",
    description="Get trend analysis for specific metric"
)
async def get_trends_analysis(
    user_id: str = Path(..., description="User identifier"),
    metric: str = Path(..., description="Metric to analyze"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
) -> DailyStatsResponse:
    """Get trends analysis for specific metric"""
    
    try:
        service = AnalyticsService()
        
        records = await service.get_trends_analysis(
            user_id=user_id,
            metric=metric,
            days=days
        )
        
        return DailyStatsResponse(
            success=True,
            message=f"Retrieved {days}-day trend analysis for {metric}",
            data=records
        )
    
    except Exception as e:
        return DailyStatsResponse(
            success=False,
            message="Failed to retrieve trends analysis",
            errors=[str(e)]
        )


# ===== SUMMARY ENDPOINTS =====

@router.get(
    "/users/{user_id}/summary",
    response_model=APIResponse,
    summary="Get analytics summary",
    description="Get high-level analytics summary for user"
)
async def get_analytics_summary(
    user_id: str = Path(..., description="User identifier")
) -> APIResponse:
    """Get high-level analytics summary"""
    
    try:
        service = AnalyticsService()
        
        # Get key statistics
        this_week = await service.get_time_range_stats(
            user_id, TimeRangeType.WEEK
        )
        this_month = await service.get_time_range_stats(
            user_id, TimeRangeType.MONTH
        )
        
        summary = {
            "user_id": user_id,
            "week": {
                "calories_burned": this_week.total_calories_burned,
                "active_days": this_week.active_days_count,
                "activity_percentage": this_week.activity_percentage,
                "avg_daily_steps": this_week.avg_daily_steps
            },
            "month": {
                "calories_burned": this_month.total_calories_burned,
                "active_days": this_month.active_days_count,
                "activity_percentage": this_month.activity_percentage,
                "weight_change": this_month.weight_change_kg
            }
        }
        
        return APIResponse(
            success=True,
            message="Analytics summary retrieved successfully",
            data=summary
        )
    
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to retrieve analytics summary",
            errors=[str(e)]
        )


# ===== ENHANCED HEALTHKIT ANALYTICS ENDPOINTS =====

@router.get(
    "/users/{user_id}/enhanced-dashboard",
    response_model=Dict[str, Any],
    summary="Get enhanced dashboard with HealthKit analytics",
    description="Enhanced dashboard with metabolic, body composition, cardiovascular, and sleep analytics"
)
async def get_enhanced_dashboard(
    user_id: str = Path(..., description="User identifier"),
    include_recommendations: bool = Query(
        True, description="Include personalized recommendations"
    ),
    include_trends: bool = Query(
        True, description="Include trend analysis"
    ),
    include_correlations: bool = Query(
        True, description="Include sleep-performance correlations"
    )
) -> Dict[str, Any]:
    """Get enhanced user dashboard with HealthKit integration"""
    
    try:
        service = AnalyticsService()
        
        # Create filters based on query parameters
        filters = DashboardFilters(
            include_weight=True,
            include_sleep=include_correlations,
            include_trends=include_trends
        )
        
        dashboard_data = await service.get_enhanced_dashboard(
            user_id=user_id,
            filters=filters
        )
        
        # Filter out recommendations if not requested
        if not include_recommendations:
            dashboard_data.pop("recommendations", None)
        
        return {
            "success": True,
            "message": "Enhanced dashboard retrieved successfully",
            "data": dashboard_data
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to retrieve enhanced dashboard",
            "error": str(e)
        }


@router.get(
    "/users/{user_id}/metabolic-analysis",
    response_model=Dict[str, Any],
    summary="Get metabolic analysis",
    description="Detailed metabolic analysis including BMR, TDEE, and caloric balance"
)
async def get_metabolic_analysis(
    user_id: str = Path(..., description="User identifier"),
    days: int = Query(30, description="Number of days to analyze", ge=7, le=365)
) -> Dict[str, Any]:
    """Get detailed metabolic analysis for user"""
    
    try:
        # This would be implemented to extract just metabolic data
        service = AnalyticsService()
        dashboard_data = await service.get_enhanced_dashboard(user_id=user_id)
        
        metabolic_data = dashboard_data.get("metabolic_analysis")
        
        return {
            "success": True,
            "message": "Metabolic analysis retrieved successfully", 
            "data": {
                "user_id": user_id,
                "analysis_period_days": days,
                "metabolic_analysis": metabolic_data,
                "generated_at": dashboard_data.get("generated_at")
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to retrieve metabolic analysis",
            "error": str(e)
        }


@router.get(
    "/users/{user_id}/cardiovascular-insights",
    response_model=Dict[str, Any],
    summary="Get cardiovascular insights",
    description="Heart rate analysis, HRV trends, and cardiovascular fitness metrics"
)
async def get_cardiovascular_insights(
    user_id: str = Path(..., description="User identifier")
) -> Dict[str, Any]:
    """Get cardiovascular health insights"""
    
    try:
        service = AnalyticsService()
        dashboard_data = await service.get_enhanced_dashboard(user_id=user_id)
        
        cardio_data = dashboard_data.get("cardiovascular_analysis")
        
        return {
            "success": True,
            "message": "Cardiovascular insights retrieved successfully",
            "data": {
                "user_id": user_id,
                "cardiovascular_analysis": cardio_data,
                "generated_at": dashboard_data.get("generated_at")
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to retrieve cardiovascular insights",
            "error": str(e)
        }


# ===== HEALTH CHECK ENDPOINTS =====

@router.get(
    "/health",
    response_model=APIResponse,
    summary="Analytics service health check",
    description="Check analytics service health"
)
async def analytics_health():
    """Analytics service specific health check"""
    
    return APIResponse(
        success=True,
        message="Analytics service is healthy",
        data={
            "service": "analytics-service",
            "version": "0.1.0",
            "endpoints": "operational",
            "timestamp": date.today().isoformat()
        }
    )
