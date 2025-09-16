"""
GraphQL Schema Configuration
Service: calorie-balance
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional

from app.graphql.queries import Query as BaseQuery
from app.graphql.mutations import Mutation as BaseMutation
from app.graphql.types import UcalorieUbalanceType
from app.graphql.extended_resolvers import (
    ExtendedCalorieQueries, ExtendedCalorieMutations
)


@strawberry.federation.type(extend=True)
class Query(BaseQuery, ExtendedCalorieQueries):
    """Extended Query for Apollo Federation with calorie-balance features."""
    pass


@strawberry.federation.type(extend=True)
class Mutation(BaseMutation, ExtendedCalorieMutations):
    """Extended Mutation for Apollo Federation with calorie features."""
    pass


# Create federated schema
schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True
)

# Create GraphQL router
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphiql=True,  # Enable GraphiQL in development
)
