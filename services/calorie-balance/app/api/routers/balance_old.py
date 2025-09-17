"""
Daily Balance API Router - Calorie Balance Service

Balance tracking and progress monitoring endpoints.
Optimized for mobile dashboards and progress tracking.
"""

import logging
from datetime import date as DateType
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

# Pydantic models for request/response
from app.api.schemas import (
    CalorieGoalResponse,
    DailyBalanceResponse,
    DailyBalanceUpdateRequest,
    ProgressResponse,
)

# Domain entities and services
from app.application.services import (
    AnalyticsService,
    CalorieEventService,
    CalorieGoalService,
)

# Dependencies
from app.core.dependencies import (
    get_analytics_service,
    get_calorie_event_service,
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
            weight_kg=Decimal(str(dashboard_data.get("current_weight", 0)))
            if dashboard_data.get("current_weight")
            else None,
            metabolic_data=dashboard_data.get("metabolic_data", {}),
        )

    except Exception as e:
        logger.error(f"Failed to get daily balance for {user_id} on {date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily balance",
        )
    uow = SqlUnitOfWork(session)

    balance_command_handler = DailyBalanceCommandHandler(
        balance_repo, user_repo, profile_repo, uow
    )
    balance_query_handler = DailyBalanceQueryHandler(balance_repo)
    progress_query_handler = ProgressQueryHandler(
        balance_repo, goal_repo, calorie_service
    )

    return balance_command_handler, balance_query_handler, progress_query_handler


@router.put("/users/{user_id}", response_model=APIResponse)
async def update_daily_balance(
    user_id: UUID,
    request: DailyBalanceUpdateRequest,
    dependencies=Depends(get_balance_dependencies),
):
    """Update daily calorie balance for user"""
    balance_command_handler, _, _ = dependencies

    try:
        command = UpdateDailyBalanceCommand(
            user_id=user_id,
            date=request.date or date_type.today(),
            calories_consumed=request.calories_consumed,
            calories_burned_exercise=request.calories_burned_exercise,
            weight_kg=request.weight_kg,
            notes=request.notes,
        )

        balance = await balance_command_handler.handle_update_balance(command)

        # Convert UUID fields to strings before serialization
        balance_dict = balance.dict()
        balance_dict["id"] = str(balance.id)
        balance_dict["user_id"] = str(balance.user_id)

        return APIResponse(
            success=True,
            message="Daily balance updated successfully",
            data=DailyBalanceResponse(**balance_dict),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users/{user_id}/date/{date}", response_model=APIResponse)
async def get_daily_balance(
    user_id: UUID, date: date_type, dependencies=Depends(get_balance_dependencies)
):
    """Get daily balance for specific date"""
    _, balance_query_handler, _ = dependencies

    query = GetDailyBalanceQuery(user_id, date)
    balance = await balance_query_handler.handle_get_balance(query)

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily balance not found for this date",
        )

    # Convert UUID fields to strings before serialization
    balance_dict = balance.dict()
    balance_dict["id"] = str(balance.id)
    balance_dict["user_id"] = str(balance.user_id)

    return APIResponse(success=True, data=DailyBalanceResponse(**balance_dict))


@router.get("/users/{user_id}/today", response_model=APIResponse)
async def get_today_balance(
    user_id: UUID, dependencies=Depends(get_balance_dependencies)
):
    """Get today's balance for user"""
    _, balance_query_handler, _ = dependencies

    today = date_type.today()
    query = GetDailyBalanceQuery(user_id, today)
    balance = await balance_query_handler.handle_get_balance(query)

    if not balance:
        # Return empty balance for today
        return APIResponse(success=True, message="No data for today yet", data=None)

    # Convert UUID fields to strings before serialization
    balance_dict = balance.dict()
    balance_dict["id"] = str(balance.id)
    balance_dict["user_id"] = str(balance.user_id)

    return APIResponse(success=True, data=DailyBalanceResponse(**balance_dict))


@router.post("/users/{user_id}/progress", response_model=APIResponse)
async def get_progress_data(
    user_id: UUID,
    request: ProgressRequest,
    dependencies=Depends(get_balance_dependencies),
):
    """Get progress data for date range"""
    _, _, progress_query_handler = dependencies

    query = GetProgressQuery(user_id, request.start_date, request.end_date)
    progress_data = await progress_query_handler.handle_get_progress(query)

    return APIResponse(success=True, data=progress_data)
