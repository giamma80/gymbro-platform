"""
Domain Layer - User Management
=============================
Service: user-management
Schema: user_management

This module contains the domain entities, value objects, and business logic
for the user management service.
"""

from .entities import (
    GenderType,
    PrivacySettings,
    User,
    UserCreatedEvent,
    UserProfile,
    UserProfileUpdatedEvent,
    UserServiceContext,
    UserStatus,
    UserVerifiedEvent,
)

__all__ = [
    "User",
    "UserProfile",
    "PrivacySettings",
    "UserServiceContext",
    "UserStatus",
    "GenderType",
    "UserCreatedEvent",
    "UserVerifiedEvent",
    "UserProfileUpdatedEvent",
]
