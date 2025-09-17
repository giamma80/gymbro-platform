"""
GraphQL module for calorie-balance
"""

from .extended_resolvers import ExtendedCalorieMutations, ExtendedCalorieQueries
from .extended_types import (
    CalorieEventType,
    CalorieGoalType,
    CreateCalorieEventInput,
    CreateCalorieGoalInput,
    DailyBalanceType,
    MetabolicCalculationInput,
    MetabolicProfileType,
    UpdateCalorieGoalInput,
)
from .mutations import Mutation
from .queries import Query
from .schema import graphql_router, schema
from .types import (
    CreateUcalorieUbalanceInput,
    UcalorieUbalanceType,
    UpdateUcalorieUbalanceInput,
)

__all__ = [
    "schema",
    "graphql_router",
    "UcalorieUbalanceType",
    "CreateUcalorieUbalanceInput",
    "UpdateUcalorieUbalanceInput",
    "Query",
    "Mutation",
    "CalorieGoalType",
    "CalorieEventType",
    "DailyBalanceType",
    "MetabolicProfileType",
    "CreateCalorieGoalInput",
    "UpdateCalorieGoalInput",
    "CreateCalorieEventInput",
    "MetabolicCalculationInput",
    "ExtendedCalorieQueries",
    "ExtendedCalorieMutations",
]
