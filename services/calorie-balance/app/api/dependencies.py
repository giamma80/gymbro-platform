"""
API dependencies module for calorie-balance service.

This module provides dependency injection for FastAPI routes,
including database connections, repository instances, and authentication.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.core.database import get_supabase_client
from app.infrastructure.repositories.repositories import SupabaseUcalorieUbalanceRepository
from app.domain.interfaces import IUcalorieUbalanceRepository
from app.application.services import UcalorieUbalanceService

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer()


def get_calorie_balance_repository() -> IUcalorieUbalanceRepository:
    """
    Dependency to provide UcalorieUbalance repository instance.
    
    Returns:
        IUcalorieUbalanceRepository: Repository instance for database operations
    """
    return SupabaseUcalorieUbalanceRepository()


def get_calorie_balance_service(
    repository: Annotated[IUcalorieUbalanceRepository, Depends(get_calorie_balance_repository)]
) -> UcalorieUbalanceService:
    """
    Dependency to provide UcalorieUbalance service instance.
    
    Args:
        repository: Repository instance injected by FastAPI
        
    Returns:
        UcalorieUbalanceService: Service instance for business logic
    """
    return UcalorieUbalanceService(repository)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and extract user information.
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        dict: User information from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        
        # Use Supabase client to verify the token
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={{"WWW-Authenticate": "Bearer"}},
            )
        
        return {{
            "user_id": user.user.id,
            "email": user.user.email,
            "user_metadata": user.user.user_metadata
        }}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={{"WWW-Authenticate": "Bearer"}},
        )


def get_current_user(user_data: dict = Depends(verify_token)) -> dict:
    """
    Get current authenticated user.
    
    Args:
        user_data: User data from token verification
        
    Returns:
        dict: Current user information
    """
    return user_data


def get_current_user_id(user_data: dict = Depends(get_current_user)) -> str:
    """
    Extract user ID from current user data.
    
    Args:
        user_data: Current user data
        
    Returns:
        str: User ID
    """
    return user_data["user_id"]


# Optional: Database health check dependency
async def check_database_health() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        supabase = get_supabase_client()
        # Simple query to test connection
        response = supabase.table("_health_check").select("count").execute()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {{e}}")
        return False


# Type aliases for commonly used dependencies
UcalorieUbalanceRepositoryDep = Annotated[IUcalorieUbalanceRepository, Depends(get_calorie_balance_repository)]
UcalorieUbalanceServiceDep = Annotated[UcalorieUbalanceService, Depends(get_calorie_balance_service)]
CurrentUserDep = Annotated[dict, Depends(get_current_user)]
CurrentUserIdDep = Annotated[str, Depends(get_current_user_id)]
