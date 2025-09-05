from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date as date_type

from ...core.database import get_session
from ...core.schemas import APIResponse
from ...infrastructure.database.repositories import (
    SqlDailyBalanceRepository, SqlUserRepository, SqlMetabolicProfileRepository, SqlCalorieGoalRepository
)
from ...infrastructure.database.uow import SqlUnitOfWork
from ...infrastructure.services import DefaultCalorieCalculationService
from ...application.commands import (
    UpdateDailyBalanceCommand, DailyBalanceCommandHandler
)
from ...application.queries import (
    GetDailyBalanceQuery, GetProgressQuery, DailyBalanceQueryHandler, ProgressQueryHandler
)
from ..schemas import DailyBalanceUpdateRequest, DailyBalanceResponse, ProgressRequest

router = APIRouter()


def get_balance_dependencies(session: AsyncSession = Depends(get_session)):
    """Get daily balance dependencies"""
    balance_repo = SqlDailyBalanceRepository(session)
    user_repo = SqlUserRepository(session)
    profile_repo = SqlMetabolicProfileRepository(session)
    goal_repo = SqlCalorieGoalRepository(session)
    calorie_service = DefaultCalorieCalculationService()
    uow = SqlUnitOfWork(session)
    
    balance_command_handler = DailyBalanceCommandHandler(balance_repo, user_repo, profile_repo, uow)
    balance_query_handler = DailyBalanceQueryHandler(balance_repo)
    progress_query_handler = ProgressQueryHandler(balance_repo, goal_repo, calorie_service)
    
    return balance_command_handler, balance_query_handler, progress_query_handler


@router.put("/users/{user_id}", response_model=APIResponse)
async def update_daily_balance(
    user_id: UUID,
    request: DailyBalanceUpdateRequest,
    dependencies=Depends(get_balance_dependencies)
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
            notes=request.notes
        )
        
        balance = await balance_command_handler.handle_update_balance(command)
        
        # Convert UUID fields to strings before serialization
        balance_dict = balance.dict()
        balance_dict["id"] = str(balance.id)
        balance_dict["user_id"] = str(balance.user_id)
        
        return APIResponse(
                success=True,
                message="Daily balance updated successfully",
                data=DailyBalanceResponse(**balance_dict)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/{user_id}/date/{date}", response_model=APIResponse)
async def get_daily_balance(
    user_id: UUID,
    date: date_type,
    dependencies=Depends(get_balance_dependencies)
):
    """Get daily balance for specific date"""
    _, balance_query_handler, _ = dependencies
    
    query = GetDailyBalanceQuery(user_id, date)
    balance = await balance_query_handler.handle_get_balance(query)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily balance not found for this date"
        )
    
    # Convert UUID fields to strings before serialization
    balance_dict = balance.dict()
    balance_dict["id"] = str(balance.id)
    balance_dict["user_id"] = str(balance.user_id)
    
    return APIResponse(
        success=True,
        data=DailyBalanceResponse(**balance_dict)
    )


@router.get("/users/{user_id}/today", response_model=APIResponse)
async def get_today_balance(
    user_id: UUID,
    dependencies=Depends(get_balance_dependencies)
):
    """Get today's balance for user"""
    _, balance_query_handler, _ = dependencies
    
    today = date_type.today()
    query = GetDailyBalanceQuery(user_id, today)
    balance = await balance_query_handler.handle_get_balance(query)
    
    if not balance:
        # Return empty balance for today
        return APIResponse(
            success=True,
            message="No data for today yet",
            data=None
        )
    
    # Convert UUID fields to strings before serialization
    balance_dict = balance.dict()
    balance_dict["id"] = str(balance.id)
    balance_dict["user_id"] = str(balance.user_id)
    
    return APIResponse(
        success=True,
        data=DailyBalanceResponse(**balance_dict)
    )


@router.post("/users/{user_id}/progress", response_model=APIResponse)
async def get_progress_data(
    user_id: UUID,
    request: ProgressRequest,
    dependencies=Depends(get_balance_dependencies)
):
    """Get progress data for date range"""
    _, _, progress_query_handler = dependencies
    
    query = GetProgressQuery(user_id, request.start_date, request.end_date)
    progress_data = await progress_query_handler.handle_get_progress(query)
    
    return APIResponse(
        success=True,
        data=progress_data
    )
