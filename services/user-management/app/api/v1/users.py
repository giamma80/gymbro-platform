"""
User Management API - REST Endpoints
====================================
Service: user-management
Schema: user_management
"""

import asyncio
from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from app.api.schemas import (
    PrivacySettingsResponse,
    PrivacySettingsUpdateRequest,
    UserCreateRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserResponse,
    UserServiceContextResponse,
    UserUpdateRequest,
)
from app.infrastructure.repositories import (
    PrivacySettingsRepository,
    UserProfileRepository,
    UserRepository,
    UserServiceContextRepository,
)

logger = structlog.get_logger()
router = APIRouter()

# Initialize repositories
user_repo = UserRepository()
profile_repo = UserProfileRepository()
privacy_repo = PrivacySettingsRepository()
context_repo = UserServiceContextRepository()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    """Get user by ID."""
    try:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.from_entity(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)
):
    """List active users with pagination."""
    try:
        users = await user_repo.list_active_users(limit=limit, offset=offset)
        return [UserResponse.from_entity(user) for user in users]
    except Exception as e:
        logger.error("Failed to list users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """Get user by email address."""
    try:
        user = await user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.from_entity(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user by email", email=email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: UUID):
    """Get user profile by user ID."""
    try:
        profile = await profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )
        return UserProfileResponse.from_entity(profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user profile", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/users/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(user_id: UUID, request: UserProfileUpdateRequest):
    """Update user profile."""
    try:
        # Get existing profile
        profile = await profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        # Update profile with request data
        updated_profile = request.update_entity(profile)

        # Save changes
        updated_profile = await profile_repo.update(updated_profile)

        return UserProfileResponse.from_entity(updated_profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user profile", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users/{user_id}/privacy", response_model=PrivacySettingsResponse)
async def get_privacy_settings(user_id: UUID):
    """Get user privacy settings."""
    try:
        settings = await privacy_repo.get_by_user_id(user_id)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Privacy settings not found",
            )
        return PrivacySettingsResponse.from_entity(settings)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get privacy settings", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/users/{user_id}/privacy", response_model=PrivacySettingsResponse)
async def update_privacy_settings(user_id: UUID, request: PrivacySettingsUpdateRequest):
    """Update user privacy settings."""
    try:
        # Get existing settings
        settings = await privacy_repo.get_by_user_id(user_id)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Privacy settings not found",
            )

        # Update settings with request data
        updated_settings = request.update_entity(settings)

        # Save changes
        updated_settings = await privacy_repo.update(updated_settings)

        return PrivacySettingsResponse.from_entity(updated_settings)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update privacy settings", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users/{user_id}/context", response_model=UserServiceContextResponse)
async def get_user_service_context(user_id: UUID):
    """Get complete user service context for GraphQL Federation."""
    try:
        context = await context_repo.get_by_user_id(user_id)
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User context not found"
            )
        return UserServiceContextResponse.from_entity(context)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user context", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users/context/active", response_model=List[UserServiceContextResponse])
async def list_active_user_contexts(
    limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)
):
    """List active user service contexts for federation."""
    try:
        contexts = await context_repo.list_active_contexts(limit=limit, offset=offset)
        return [UserServiceContextResponse.from_entity(context) for context in contexts]
    except Exception as e:
        logger.error("Failed to list user contexts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/users/{user_id}/verify-email")
async def verify_user_email(user_id: UUID):
    """Verify user email address."""
    try:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            return {"message": "Email already verified", "verified": True}

        # Mark email as verified
        user.verify_email()

        # Save changes
        await user_repo.update(user)

        return {"message": "Email verified successfully", "verified": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to verify email", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/users/{user_id}/login")
async def record_user_login(user_id: UUID):
    """Record user login timestamp."""
    try:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Record login
        user.record_login()

        # Save changes
        await user_repo.update(user)

        return {
            "message": "Login recorded successfully",
            "last_login": user.last_login_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to record login", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
