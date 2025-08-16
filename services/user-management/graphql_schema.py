"""
GraphQL schema with Strawberry and Apollo Federation support
for User Management Service - Working Version
"""

from enum import Enum
from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

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


@strawberry.type
class Query:
    """GraphQL Query root"""

    @strawberry.field
    def hello(self) -> str:
        """Test query - Strawberry GraphQL is working!"""
        return (
            "🎉 Hello from User Management GraphQL with Strawberry! "
            "The module import is WORKING!"
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


@strawberry.type
class Mutation:
    """GraphQL Mutation root"""

    @strawberry.field
    def test_mutation(self) -> str:
        """Test mutation"""
        return (
            "🚀 Mutation working with Strawberry GraphQL! "
            "Federation Step 1 SUCCESSFUL!"
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema, graphiql=True, path="/graphql")
