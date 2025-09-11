"""
API Schemas - Pydantic Models for User Management
=================================================
Service: user-management
Schema: user_management
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from app.domain.entities import (
    GenderType,
    PrivacySettings,
    User,
    UserProfile,
    UserServiceContext,
    UserStatus,
)


class UserStatusEnum(str, Enum):
    """User status for API responses."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class GenderTypeEnum(str, Enum):
    """Gender type for API responses."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


# User Schemas
class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: EmailStr
    username: str
    status: UserStatusEnum
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        """Create response from User entity."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            status=UserStatusEnum(user.status.value),
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )


class UserCreateRequest(BaseModel):
    """User creation request schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

    @validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores and hyphens"
            )
        return v


class UserUpdateRequest(BaseModel):
    """User update request schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    status: Optional[UserStatusEnum] = None

    @validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if v and not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores and hyphens"
            )
        return v


# User Profile Schemas
class UserProfileResponse(BaseModel):
    """User profile response schema."""

    id: UUID
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderTypeEnum] = None
    timezone: str
    locale: str
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    full_name: str
    age: Optional[int] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, profile: UserProfile) -> "UserProfileResponse":
        """Create response from UserProfile entity."""
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            date_of_birth=profile.date_of_birth,
            gender=GenderTypeEnum(profile.gender.value) if profile.gender else None,
            timezone=profile.timezone,
            locale=profile.locale,
            preferences=profile.preferences,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            full_name=profile.full_name,
            age=profile.age,
        )


class UserProfileUpdateRequest(BaseModel):
    """User profile update request schema."""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=150)
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderTypeEnum] = None
    timezone: Optional[str] = Field(None, max_length=50)
    locale: Optional[str] = Field(None, max_length=10)
    preferences: Optional[Dict[str, Any]] = None

    @validator("date_of_birth")
    def validate_age(cls, v):
        """Validate user is at least 13 years old."""
        if v:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 13:
                raise ValueError("User must be at least 13 years old")
        return v

    def update_entity(self, profile: UserProfile) -> UserProfile:
        """Update entity with request data."""
        if self.first_name is not None:
            profile.first_name = self.first_name
        if self.last_name is not None:
            profile.last_name = self.last_name
        if self.display_name is not None:
            profile.display_name = self.display_name
        if self.avatar_url is not None:
            profile.avatar_url = self.avatar_url
        if self.date_of_birth is not None:
            profile.date_of_birth = self.date_of_birth
        if self.gender is not None:
            profile.gender = GenderType(self.gender.value)
        if self.timezone is not None:
            profile.timezone = self.timezone
        if self.locale is not None:
            profile.locale = self.locale
        if self.preferences is not None:
            profile.preferences.update(self.preferences)

        profile.updated_at = datetime.utcnow()
        return profile


# Privacy Settings Schemas
class PrivacySettingsResponse(BaseModel):
    """Privacy settings response schema."""

    id: UUID
    user_id: UUID
    data_processing_consent: bool
    marketing_consent: bool
    analytics_consent: bool
    profile_visibility: bool
    health_data_sharing: bool
    preferences: Dict[str, Any]
    consent_given_at: Optional[datetime] = None
    updated_at: datetime
    has_basic_consent: bool
    consent_level: str

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, settings: PrivacySettings) -> "PrivacySettingsResponse":
        """Create response from PrivacySettings entity."""
        return cls(
            id=settings.id,
            user_id=settings.user_id,
            data_processing_consent=settings.data_processing_consent,
            marketing_consent=settings.marketing_consent,
            analytics_consent=settings.analytics_consent,
            profile_visibility=settings.profile_visibility,
            health_data_sharing=settings.health_data_sharing,
            preferences=settings.preferences,
            consent_given_at=settings.consent_given_at,
            updated_at=settings.updated_at,
            has_basic_consent=settings.has_basic_consent,
            consent_level=settings.consent_level,
        )


class PrivacySettingsUpdateRequest(BaseModel):
    """Privacy settings update request schema."""

    data_processing_consent: Optional[bool] = None
    marketing_consent: Optional[bool] = None
    analytics_consent: Optional[bool] = None
    profile_visibility: Optional[bool] = None
    health_data_sharing: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None

    def update_entity(self, settings: PrivacySettings) -> PrivacySettings:
        """Update entity with request data."""
        if self.data_processing_consent is not None:
            settings.update_consent(
                "data_processing_consent", self.data_processing_consent
            )
        if self.marketing_consent is not None:
            settings.update_consent("marketing_consent", self.marketing_consent)
        if self.analytics_consent is not None:
            settings.update_consent("analytics_consent", self.analytics_consent)
        if self.profile_visibility is not None:
            settings.update_consent("profile_visibility", self.profile_visibility)
        if self.health_data_sharing is not None:
            settings.update_consent("health_data_sharing", self.health_data_sharing)
        if self.preferences is not None:
            settings.preferences.update(self.preferences)

        return settings


# User Service Context Schema
class UserServiceContextResponse(BaseModel):
    """User service context response for GraphQL Federation."""

    user_id: UUID
    email: EmailStr
    username: str
    user_status: UserStatusEnum
    email_verified_at: Optional[datetime] = None
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: str
    locale: str
    preferences: Dict[str, Any]
    health_data_sharing: bool
    analytics_consent: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_verified: bool
    full_name: str

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, context: UserServiceContext) -> "UserServiceContextResponse":
        """Create response from UserServiceContext entity."""
        return cls(
            user_id=context.user_id,
            email=context.email,
            username=context.username,
            user_status=UserStatusEnum(context.user_status.value),
            email_verified_at=context.email_verified_at,
            display_name=context.display_name,
            first_name=context.first_name,
            last_name=context.last_name,
            timezone=context.timezone,
            locale=context.locale,
            preferences=context.preferences,
            health_data_sharing=context.health_data_sharing,
            analytics_consent=context.analytics_consent,
            created_at=context.created_at,
            updated_at=context.updated_at,
            is_active=context.is_active,
            is_verified=context.is_verified,
            full_name=context.full_name,
        )


# Health Check Schemas
class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str
    timestamp: Optional[float] = None
    database: Optional[str] = None
    checks: Optional[Dict[str, str]] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
