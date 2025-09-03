"""
GraphQL schema for Analytics Service with Strawberry
Provides analytics data for user dashboards and insights
"""

from typing import List, Optional
from datetime import date
import strawberry


@strawberry.type
class DailyStatsType:
    id: str
    user_id: str
    date_recorded: date
    calories_burned: float
    calories_consumed: float
    steps: int
    active_minutes: int
    sleep_hours: float
    water_liters: float
    weight_kg: Optional[float] = None


@strawberry.type
class TimeRangeStatsType:
    start_date: date
    end_date: date
    total_calories_burned: float
    total_calories_consumed: float
    avg_calories_burned: float
    avg_calories_consumed: float
    total_steps: int
    avg_steps: float
    total_active_minutes: int
    avg_active_minutes: float
    avg_sleep_hours: float
    avg_water_liters: float
    weight_change_kg: Optional[float] = None


@strawberry.type
class UserDashboardType:
    user_id: str
    current_stats: Optional[DailyStatsType] = None
    weekly_stats: Optional[TimeRangeStatsType] = None
    monthly_stats: Optional[TimeRangeStatsType] = None
    recent_activities: List[DailyStatsType]


@strawberry.input
class DashboardFiltersInput:
    user_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_weight_data: Optional[bool] = True


# Query and Mutation resolvers
@strawberry.type
class Query:
    @strawberry.field
    async def get_user_dashboard(
        self, filters: DashboardFiltersInput
    ) -> Optional[UserDashboardType]:
        """Get user dashboard with analytics data"""
        # Mock implementation - replace with actual data fetching
        return UserDashboardType(
            user_id=filters.user_id,
            current_stats=None,
            weekly_stats=None,
            monthly_stats=None,
            recent_activities=[]
        )
    
    @strawberry.field
    async def get_daily_stats(
        self, user_id: str, date_filter: Optional[date] = None
    ) -> List[DailyStatsType]:
        """Get daily statistics for a user"""
        # Mock implementation - replace with actual data fetching
        return []

    @strawberry.field
    async def get_time_range_stats(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Optional[TimeRangeStatsType]:
        """Get statistics for a specific time range"""
        # Mock implementation - replace with actual data fetching
        return None


@strawberry.type
class Mutation:
    @strawberry.field
    async def update_daily_stats(
        self, user_id: str, date_recorded: date
    ) -> bool:
        """Update daily statistics for a user"""
        # Mock implementation - replace with actual data update
        return True


# Schema definition
schema = strawberry.Schema(query=Query, mutation=Mutation)
