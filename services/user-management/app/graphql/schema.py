"""
GraphQL Schema Configuration for user-management
"""

import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.mutations import Mutation
from app.graphql.queries import Query


@strawberry.federation.type(extend=True)
class Query(Query):
    """Extended Query for Apollo Federation."""

    pass


@strawberry.federation.type(extend=True)
class Mutation(Mutation):
    """Extended Mutation for Apollo Federation."""

    pass


# Create federated schema
schema = strawberry.federation.Schema(
    query=Query, mutation=Mutation, enable_federation_2=True
)

# Create GraphQL router
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphiql=True,  # Enable GraphiQL in development
)
