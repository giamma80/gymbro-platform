# Application layer exports
from .commands import (
    CreateUserCommand,
    UpdateUserProfileCommand,
    CreateCalorieGoalCommand,
    UpdateDailyBalanceCommand,
    UserCommandHandler,
    CalorieGoalCommandHandler,
    DailyBalanceCommandHandler
)

from .queries import (
    GetUserQuery,
    GetCalorieGoalQuery,
    GetDailyBalanceQuery,
    GetProgressQuery,
    GetMetabolicProfileQuery,
    UserQueryHandler,
    CalorieGoalQueryHandler,
    DailyBalanceQueryHandler,
    ProgressQueryHandler,
    MetabolicProfileQueryHandler
)

from .services import (
    MetabolicProfileService,
    AnalyticsService,
    RecommendationService
)

__all__ = [
    # Commands
    "CreateUserCommand",
    "UpdateUserProfileCommand", 
    "CreateCalorieGoalCommand",
    "UpdateDailyBalanceCommand",
    "UserCommandHandler",
    "CalorieGoalCommandHandler",
    "DailyBalanceCommandHandler",
    
    # Queries
    "GetUserQuery",
    "GetUserBySupabaseIdQuery",
    "GetCalorieGoalQuery", 
    "GetDailyBalanceQuery",
    "GetProgressQuery",
    "GetMetabolicProfileQuery",
    "UserQueryHandler",
    "CalorieGoalQueryHandler",
    "DailyBalanceQueryHandler",
    "ProgressQueryHandler",
    "MetabolicProfileQueryHandler",
    
    # Services
    "MetabolicProfileService",
    "AnalyticsService",
    "RecommendationService"
]
