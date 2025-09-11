"""
User Repository - Supabase Implementation
========================================
Service: user-management
Schema: user_management
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog

from app.core.schema_tables import get_schema_manager
from app.domain.entities import (
    GenderType,
    PrivacySettings,
    User,
    UserProfile,
    UserServiceContext,
    UserStatus,
)

logger = structlog.get_logger()


class UserRepository:
    """Repository for User entity operations."""

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.users

    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            data = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "status": user.status.value,
                "email_verified_at": user.email_verified_at.isoformat()
                if user.email_verified_at
                else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login_at": user.last_login_at.isoformat()
                if user.last_login_at
                else None,
            }

            result = self.table.insert(data).execute()

            if result.data:
                logger.info("User created", user_id=user.id, email=user.email)
                return self._map_to_entity(result.data[0])
            else:
                raise Exception("No data returned from user creation")

        except Exception as e:
            logger.error("Failed to create user", user_id=user.id, error=str(e))
            raise

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            result = self.table.select("*").eq("id", str(user_id)).execute()

            if result.data:
                return self._map_to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error("Failed to get user by ID", user_id=user_id, error=str(e))
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = self.table.select("*").eq("email", email).execute()

            if result.data:
                return self._map_to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error("Failed to get user by email", email=email, error=str(e))
            raise

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            result = self.table.select("*").eq("username", username).execute()

            if result.data:
                return self._map_to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(
                "Failed to get user by username", username=username, error=str(e)
            )
            raise

    async def update(self, user: User) -> User:
        """Update existing user."""
        try:
            data = {
                "email": user.email,
                "username": user.username,
                "status": user.status.value,
                "email_verified_at": user.email_verified_at.isoformat()
                if user.email_verified_at
                else None,
                "updated_at": datetime.utcnow().isoformat(),
                "last_login_at": user.last_login_at.isoformat()
                if user.last_login_at
                else None,
            }

            result = self.table.update(data).eq("id", str(user.id)).execute()

            if result.data:
                logger.info("User updated", user_id=user.id)
                return self._map_to_entity(result.data[0])
            else:
                raise Exception("No data returned from user update")

        except Exception as e:
            logger.error("Failed to update user", user_id=user.id, error=str(e))
            raise

    async def delete(self, user_id: UUID) -> bool:
        """Delete user (soft delete by changing status)."""
        try:
            result = (
                self.table.update(
                    {
                        "status": UserStatus.DELETED.value,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", str(user_id))
                .execute()
            )

            logger.info("User deleted", user_id=user_id)
            return True

        except Exception as e:
            logger.error("Failed to delete user", user_id=user_id, error=str(e))
            raise

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination."""
        try:
            result = self.table.select("*").range(offset, offset + limit - 1).execute()

            return [self._map_to_entity(row) for row in result.data or []]

        except Exception as e:
            logger.error("Failed to get all users", error=str(e))
            raise

    async def list_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List active users with pagination."""
        try:
            result = (
                self.table.select("*")
                .eq("status", UserStatus.ACTIVE.value)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [self._map_to_entity(row) for row in result.data or []]

        except Exception as e:
            logger.error("Failed to list active users", error=str(e))
            raise

    def _map_to_entity(self, data: Dict[str, Any]) -> User:
        """Map database row to User entity."""
        return User(
            id=UUID(data["id"]),
            email=data["email"],
            username=data["username"],
            status=UserStatus(data["status"]),
            email_verified_at=datetime.fromisoformat(data["email_verified_at"])
            if data["email_verified_at"]
            else None,
            created_at=datetime.fromisoformat(data["created_at"])
            if data["created_at"]
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data["updated_at"]
            else None,
            last_login_at=datetime.fromisoformat(data["last_login_at"])
            if data["last_login_at"]
            else None,
        )


class UserProfileRepository:
    """Repository for UserProfile entity operations."""

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.user_profiles

    async def create(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile."""
        try:
            data = {
                "id": str(profile.id),
                "user_id": str(profile.user_id),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "display_name": profile.display_name,
                "avatar_url": profile.avatar_url,
                "date_of_birth": profile.date_of_birth.isoformat()
                if profile.date_of_birth
                else None,
                "gender": profile.gender.value if profile.gender else None,
                "timezone": profile.timezone,
                "locale": profile.locale,
                "preferences": profile.preferences,
                "created_at": profile.created_at.isoformat()
                if profile.created_at
                else None,
                "updated_at": profile.updated_at.isoformat()
                if profile.updated_at
                else None,
            }

            result = self.table.insert(data).execute()

            if result.data:
                logger.info("User profile created", user_id=profile.user_id)
                return self._map_to_entity(result.data[0])
            else:
                raise Exception("No data returned from profile creation")

        except Exception as e:
            logger.error(
                "Failed to create user profile", user_id=profile.user_id, error=str(e)
            )
            raise

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by user ID."""
        try:
            result = self.table.select("*").eq("user_id", str(user_id)).execute()

            if result.data:
                return self._map_to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error("Failed to get user profile", user_id=user_id, error=str(e))
            raise

    async def update(self, profile: UserProfile) -> UserProfile:
        """Update existing user profile."""
        try:
            data = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "display_name": profile.display_name,
                "avatar_url": profile.avatar_url,
                "date_of_birth": profile.date_of_birth.isoformat()
                if profile.date_of_birth
                else None,
                "gender": profile.gender.value if profile.gender else None,
                "timezone": profile.timezone,
                "locale": profile.locale,
                "preferences": profile.preferences,
                "updated_at": datetime.utcnow().isoformat(),
            }

            result = (
                self.table.update(data).eq("user_id", str(profile.user_id)).execute()
            )

            if result.data:
                logger.info("User profile updated", user_id=profile.user_id)
                return self._map_to_entity(result.data[0])
            else:
                raise Exception("No data returned from profile update")

        except Exception as e:
            logger.error(
                "Failed to update user profile", user_id=profile.user_id, error=str(e)
            )
            raise

    def _map_to_entity(self, data: Dict[str, Any]) -> UserProfile:
        """Map database row to UserProfile entity."""
        return UserProfile(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            display_name=data.get("display_name"),
            avatar_url=data.get("avatar_url"),
            date_of_birth=datetime.fromisoformat(data["date_of_birth"]).date()
            if data.get("date_of_birth")
            else None,
            gender=GenderType(data["gender"]) if data.get("gender") else None,
            timezone=data.get("timezone", "UTC"),
            locale=data.get("locale", "en-US"),
            preferences=data.get("preferences", {}),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )


class PrivacySettingsRepository:
    """Repository for PrivacySettings entity operations."""

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.privacy_settings

    async def create(self, settings: PrivacySettings) -> PrivacySettings:
        """Create new privacy settings."""
        try:
            data = {
                "id": str(settings.id),
                "user_id": str(settings.user_id),
                "data_processing_consent": settings.data_processing_consent,
                "marketing_consent": settings.marketing_consent,
                "analytics_consent": settings.analytics_consent,
                "profile_visibility": settings.profile_visibility,
                "health_data_sharing": settings.health_data_sharing,
                "preferences": settings.preferences,
                "consent_given_at": settings.consent_given_at.isoformat()
                if settings.consent_given_at
                else None,
                "updated_at": settings.updated_at.isoformat()
                if settings.updated_at
                else None,
            }

            result = self.table.insert(data).execute()

            if result.data:
                logger.info("Privacy settings created", user_id=settings.user_id)
                return self._map_to_entity(result.data[0])
            else:
                raise Exception("No data returned from privacy settings creation")

        except Exception as e:
            logger.error(
                "Failed to create privacy settings",
                user_id=settings.user_id,
                error=str(e),
            )
            raise

    async def get_by_user_id(self, user_id: UUID) -> Optional[PrivacySettings]:
        """Get privacy settings by user ID."""
        try:
            result = self.table.select("*").eq("user_id", str(user_id)).execute()

            if result.data:
                return self._map_to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(
                "Failed to get privacy settings", user_id=user_id, error=str(e)
            )
            raise

    async def update(self, settings: PrivacySettings) -> PrivacySettings:
        """Update existing privacy settings."""
        try:
            data = {
                "data_processing_consent": settings.data_processing_consent,
                "marketing_consent": settings.marketing_consent,
                "analytics_consent": settings.analytics_consent,
                "profile_visibility": settings.profile_visibility,
                "health_data_sharing": settings.health_data_sharing,
                "preferences": settings.preferences,
                "consent_given_at": settings.consent_given_at.isoformat()
                if settings.consent_given_at
                else None,
                "updated_at": datetime.utcnow().isoformat(),
            }

            result = (
                self.table.update(data).eq("user_id", str(settings.user_id)).execute()
            )

            if result.data:
                logger.info("Privacy settings updated", user_id=settings.user_id)
                return self._map_to_entity(result.data[0])
            else:
                raise Exception("No data returned from privacy settings update")

        except Exception as e:
            logger.error(
                "Failed to update privacy settings",
                user_id=settings.user_id,
                error=str(e),
            )
            raise

    def _map_to_entity(self, data: Dict[str, Any]) -> PrivacySettings:
        """Map database row to PrivacySettings entity."""
        return PrivacySettings(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            data_processing_consent=data.get("data_processing_consent", False),
            marketing_consent=data.get("marketing_consent", False),
            analytics_consent=data.get("analytics_consent", False),
            profile_visibility=data.get("profile_visibility", False),
            health_data_sharing=data.get("health_data_sharing", False),
            preferences=data.get("preferences", {}),
            consent_given_at=datetime.fromisoformat(data["consent_given_at"])
            if data.get("consent_given_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )


class UserServiceContextRepository:
    """Repository for UserServiceContext view operations."""

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.view = self.schema_manager.user_service_context

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserServiceContext]:
        """Get complete user service context by user ID."""
        try:
            result = self.view.select("*").eq("user_id", str(user_id)).execute()

            if result.data:
                return self._map_to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(
                "Failed to get user service context", user_id=user_id, error=str(e)
            )
            raise

    async def list_active_contexts(
        self, limit: int = 100, offset: int = 0
    ) -> List[UserServiceContext]:
        """List active user service contexts."""
        try:
            result = (
                self.view.select("*")
                .eq("user_status", UserStatus.ACTIVE.value)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [self._map_to_entity(row) for row in result.data or []]

        except Exception as e:
            logger.error("Failed to list user service contexts", error=str(e))
            raise

    def _map_to_entity(self, data: Dict[str, Any]) -> UserServiceContext:
        """Map database row to UserServiceContext entity."""
        return UserServiceContext(
            user_id=UUID(data["user_id"]),
            email=data["email"],
            username=data["username"],
            user_status=UserStatus(data["user_status"]),
            email_verified_at=datetime.fromisoformat(data["email_verified_at"])
            if data.get("email_verified_at")
            else None,
            display_name=data.get("display_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            timezone=data.get("timezone", "UTC"),
            locale=data.get("locale", "en-US"),
            preferences=data.get("preferences", {}),
            health_data_sharing=data.get("health_data_sharing", False),
            analytics_consent=data.get("analytics_consent", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
