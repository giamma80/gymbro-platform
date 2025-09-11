"""
GraphQL module for user-management
"""

from .mutations import Mutation
from .queries import Query
from .schema import graphql_router, schema
from .types import CreateUserInput, UpdateUserInput, UserType

__all__ = [
    "schema",
    "graphql_router",
    "UserType",
    "CreateUserInput",
    "UpdateUserInput",
    "Query",
    "Mutation",
]
