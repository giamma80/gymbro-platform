"""
GraphQL module for calorie-balance
"""

from .schema import schema, graphql_router
from .types import (
    UcalorieUbalanceType, CreateUcalorieUbalanceInput,
    UpdateUcalorieUbalanceInput
)
from .queries import Query
from .mutations import Mutation
from .extended_types import (
    CalorieGoalType, CalorieEventType, DailyBalanceType,
    MetabolicProfileType, CreateCalorieGoalInput, UpdateCalorieGoalInput,
    CreateCalorieEventInput, MetabolicCalculationInput
)
from .extended_resolvers import (
    ExtendedCalorieQueries, ExtendedCalorieMutations
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
    "ExtendedCalorieMutations"
]
