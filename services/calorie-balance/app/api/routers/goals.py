from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...core.database import get_session
from ...core.schemas import APIResponse
from ...infrastructure.database.repositories import (
    SqlCalorieGoalRepository, SqlUserRepository, SqlMetabolicProfileRepository
)
from ...infrastructure.database.uow import SqlUnitOfWork
from ...infrastructure.services import DefaultCalorieCalculationService
from ...application.commands import (
    CreateCalorieGoalCommand, CalorieGoalCommandHandler
)
from ...application.queries import (
    GetCalorieGoalQuery, CalorieGoalQueryHandler
)
from ..schemas import CalorieGoalCreateRequest, CalorieGoalResponse

router = APIRouter()


def get_goal_dependencies(session: AsyncSession = Depends(get_session)):
    """Get calorie goal dependencies"""
    goal_repo = SqlCalorieGoalRepository(session)
    user_repo = SqlUserRepository(session)
    calorie_service = DefaultCalorieCalculationService()
    uow = SqlUnitOfWork(session)
    
    goal_command_handler = CalorieGoalCommandHandler(goal_repo, user_repo, calorie_service, uow)
    goal_query_handler = CalorieGoalQueryHandler(goal_repo)
    
    return goal_command_handler, goal_query_handler


@router.post("/users/{user_id}", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_calorie_goal(
    user_id: UUID,
    request: CalorieGoalCreateRequest,
    dependencies=Depends(get_goal_dependencies)
):
    """Create a new calorie goal for user"""
    goal_command_handler, _ = dependencies
    
    try:
        command = CreateCalorieGoalCommand(
            user_id=user_id,
            goal_type=request.goal_type.value,
            target_weight_kg=request.target_weight_kg,
            weekly_weight_change_kg=request.weekly_weight_change_kg,
            start_date=request.start_date
        )
        
        goal = await goal_command_handler.handle_create_goal(command)
        
        return APIResponse(
            success=True,
            message="Calorie goal created successfully",
            data=CalorieGoalResponse.from_orm(goal)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/{user_id}/active", response_model=APIResponse)
async def get_active_goal(
    user_id: UUID,
    dependencies=Depends(get_goal_dependencies)
):
    """Get active calorie goal for user"""
    _, goal_query_handler = dependencies
    
    query = GetCalorieGoalQuery(user_id)
    goal = await goal_query_handler.handle_get_goal(query)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active calorie goal found for user"
        )
    
    return APIResponse(
        success=True,
        data=CalorieGoalResponse.from_orm(goal)
    )
