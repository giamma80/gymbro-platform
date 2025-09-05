from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...core.database import get_session
from ...core.schemas import APIResponse
from ...infrastructure.database.repositories import SqlUserRepository
from ...infrastructure.database.uow import SqlUnitOfWork
from ...infrastructure.services import DefaultMetabolicCalculationService
from ...application.commands import (
    CreateUserCommand, UpdateUserProfileCommand, UserCommandHandler
)
from ...application.queries import (
    GetUserQuery, UserQueryHandler
)
from ...application.services import MetabolicProfileService
from ..schemas import UserCreateRequest, UserUpdateRequest, UserResponse

router = APIRouter()


def get_user_dependencies(session: AsyncSession = Depends(get_session)):
    """Get user-related dependencies"""
    user_repo = SqlUserRepository(session)
    metabolic_service = DefaultMetabolicCalculationService()
    uow = SqlUnitOfWork(session)
    
    user_command_handler = UserCommandHandler(user_repo, metabolic_service, uow)
    user_query_handler = UserQueryHandler(user_repo)
    
    return user_command_handler, user_query_handler


@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    dependencies=Depends(get_user_dependencies)
):
    """Create a new user"""
    user_command_handler, _ = dependencies
    
    try:
        command = CreateUserCommand(
            user_id=request.user_id,
            email=request.email,
            full_name=request.full_name
        )
        
        user = await user_command_handler.handle_create_user(command)
        
        return APIResponse(
            success=True,
            message="User created successfully",
            data=UserResponse.from_orm(user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=APIResponse)
async def get_user(
    user_id: str,
    dependencies=Depends(get_user_dependencies)
):
    """Get user by ID"""
    _, user_query_handler = dependencies
    
    query = GetUserQuery(user_id)
    user = await user_query_handler.handle_get_user(query)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return APIResponse(
        success=True,
        data=UserResponse.from_orm(user)
    )


@router.put("/{user_id}", response_model=APIResponse)
async def update_user_profile(
    user_id: str,
    request: UserUpdateRequest,
    dependencies=Depends(get_user_dependencies)
):
    """Update user profile"""
    user_command_handler, _ = dependencies
    
    try:
        command = UpdateUserProfileCommand(
            user_id=user_id,
            age=request.age,
            gender=request.gender.value if request.gender else None,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            activity_level=request.activity_level.value if request.activity_level else None
        )
        
        user = await user_command_handler.handle_update_profile(command)
        
        return APIResponse(
            success=True,
            message="User profile updated successfully",
            data=UserResponse.from_orm(user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
