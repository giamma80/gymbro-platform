"""
GraphQL schema with Strawberry and Apollo Federation support
for User Management Service - Apollo Federation Compatible
"""


from enum import Enum
from typing import List, Optional
import datetime

import strawberry
from strawberry.fastapi import GraphQLRouter

# Try to import federation support, fall back to regular schema if not available
try:
    from strawberry.federation import build_schema
    FEDERATION_AVAILABLE = True
except ImportError:
    from strawberry import Schema as build_schema
    FEDERATION_AVAILABLE = False
    print("⚠️ Strawberry Federation not available, using regular schema")


# Enums
@strawberry.enum
class UserRoleType(Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

@strawberry.enum
class GenderType(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

@strawberry.enum
class ActivityLevelType(Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

# Types
@strawberry.type
class UserProfile:
    id: str
    email: str
    first_name: str
    last_name: str
    age: int
    gender: GenderType
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelType
    role: UserRoleType
    is_premium: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

@strawberry.type
class UserStats:
    total_calories_burned: float
    total_calories_consumed: float
    days_active: int
    current_streak: int
    weight_change_kg: float
    bmi: float

@strawberry.type
class UserPreferences:
    timezone: str
    language: str
    push_notifications: bool
    email_notifications: bool
    meal_reminders: bool
    workout_reminders: bool
    profile_public: bool
    share_achievements: bool
    weight_unit: str
    distance_unit: str

@strawberry.type
class UserListResponse:
    users: List[UserProfile]
    total: int
    page: int
    limit: int
    total_pages: int

@strawberry.type
class TokenResponse:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserProfile

# Input Types
@strawberry.input
class UserRegistrationInput:
    email: str
    password: str
    first_name: str
    last_name: str
    date_of_birth: datetime.datetime
    gender: GenderType
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelType

@strawberry.input
class UserLoginInput:
    email: str
    password: str

@strawberry.input
class UserProfileUpdateInput:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevelType] = None

@strawberry.input
class PasswordChangeInput:
    current_password: str
    new_password: str

@strawberry.input
class UserPreferencesInput:
    timezone: Optional[str] = None
    language: Optional[str] = None
    push_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    meal_reminders: Optional[bool] = None
    workout_reminders: Optional[bool] = None
    profile_public: Optional[bool] = None
    share_achievements: Optional[bool] = None
    weight_unit: Optional[str] = None
    distance_unit: Optional[str] = None


# GraphQL Schema Setup
# =====================================


# GraphQL Types for Federation
# =====================================

@strawberry.type
class ServiceDefinition:
    """Apollo Federation service definition"""
    sdl: str



@strawberry.type
class Query:
    """GraphQL Query root - Apollo Federation compatible"""

    @strawberry.field
    def hello(self) -> str:
        return (
            "🎉 Hello from User Management GraphQL with Strawberry! "
            "Apollo Federation _service field enabled!"
        )

    @strawberry.field
    def test_enums(self) -> str:
        role = UserRoleType.USER
        gender = GenderType.MALE
        activity = ActivityLevelType.MODERATELY_ACTIVE
        return f"✅ Enums working: {role.value}, {gender.value}, {activity.value}"

    @strawberry.field
    def user_count(self) -> int:
        return 42

    # --- REAL QUERIES ---
    @strawberry.field
    def me(self) -> UserProfile:
        # TODO: Recupera utente autenticato dal context
        return UserProfile(
            id="1",
            email="demo@example.com",
            first_name="Demo",
            last_name="User",
            age=30,
            gender=GenderType.MALE,
            height_cm=180.0,
            weight_kg=75.0,
            activity_level=ActivityLevelType.MODERATELY_ACTIVE,
            role=UserRoleType.USER,
            is_premium=False,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )

    @strawberry.field
    def user_profile(self, user_id: str) -> UserProfile:
        # TODO: Recupera profilo utente dal database
        return self.me()

    @strawberry.field
    def users(self, page: int = 1, limit: int = 20) -> UserListResponse:
        # TODO: Query reale dal database
        return UserListResponse(
            users=[self.me()],
            total=1,
            page=page,
            limit=limit,
            total_pages=1,
        )

    @strawberry.field
    def user_stats(self, user_id: str) -> UserStats:
        # TODO: Query reale dal database
        return UserStats(
            total_calories_burned=1000.0,
            total_calories_consumed=2000.0,
            days_active=10,
            current_streak=3,
            weight_change_kg=-1.5,
            bmi=22.5,
        )

    @strawberry.field
    def user_preferences(self, user_id: str) -> UserPreferences:
        # TODO: Query reale dal database
        return UserPreferences(
            timezone="Europe/Rome",
            language="it",
            push_notifications=True,
            email_notifications=True,
            meal_reminders=True,
            workout_reminders=True,
            profile_public=False,
            share_achievements=True,
            weight_unit="kg",
            distance_unit="km",
        )

    @strawberry.field(name="_service")
    def service_field(self) -> ServiceDefinition:
        sdl = """
            extend type Query {
                hello: String
                testEnums: String
                userCount: Int
                me: UserProfile
                userProfile(userId: String!): UserProfile
                users(page: Int, limit: Int): UserListResponse
                userStats(userId: String!): UserStats
                userPreferences(userId: String!): UserPreferences
            }

            type UserProfile {
                id: String!
                email: String!
                firstName: String!
                lastName: String!
                age: Int!
                gender: GenderType!
                heightCm: Float!
                weightKg: Float!
                activityLevel: ActivityLevelType!
                role: UserRoleType!
                isPremium: Boolean!
                createdAt: DateTime!
                updatedAt: DateTime!
            }

            type UserStats {
                totalCaloriesBurned: Float!
                totalCaloriesConsumed: Float!
                daysActive: Int!
                currentStreak: Int!
                weightChangeKg: Float!
                bmi: Float!
            }

            type UserPreferences {
                timezone: String!
                language: String!
                pushNotifications: Boolean!
                emailNotifications: Boolean!
                mealReminders: Boolean!
                workoutReminders: Boolean!
                profilePublic: Boolean!
                shareAchievements: Boolean!
                weightUnit: String!
                distanceUnit: String!
            }

            type UserListResponse {
                users: [UserProfile!]!
                total: Int!
                page: Int!
                limit: Int!
                totalPages: Int!
            }

            type TokenResponse {
                accessToken: String!
                refreshToken: String!
                tokenType: String!
                expiresIn: Int!
                user: UserProfile!
            }

            input UserRegistrationInput {
                email: String!
                password: String!
                firstName: String!
                lastName: String!
                dateOfBirth: DateTime!
                gender: GenderType!
                heightCm: Float!
                weightKg: Float!
                activityLevel: ActivityLevelType!
            }

            input UserLoginInput {
                email: String!
                password: String!
            }

            input UserProfileUpdateInput {
                firstName: String
                lastName: String
                heightCm: Float
                weightKg: Float
                activityLevel: ActivityLevelType
            }

            input PasswordChangeInput {
                currentPassword: String!
                newPassword: String!
            }

            input UserPreferencesInput {
                timezone: String
                language: String
                pushNotifications: Boolean
                emailNotifications: Boolean
                mealReminders: Boolean
                workoutReminders: Boolean
                profilePublic: Boolean
                shareAchievements: Boolean
                weightUnit: String
                distanceUnit: String
            }

            enum GenderType {
                MALE
                FEMALE
                OTHER
            }

            enum UserRoleType {
                USER
                PREMIUM
                ADMIN
            }

            enum ActivityLevelType {
                SEDENTARY
                LIGHTLY_ACTIVE
                MODERATELY_ACTIVE
                VERY_ACTIVE
                EXTREMELY_ACTIVE
            }
        """
        return ServiceDefinition(sdl=sdl)



@strawberry.type
class Mutation:
    """GraphQL Mutation root - Apollo Federation compatible"""

    @strawberry.field
    def test_mutation(self) -> str:
        return (
            "🚀 Mutation working with Strawberry GraphQL Federation! "
            "Apollo Gateway integration ready!"
        )

    @strawberry.field
    def register_user(self, input: UserRegistrationInput) -> TokenResponse:
        # TODO: Implementa logica reale
        return TokenResponse(
            access_token="mock-token",
            refresh_token="mock-refresh",
            token_type="bearer",
            expires_in=3600,
            user=Query().me(),
        )

    @strawberry.field
    def login_user(self, input: UserLoginInput) -> TokenResponse:
        # TODO: Implementa logica reale
        return self.register_user(UserRegistrationInput(
            email=input.email,
            password=input.password,
            first_name="Demo",
            last_name="User",
            date_of_birth=datetime.datetime(1990,1,1),
            gender=GenderType.MALE,
            height_cm=180.0,
            weight_kg=75.0,
            activity_level=ActivityLevelType.MODERATELY_ACTIVE,
        ))

    @strawberry.field
    def update_user_profile(self, input: UserProfileUpdateInput) -> UserProfile:
        # TODO: Implementa logica reale
        return Query().me()

    @strawberry.field
    def change_password(self, input: PasswordChangeInput) -> bool:
        # TODO: Implementa logica reale
        return True

    @strawberry.field
    def update_user_preferences(self, input: UserPreferencesInput) -> UserPreferences:
        # TODO: Implementa logica reale
        return Query().user_preferences(user_id="1")


# ✅ CRITICAL: Apollo Federation Schema (with fallback)
# Use build_schema for Apollo Federation support if available
if FEDERATION_AVAILABLE:
    schema = build_schema(query=Query, mutation=Mutation)
    print("✅ Apollo Federation schema enabled")
else:
    schema = build_schema(query=Query, mutation=Mutation)
    print("⚠️ Using regular GraphQL schema (no federation)")

graphql_router = GraphQLRouter(schema, graphiql=True, path="/graphql")
