"""
Domain Layer - User Management Entities
=======================================
Service: user-management
Schema: user_management
Phase: 1.0 - Foundation Setup
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
from uuid import UUID


class UserStatus(Enum):
    """User account status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class GenderType(Enum):
    """Gender type enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


@dataclass
class User:
    """Core user entity - represents identity and authentication."""
    
    id: UUID
    email: str
    username: str
    status: UserStatus
    email_verified_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    last_login_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_verified(self) -> bool:
        """Check if user email is verified."""
        return self.email_verified_at is not None
    
    def activate(self):
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate user account."""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()
    
    def suspend(self):
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
    
    def verify_email(self):
        """Mark user email as verified."""
        self.email_verified_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def record_login(self):
        """Record user login timestamp."""
        self.last_login_at = datetime.utcnow()


@dataclass
class UserProfile:
    """Extended user profile entity - represents personal information."""
    
    id: UUID
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderType] = None
    timezone: str = "UTC"
    locale: str = "en-US"
    preferences: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.preferences is None:
            self.preferences = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.display_name or "User"
    
    @property
    def age(self) -> Optional[int]:
        """Calculate user's age from date of birth."""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
            
        return age
    
    def update_preference(self, key: str, value: Any):
        """Update a specific preference."""
        self.preferences[key] = value
        self.updated_at = datetime.utcnow()
    
    def remove_preference(self, key: str):
        """Remove a specific preference."""
        self.preferences.pop(key, None)
        self.updated_at = datetime.utcnow()


@dataclass
class PrivacySettings:
    """Privacy and consent settings entity - GDPR compliance."""
    
    id: UUID
    user_id: UUID
    data_processing_consent: bool = False
    marketing_consent: bool = False
    analytics_consent: bool = False
    profile_visibility: bool = False
    health_data_sharing: bool = False
    preferences: Dict[str, Any] = None
    consent_given_at: Optional[datetime] = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.preferences is None:
            self.preferences = {}
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def has_basic_consent(self) -> bool:
        """Check if user has given basic data processing consent."""
        return self.data_processing_consent
    
    @property
    def consent_level(self) -> str:
        """Get overall consent level."""
        consents = [
            self.data_processing_consent,
            self.marketing_consent,
            self.analytics_consent,
            self.profile_visibility,
            self.health_data_sharing
        ]
        
        given_count = sum(consents)
        
        if given_count == 0:
            return "none"
        elif given_count <= 2:
            return "minimal"
        elif given_count <= 4:
            return "moderate"
        else:
            return "full"
    
    def give_basic_consent(self):
        """Give basic data processing consent."""
        self.data_processing_consent = True
        if not self.consent_given_at:
            self.consent_given_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def revoke_consent(self, consent_type: str):
        """Revoke specific consent type."""
        if hasattr(self, consent_type):
            setattr(self, consent_type, False)
            self.updated_at = datetime.utcnow()
    
    def update_consent(self, consent_type: str, value: bool):
        """Update specific consent setting."""
        if hasattr(self, consent_type):
            setattr(self, consent_type, value)
            if value and not self.consent_given_at:
                self.consent_given_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()


@dataclass
class UserServiceContext:
    """Complete user context for service integration and GraphQL Federation."""
    
    user_id: UUID
    email: str
    username: str
    user_status: UserStatus
    email_verified_at: Optional[datetime]
    display_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    timezone: str
    locale: str
    preferences: Dict[str, Any]
    health_data_sharing: bool
    analytics_consent: bool
    created_at: datetime
    updated_at: datetime
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.user_status == UserStatus.ACTIVE
    
    @property
    def is_verified(self) -> bool:
        """Check if user email is verified."""
        return self.email_verified_at is not None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.display_name or "User"


# Domain Events for event-driven architecture
@dataclass
class UserCreatedEvent:
    """Event fired when a new user is created."""
    user_id: UUID
    email: str
    username: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class UserVerifiedEvent:
    """Event fired when user email is verified."""
    user_id: UUID
    email: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class UserProfileUpdatedEvent:
    """Event fired when user profile is updated."""
    user_id: UUID
    updated_fields: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
