"""
Calorie Goals API Router - Calorie Balance Service

Goal setting and management endpoints.
AI-optimized goal recommendations and progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date as DateType
from decimal import Decimal
import logging

# Pydantic models for request/response  
from app.api.calorie_schemas import (
    CalorieGoalResponse,
    CalorieGoalCreateRequest,
    CalorieGoalUpdateRequest
)
from app.api.schemas import WeightLossGoalRequest

# Domain entities and services
from app.application.services import (
    CalorieGoalService,
    MetabolicCalculationService
)
from app.domain.entities import GoalType

# Dependencies
from app.core.dependencies import (
    get_calorie_goal_service,
    get_metabolic_service,
    get_current_user_id
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=CalorieGoalResponse)
async def create_calorie_goal(
    request: CalorieGoalCreateRequest,
    user_id: str = Depends(get_current_user_id),
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
) -> CalorieGoalResponse:
    """
    Create a new calorie goal with AI optimization.
    
    Automatically calculates optimal targets based on user profile.
    """
    try:
        # Create goal using the service with Parameter Passing
        goal = await goal_service.create_goal(
            user_id=user_id,
            goal_type=GoalType(request.goal_type),
            target_weight_kg=request.target_weight_kg,
            target_date=request.target_date,
            weekly_weight_change_kg=request.weekly_weight_change_kg,
            activity_level=request.activity_level,
            custom_calorie_target=request.custom_calorie_target,
            # Parameter Passing - User metrics from request
            user_weight_kg=request.user_weight_kg,
            user_height_cm=request.user_height_cm,
            user_age=request.user_age,
            user_gender=request.user_gender
        )
        
        return CalorieGoalResponse.from_entity(goal)
        
    except ValueError as e:
        logger.error(f"Invalid goal data for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create goal for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create calorie goal: {str(e)}"
        )


@router.get("/", response_model=List[CalorieGoalResponse])
async def get_user_goals(
    active_only: bool = True,
    user_id: str = Depends(get_current_user_id),
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
) -> List[CalorieGoalResponse]:
    """
    Get all goals for current user.
    
    Args:
        active_only: If True, returns only active goals
    """
    try:
        goals = await goal_service.get_user_goals(user_id, active_only)
        return [CalorieGoalResponse.from_entity(goal) for goal in goals]
        
    except Exception as e:
        logger.error(f"Failed to get goals for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goals"
        )


@router.get("/current", response_model=Optional[CalorieGoalResponse])
async def get_current_goal(
    user_id: str = Depends(get_current_user_id),
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
) -> Optional[CalorieGoalResponse]:
    """
    Get current active goal for user.
    
    Returns the most recent active goal.
    """
    try:
        goal = await goal_service.get_current_goal(user_id)
        return CalorieGoalResponse.from_entity(goal) if goal else None
        
    except Exception as e:
        logger.error(f"Failed to get current goal for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current goal"
        )


@router.put("/{goal_id}", response_model=CalorieGoalResponse)
async def update_calorie_goal(
    goal_id: str,
    request: CalorieGoalUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
) -> CalorieGoalResponse:
    """
    Update existing calorie goal.
    
    Recalculates targets if parameters change.
    """
    try:
        goal = await goal_service.update_goal(
            goal_id=goal_id,
            user_id=user_id,
            updates=request.dict(exclude_unset=True)
        )
        
        return CalorieGoalResponse.from_entity(goal)
        
    except ValueError as e:
        logger.error(f"Invalid update data for goal {goal_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update goal {goal_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal"
        )


@router.delete("/{goal_id}")
async def deactivate_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
):
    """
    Deactivate a calorie goal (soft delete).
    
    Goal is marked inactive but preserved for analytics.
    """
    try:
        await goal_service.deactivate_goal(goal_id, user_id)
        return {"message": "Goal deactivated successfully"}
        
    except ValueError as e:
        logger.error(f"Invalid goal deactivation {goal_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to deactivate goal {goal_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate goal"
        )


@router.post("/ai-recommend", response_model=CalorieGoalResponse)
async def get_ai_goal_recommendation(
    current_weight_kg: Decimal,
    target_weight_kg: Decimal,
    timeline_weeks: int,
    activity_level: str = "moderate",
    user_id: str = Depends(get_current_user_id),
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
) -> CalorieGoalResponse:
    """
    Get AI-optimized goal recommendation.
    
    Analyzes user data and provides optimal calorie targets.
    """
    try:
        # Determine goal type based on weight difference
        weight_diff = target_weight_kg - current_weight_kg
        
        if weight_diff < -1:
            goal_type = GoalType.WEIGHT_LOSS
        elif weight_diff > 1:
            goal_type = GoalType.WEIGHT_GAIN
        else:
            goal_type = GoalType.MAINTENANCE
        
        # Calculate target date
        from datetime import date, timedelta
        target_date = date.today() + timedelta(weeks=timeline_weeks)
        
        # Weekly change (kg per week)
        weekly_change = weight_diff / timeline_weeks
        
        goal = await goal_service.create_ai_optimized_goal(
            user_id=user_id,
            goal_type=goal_type,
            target_weight_kg=target_weight_kg,
            target_date=target_date,
            weekly_weight_change_kg=abs(weekly_change),
            activity_level=activity_level
        )
        
        return CalorieGoalResponse.from_entity(goal)
        
    except Exception as e:
        logger.error(f"Failed to create AI goal for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI recommendation"
        )


@router.post(
    "/users/{user_id}/weight-loss",
    response_model=CalorieGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Weight Loss Goal with User Metrics",
    description="""
    Create intelligent weight loss goal using Parameter Passing pattern.
    
    **Architecture**: User metrics provided in request body
    - No dependency on user-management service
    - Enables microservice decoupling and reusability
    - Suitable for mobile app and N8N orchestrator usage
    
    **Calculations**:
    - BMR calculated using Mifflin-St Jeor equation
    - TDEE derived from BMR and activity level
    - Daily calorie deficit based on desired weekly loss
    """
)
async def create_weight_loss_goal_with_metrics(
    user_id: str,
    request: WeightLossGoalRequest,
    goal_service: CalorieGoalService = Depends(get_calorie_goal_service)
) -> CalorieGoalResponse:
    """Create weight loss goal with user metrics provided in request."""
    try:
        from uuid import UUID
        
        goal = await goal_service.create_weight_loss_goal(
            user_id=UUID(user_id),
            target_weight_kg=request.target_weight_kg,
            weekly_loss_kg=request.weekly_loss_kg,
            current_weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            age=request.age,
            gender=request.gender,
            activity_level=request.activity_level
        )
        
        logger.info(f"Created weight loss goal for user {user_id}")
        return CalorieGoalResponse.from_entity(goal)
        
    except Exception as e:
        logger.error(f"Failed to create weight loss goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create weight loss goal: {str(e)}"
        )