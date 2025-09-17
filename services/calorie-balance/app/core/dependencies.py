"""
FastAPI Dependencies - Calorie Balance Service

Dependency injection for services, authentication, and cross-cutting concerns.
"""

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

# Services
from app.application.services import (
    AnalyticsService,
    CalorieEventService,
    CalorieGoalService,
    MetabolicCalculationService,
)

# Repositories
from app.infrastructure.repositories.repositories import (
    SupabaseCalorieEventRepository,
    SupabaseCalorieGoalRepository,
    SupabaseCalorieSearchRepository,
    SupabaseDailyBalanceRepository,
    SupabaseMetabolicProfileRepository,
    SupabaseTemporalAnalyticsRepository,
)

logger = logging.getLogger(__name__)


# =============================================================================
# REPOSITORY DEPENDENCIES - Singleton Instances
# =============================================================================
# NOTE: User repository removed - user management handled by separate microservice


@lru_cache()
def get_calorie_event_repository() -> SupabaseCalorieEventRepository:
    """Get calorie event repository instance."""
    return SupabaseCalorieEventRepository()


@lru_cache()
def get_calorie_goal_repository() -> SupabaseCalorieGoalRepository:
    """Get calorie goal repository instance."""
    return SupabaseCalorieGoalRepository()


@lru_cache()
def get_daily_balance_repository() -> SupabaseDailyBalanceRepository:
    """Get daily balance repository instance."""
    return SupabaseDailyBalanceRepository()


@lru_cache()
def get_metabolic_profile_repository() -> SupabaseMetabolicProfileRepository:
    """Get metabolic profile repository instance."""
    return SupabaseMetabolicProfileRepository()


@lru_cache()
def get_analytics_repository() -> SupabaseTemporalAnalyticsRepository:
    """Get temporal analytics repository instance."""
    return SupabaseTemporalAnalyticsRepository()


@lru_cache()
def get_search_repository() -> SupabaseCalorieSearchRepository:
    """Get search repository instance."""
    return SupabaseCalorieSearchRepository()


# =============================================================================
# SERVICE DEPENDENCIES - Composed Services
# =============================================================================


def get_metabolic_service(
    profile_repo: SupabaseMetabolicProfileRepository = Depends(
        get_metabolic_profile_repository
    ),
) -> MetabolicCalculationService:
    """Get metabolic calculation service."""
    return MetabolicCalculationService(profile_repo)


def get_calorie_event_service(
    event_repo: SupabaseCalorieEventRepository = Depends(get_calorie_event_repository),
    balance_repo: SupabaseDailyBalanceRepository = Depends(
        get_daily_balance_repository
    ),
) -> CalorieEventService:
    """Get calorie event service - HIGH FREQUENCY."""
    return CalorieEventService(event_repo, balance_repo)


def get_calorie_goal_service(
    goal_repo: SupabaseCalorieGoalRepository = Depends(get_calorie_goal_repository),
    metabolic_service: MetabolicCalculationService = Depends(get_metabolic_service),
) -> CalorieGoalService:
    """Get calorie goal service."""
    return CalorieGoalService(goal_repo, metabolic_service)


def get_analytics_service(
    analytics_repo: SupabaseTemporalAnalyticsRepository = Depends(
        get_analytics_repository
    ),
    event_repo: SupabaseCalorieEventRepository = Depends(get_calorie_event_repository),
    balance_repo: SupabaseDailyBalanceRepository = Depends(
        get_daily_balance_repository
    ),
) -> AnalyticsService:
    """Get analytics service - Timeline Analytics."""
    return AnalyticsService(analytics_repo, event_repo, balance_repo)


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None
) -> str:
    """
    Extract user ID from JWT token.

    In production, this would validate JWT and extract user_id.
    For development, we'll use a simple header-based approach.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # In development mode, accept simple format: "Bearer user-id"
        # In production, this would decode JWT and extract user_id
        if authorization.startswith("Bearer "):
            user_id = authorization[7:]  # Remove "Bearer " prefix

            if not user_id:
                raise ValueError("Empty user ID")

            return user_id
        else:
            raise ValueError("Invalid authorization format")

    except Exception as e:
        logger.error(f"Failed to extract user ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    authorization: Annotated[str | None, Header()] = None
) -> str | None:
    """Get user ID if provided, None otherwise (for public endpoints)."""
    try:
        return await get_current_user_id(authorization)
    except HTTPException:
        return None


# =============================================================================
# DATABASE CONNECTION DEPENDENCIES
# =============================================================================


@lru_cache()
def get_database_config() -> dict:
    """Get database configuration."""
    from app.core.config import get_settings

    settings = get_settings()

    return {
        "url": settings.supabase_url,
        "key": settings.supabase_anon_key,
        "schema": settings.database_schema,
    }


# =============================================================================
# MONITORING AND OBSERVABILITY
# =============================================================================


async def log_request_metrics(user_id: str = Depends(get_current_user_id)):
    """Log request metrics for monitoring."""
    # In production, this would send metrics to monitoring system
    logger.info(f"API request from user: {user_id}")
    return user_id


# =============================================================================
# RATE LIMITING DEPENDENCIES (Future)
# =============================================================================


async def check_rate_limit(user_id: str = Depends(get_current_user_id)):
    """
    Check rate limits for high-frequency endpoints.

    Important for calorie event endpoints that receive high mobile traffic.
    """
    # TODO: Implement rate limiting logic
    # - Redis-based sliding window
    # - Different limits per endpoint type
    # - User-specific limits

    return user_id


# =============================================================================
# VALIDATION DEPENDENCIES
# =============================================================================


async def validate_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """Validate date range parameters."""
    from datetime import datetime

    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        if start > end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date",
            )

        # Limit to 1 year max
        if (end - start).days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days",
            )

        return start_date, end_date

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )
