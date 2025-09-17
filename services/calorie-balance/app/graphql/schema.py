"""
GraphQL Schema Configuration
Service: calorie-balance
"""

from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.extended_resolvers import (
    ExtendedCalorieMutations,
    ExtendedCalorieQueries,
)
from app.graphql.mutations import Mutation as BaseMutation
from app.graphql.queries import Query as BaseQuery
from app.graphql.types import UcalorieUbalanceType

from .interceptors import GraphQLQueryLoggingExtension


@strawberry.federation.type(extend=True)
class Query(BaseQuery, ExtendedCalorieQueries):
    """Extended Query for Apollo Federation with calorie-balance features."""

    pass


@strawberry.federation.type(extend=True)
class Mutation(BaseMutation, ExtendedCalorieMutations):
    """Extended Mutation for Apollo Federation with calorie features."""

    pass


# Create federated schema with logging extension
schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True,
    extensions=[GraphQLQueryLoggingExtension],
)

# Create GraphQL router
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphiql=True,  # Enable GraphiQL in development
)
