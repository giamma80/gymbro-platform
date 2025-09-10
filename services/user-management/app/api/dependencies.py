"""
Dependency injection for authentication system.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.core.database import get_supabase_client
from app.domain.entities import User
from app.infrastructure.auth_repositories import (
    SupabaseAuthCredentialsRepository,
    SupabaseAuthSessionRepository,
    SupabasePasswordResetTokenRepository,
    SupabaseEmailVerificationTokenRepository,
    SupabaseAuditLogRepository
)
from app.infrastructure.repositories import (
    UserRepository,
    UserProfileRepository,
    PrivacySettingsRepository,
    UserServiceContextRepository
)
from app.application.auth_services import AuthenticationService
from app.core.security import decode_access_token

security = HTTPBearer()


def get_auth_service(
    supabase_client=Depends(get_supabase_client)
) -> AuthenticationService:
    """Get authentication service with all dependencies."""
    user_repo = UserRepository()  # No parameters needed
    user_profile_repo = UserProfileRepository()
    auth_credentials_repo = SupabaseAuthCredentialsRepository(supabase_client)
    auth_session_repo = SupabaseAuthSessionRepository(supabase_client)
    password_reset_repo = SupabasePasswordResetTokenRepository(supabase_client)
    email_verification_repo = SupabaseEmailVerificationTokenRepository(
        supabase_client
    )
    audit_log_repo = SupabaseAuditLogRepository(supabase_client)
    
    return AuthenticationService(
        user_repo=user_repo,
        auth_credentials_repo=auth_credentials_repo,
        auth_session_repo=auth_session_repo,
        password_reset_repo=password_reset_repo,
        email_verification_repo=email_verification_repo,
        audit_log_repo=audit_log_repo,
        user_profile_repo=user_profile_repo
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        
        if user is None:
            raise credentials_exception
            
        return user
        
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None."""
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        return auth_service.get_current_user(token)
    except Exception:
        return None
