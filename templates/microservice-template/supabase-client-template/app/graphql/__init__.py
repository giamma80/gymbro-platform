"""
GraphQL module for {service-name}
"""

from .schema import schema, graphql_router
from .types import {ServiceName}Type, Create{ServiceName}Input, Update{ServiceName}Input
from .queries import Query
from .mutations import Mutation

__all__ = [
    "schema",
    "graphql_router", 
    "{ServiceName}Type",
    "Create{ServiceName}Input",
    "Update{ServiceName}Input",
    "Query",
    "Mutation"
]
