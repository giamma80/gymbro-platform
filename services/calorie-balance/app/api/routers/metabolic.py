"""
Metabolic Profile API Router

Handles metabolic calculations using Parameter Passing pattern for microservice decoupling.
User metrics are provided by client instead of accessing user-management service directly.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.schemas import (
    MetabolicCalculationRequest, 
    MetabolicProfileResponse
)
from app.core.dependencies import get_metabolic_service
from app.application.services import MetabolicCalculationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/users/{user_id}/profile/metabolic",
    tags=["Metabolic Profiles"]
)


@router.post(
    "/calculate",
    response_model=MetabolicProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate Metabolic Profile",
    description="""
    Calculate BMR and TDEE using user metrics provided in request body.
    
    **Architecture**: Parameter Passing Pattern
    - User metrics provided by client (mobile app, N8N orchestrator)
    - No direct access to user-management service
    - Ensures microservice decoupling and reusability
    
    **Calculations**:
    - BMR: Mifflin-St Jeor equation
    - TDEE: BMR × activity level multiplier
    """
)
async def calculate_metabolic_profile(
    user_id: UUID,
    request: MetabolicCalculationRequest,
    metabolic_service: MetabolicCalculationService = Depends(get_metabolic_service)
) -> MetabolicProfileResponse:
    """Calculate metabolic profile with user data from request body."""
    try:
        logger.info(f"Calculating metabolic profile for user {user_id}")
        
        profile = await metabolic_service.calculate_metabolic_profile(
            user_id=user_id,
            weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            age=request.age,
            gender=request.gender,
            activity_level=request.activity_level
        )
        
        return MetabolicProfileResponse.model_validate(profile)
        
    except Exception as e:
        logger.error(f"Failed to calculate metabolic profile for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate metabolic profile: {str(e)}"
        )


@router.get(
    "",
    response_model=Optional[MetabolicProfileResponse],
    summary="Get Latest Metabolic Profile",
    description="Get the most recent metabolic profile for the user."
)
async def get_metabolic_profile(
    user_id: UUID,
    metabolic_service: MetabolicCalculationService = Depends(get_metabolic_service)
) -> Optional[MetabolicProfileResponse]:
    """Get latest metabolic profile for user."""
    try:
        logger.info(f"Getting metabolic profile for user {user_id}")
        
        profile = await metabolic_service.profile_repo.get_latest(str(user_id))
        
        if not profile:
            return None
            
        return MetabolicProfileResponse.model_validate(profile)
        
    except Exception as e:
        logger.error(f"Failed to get metabolic profile for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metabolic profile: {str(e)}"
        )