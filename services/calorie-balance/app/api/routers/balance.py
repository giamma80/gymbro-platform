"""
Daily Balance API Router - Calorie Balance Service

Balance tracking and progress monitoring endpoints.
Optimized for mobile dashboards and progress tracking.
"""

import logging
from datetime import date as DateType
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

# Pydantic models for request/response
from app.api.calorie_schemas import DailyBalanceResponse, ProgressResponse

# Domain entities and services
from app.application.services import AnalyticsService, CalorieGoalService

# Dependencies
from app.core.dependencies import (
    get_analytics_service,
    get_calorie_goal_service,
    get_current_user_id,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/daily/{date}", response_model=DailyBalanceResponse)
async def get_daily_balance(
    date: DateType,
    user_id: str = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> DailyBalanceResponse:
    """
    Get daily balance for specific date.

    Mobile-optimized endpoint for dashboard display.
    """
    try:
        dashboard_data = await analytics_service.get_daily_dashboard(user_id, date)

        return DailyBalanceResponse(
            user_id=user_id,
            date=date,
            calories_consumed=Decimal(str(dashboard_data.get("calories_consumed", 0))),
            calories_burned=Decimal(str(dashboard_data.get("calories_burned", 0))),
            net_calories=Decimal(str(dashboard_data.get("net_calories", 0))),
            daily_goal=Decimal(str(dashboard_data.get("daily_goal", 0))),
            progress_percentage=dashboard_data.get("progress_percentage", 0.0),
            weight_kg=(
                Decimal(str(dashboard_data.get("current_weight", 0)))
                if dashboard_data.get("current_weight")
                else None
            ),
            metabolic_data=dashboard_data.get("metabolic_data", {}),
        )

    except Exception as e:
        logger.error(f"Failed to get daily balance for {user_id} on {date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily balance",
        )


@router.get("/today", response_model=DailyBalanceResponse)
async def get_today_balance(
    user_id: str = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> DailyBalanceResponse:
    """
    Get today's balance for current user.

    Quick endpoint for mobile dashboard.
    """
    from datetime import date

    today = date.today()
    return await get_daily_balance(today, user_id, analytics_service)


@router.get("/progress", response_model=List[ProgressResponse])
async def get_weekly_progress(
    days: int = 7,
    user_id: str = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> List[ProgressResponse]:
    """
    Get progress data for last N days.

    Optimized for mobile progress charts.
    """
    try:
        from datetime import date, timedelta

        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        progress_data = []
        current_date = start_date

        while current_date <= end_date:
            dashboard_data = await analytics_service.get_daily_dashboard(
                user_id, current_date
            )

            progress_data.append(
                ProgressResponse(
                    date=current_date,
                    calories_consumed=Decimal(
                        str(dashboard_data.get("calories_consumed", 0))
                    ),
                    calories_burned=Decimal(
                        str(dashboard_data.get("calories_burned", 0))
                    ),
                    net_calories=Decimal(str(dashboard_data.get("net_calories", 0))),
                    daily_goal=Decimal(str(dashboard_data.get("daily_goal", 0))),
                    progress_percentage=dashboard_data.get("progress_percentage", 0.0),
                    weight_kg=(
                        Decimal(str(dashboard_data.get("current_weight", 0)))
                        if dashboard_data.get("current_weight")
                        else None
                    ),
                )
            )

            current_date += timedelta(days=1)

        return progress_data

    except Exception as e:
        logger.error(f"Failed to get progress for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress data",
        )
