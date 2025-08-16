"""
GraphQL schema with Strawberry and Apollo Federation support
for User Management Service - Apollo Federation Compatible
"""

from enum import Enum
from typing import List, Optional

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

# GraphQL Enums - Correct approach
# =====================================


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
        """Test query - Strawberry GraphQL is working!"""
        return (
            "🎉 Hello from User Management GraphQL with Strawberry! "
            "Apollo Federation _service field enabled!"
        )

    @strawberry.field
    def test_enums(self) -> str:
        """Test enum usage"""
        role = UserRoleType.USER
        gender = GenderType.MALE
        activity = ActivityLevelType.MODERATELY_ACTIVE
        return f"✅ Enums working: {role.value}, {gender.value}, {activity.value}"

    @strawberry.field
    def user_count(self) -> int:
        """Get total user count"""
        try:
            # Per ora restituisce un valore mock per testare GraphQL
            # TODO: Implementare connessione database appropriata in GraphQL context
            return 42
        except Exception:
            return 0

    @strawberry.field(name="_service")
    def service_field(self) -> ServiceDefinition:
        """Apollo Federation service definition - Required by Gateway"""
        # Minimal SDL for User Management service
        sdl = """
            extend type Query {
                hello: String
                test_enums: String
                user_count: Int
            }
        """
        return ServiceDefinition(sdl=sdl)


@strawberry.type
class Mutation:
    """GraphQL Mutation root - Apollo Federation compatible"""

    @strawberry.field
    def test_mutation(self) -> str:
        """Test mutation"""
        return (
            "🚀 Mutation working with Strawberry GraphQL Federation! "
            "Apollo Gateway integration ready!"
        )


# ✅ CRITICAL: Apollo Federation Schema (with fallback)
# Use build_schema for Apollo Federation support if available
if FEDERATION_AVAILABLE:
    schema = build_schema(query=Query, mutation=Mutation)
    print("✅ Apollo Federation schema enabled")
else:
    schema = build_schema(query=Query, mutation=Mutation)
    print("⚠️ Using regular GraphQL schema (no federation)")

graphql_router = GraphQLRouter(schema, graphiql=True, path="/graphql")
