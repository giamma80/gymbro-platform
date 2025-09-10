"""
Domain repositories for user management service.
Defines interfaces for data access layer.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from .entities import (
    User, UserProfile, PrivacySettings, AuthCredentials, AuthSession,
    SocialAuthProfile, AuditLog, PasswordResetToken, EmailVerificationToken
)


class UserRepository(ABC):
    """Repository interface for User entities."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        pass
    
    @abstractmethod
    async def list_users(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """List users with pagination and filters."""
        pass


class UserProfileRepository(ABC):
    """Repository interface for UserProfile entities."""
    
    @abstractmethod
    async def create(self, profile: UserProfile) -> UserProfile:
        """Create user profile."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """Get profile by user ID."""
        pass
    
    @abstractmethod
    async def update(self, profile: UserProfile) -> UserProfile:
        """Update user profile."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user profile."""
        pass


class PrivacySettingsRepository(ABC):
    """Repository interface for PrivacySettings entities."""
    
    @abstractmethod
    async def create(self, settings: PrivacySettings) -> PrivacySettings:
        """Create privacy settings."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[PrivacySettings]:
        """Get privacy settings by user ID."""
        pass
    
    @abstractmethod
    async def update(self, settings: PrivacySettings) -> PrivacySettings:
        """Update privacy settings."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete privacy settings."""
        pass


class AuthCredentialsRepository(ABC):
    """Repository interface for AuthCredentials entities."""
    
    @abstractmethod
    async def create(self, credentials: AuthCredentials) -> AuthCredentials:
        """Create authentication credentials."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[AuthCredentials]:
        """Get credentials by user ID."""
        pass
    
    @abstractmethod
    async def update(self, credentials: AuthCredentials) -> AuthCredentials:
        """Update authentication credentials."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete authentication credentials."""
        pass
    
    @abstractmethod
    async def increment_failed_attempts(self, user_id: UUID) -> int:
        """Increment failed login attempts."""
        pass
    
    @abstractmethod
    async def reset_failed_attempts(self, user_id: UUID) -> bool:
        """Reset failed login attempts."""
        pass


class AuthSessionRepository(ABC):
    """Repository interface for AuthSession entities."""
    
    @abstractmethod
    async def create(self, session: AuthSession) -> AuthSession:
        """Create authentication session."""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[AuthSession]:
        """Get session by token."""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        active_only: bool = True
    ) -> List[AuthSession]:
        """Get sessions by user ID."""
        pass
    
    @abstractmethod
    async def update(self, session: AuthSession) -> AuthSession:
        """Update session."""
        pass
    
    @abstractmethod
    async def invalidate_session(self, token: str) -> bool:
        """Invalidate session."""
        pass
    
    @abstractmethod
    async def invalidate_user_sessions(self, user_id: UUID) -> int:
        """Invalidate all user sessions."""
        pass
    
    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        pass


class SocialAuthProfileRepository(ABC):
    """Repository interface for SocialAuthProfile entities."""
    
    @abstractmethod
    async def create(self, profile: SocialAuthProfile) -> SocialAuthProfile:
        """Create social auth profile."""
        pass
    
    @abstractmethod
    async def get_by_provider_id(
        self,
        provider: str,
        provider_user_id: str
    ) -> Optional[SocialAuthProfile]:
        """Get profile by provider and provider user ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[SocialAuthProfile]:
        """Get social profiles by user ID."""
        pass
    
    @abstractmethod
    async def update(self, profile: SocialAuthProfile) -> SocialAuthProfile:
        """Update social auth profile."""
        pass
    
    @abstractmethod
    async def delete(self, profile_id: UUID) -> bool:
        """Delete social auth profile."""
        pass


class AuditLogRepository(ABC):
    """Repository interface for AuditLog entities."""
    
    @abstractmethod
    async def create(self, log: AuditLog) -> AuditLog:
        """Create audit log entry."""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs by user ID with pagination and date filters."""
        pass
    
    @abstractmethod
    async def get_by_action(
        self,
        action: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs by action type."""
        pass
    
    @abstractmethod
    async def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """Clean up old audit logs."""
        pass


class PasswordResetTokenRepository(ABC):
    """Repository interface for PasswordResetToken entities."""
    
    @abstractmethod
    async def create(self, token: PasswordResetToken) -> PasswordResetToken:
        """Create password reset token."""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get token by token string."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[PasswordResetToken]:
        """Get active tokens by user ID."""
        pass
    
    @abstractmethod
    async def invalidate_token(self, token: str) -> bool:
        """Invalidate token."""
        pass
    
    @abstractmethod
    async def invalidate_user_tokens(self, user_id: UUID) -> int:
        """Invalidate all user tokens."""
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        pass


class EmailVerificationTokenRepository(ABC):
    """Repository interface for EmailVerificationToken entities."""
    
    @abstractmethod
    async def create(self, token: EmailVerificationToken) -> EmailVerificationToken:
        """Create email verification token."""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[EmailVerificationToken]:
        """Get token by token string."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[EmailVerificationToken]:
        """Get active tokens by user ID."""
        pass
    
    @abstractmethod
    async def invalidate_token(self, token: str) -> bool:
        """Invalidate token."""
        pass
    
    @abstractmethod
    async def invalidate_user_tokens(self, user_id: UUID) -> int:
        """Invalidate all user tokens."""
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        pass
