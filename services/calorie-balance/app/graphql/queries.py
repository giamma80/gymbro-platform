"""
GraphQL Queries for calorie-balance
"""

import strawberry
from typing import List, Optional
from app.graphql.types import UcalorieUbalanceType, UcalorieUbalanceListResponse
from app.core.database import SupabaseRepository
import logging

logger = logging.getLogger(__name__)


@strawberry.type
class CalorieGoalType:
    """GraphQL type for calorie goal."""
    id: strawberry.ID
    user_id: str
    goal_type: str  # Normalized to lowercase for GraphQL responses
    daily_calorie_target: float
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None


@strawberry.type
class CalorieGoalListResponse:
    """Response wrapper for calorie goal list."""
    success: bool
    message: str
    data: List[CalorieGoalType]
    total: int


@strawberry.type
class CalorieEventType:
    """GraphQL type for calorie event."""
    id: strawberry.ID
    user_id: str
    event_type: str  # Normalized to lowercase for GraphQL responses
    value: float
    source: str
    event_timestamp: str
    created_at: str


@strawberry.type
class CalorieEventListResponse:
    """Response wrapper for calorie event list."""
    success: bool
    message: str
    data: List[CalorieEventType]
    total: int


@strawberry.type
class DailyBalanceType:
    """GraphQL type for daily balance."""
    id: strawberry.ID
    user_id: str
    date: str
    calories_consumed: float
    calories_burned_exercise: float
    calories_burned_bmr: float
    net_calories: float
    daily_calorie_target: Optional[float] = None
    created_at: str
    updated_at: Optional[str] = None


@strawberry.type
class DailyBalanceListResponse:
    """Response wrapper for daily balance list."""
    success: bool
    message: str
    data: List[DailyBalanceType]
    total: int


@strawberry.type
class DailyBalanceResponse:
    """Response wrapper for single daily balance."""
    success: bool
    message: str
    data: Optional[DailyBalanceType] = None


@strawberry.type
class MetabolicProfileType:
    """GraphQL type for metabolic profile."""
    id: strawberry.ID
    user_id: str
    bmr_calories: float
    tdee_calories: float
    activity_level: str
    is_ai_adjusted: bool
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None


@strawberry.type
class MetabolicProfileResponse:
    """Response wrapper for metabolic profile."""
    success: bool
    message: str
    data: Optional[MetabolicProfileType] = None


@strawberry.type
class Query:
    """GraphQL queries for calorie-balance."""
    
    @strawberry.field
    async def get_calorie_balance(
        self, id: strawberry.ID
    ) -> Optional[UcalorieUbalanceType]:
        """Get a single calorie-balance by ID."""
        # Initialize repository
        repo = SupabaseRepository("calorie_balance")
        
        # Fetch data from Supabase
        data = await repo.get_by_id(str(id))
        
        if not data:
            return None
            
        return UcalorieUbalanceType(
            id=strawberry.ID(data["id"]),
            name=data["name"],
            description=data.get("description"),
            created_at=data["created_at"],
            updated_at=data.get("updated_at")
        )
    
    @strawberry.field
    async def list_calorie_balances(
        self,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> UcalorieUbalanceListResponse:
        """List calorie-balances with pagination."""
        try:
            # Initialize repository
            repo = SupabaseRepository("calorie_balance")
            
            # Fetch data from Supabase
            data = await repo.get_all(limit=limit, offset=offset)
            
            # Convert to GraphQL types
            items = [
                UcalorieUbalanceType(
                    id=strawberry.ID(item["id"]),
                    name=item["name"],
                    description=item.get("description"),
                    created_at=item["created_at"],
                    updated_at=item.get("updated_at")
                )
                for item in data
            ]
            
            return UcalorieUbalanceListResponse(
                success=True,
                message="Successfully retrieved calorie_balances",
                data=items,
                total=len(items)
            )
            
        except Exception as e:
            return UcalorieUbalanceListResponse(
                success=False,
                message=f"Error retrieving calorie_balances: {str(e)}",
                data=[],
                total=0
            )
    
    @strawberry.field
    async def get_user_calorie_goals(
        self,
        user_id: str,
        is_active: Optional[bool] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> CalorieGoalListResponse:
        """Get user's calorie goals with filtering."""
        try:
            # Use repository directly
            from app.infrastructure.repositories.repositories import (
                SupabaseCalorieGoalRepository
            )
            
            # Initialize repository
            repository = SupabaseCalorieGoalRepository()
            
            # Get goals directly from repository
            goals = await repository.get_user_goals(
                user_id,
                include_inactive=(is_active is None)
            )
            
            # Convert to GraphQL types with normalized goal_type
            goal_data = []
            for goal in goals:
                # Normalize goal_type to lowercase
                normalized_goal_type = (
                    goal.goal_type.lower() if goal.goal_type else ""
                )
                
                goal_data.append(CalorieGoalType(
                    id=strawberry.ID(str(goal.id)),
                    user_id=user_id,
                    goal_type=normalized_goal_type,  # Normalized to lowercase
                    daily_calorie_target=float(goal.daily_calorie_target),
                    is_active=goal.is_active,
                    created_at=str(goal.created_at),
                    updated_at=(
                        str(goal.updated_at) if goal.updated_at else None
                    )
                ))
            
            return CalorieGoalListResponse(
                success=True,
                message=f"Found {len(goals)} goals",
                data=goal_data,
                total=len(goals)
            )
        except Exception as e:
            logger.error(f"Error in get_user_calorie_goals: {str(e)}")
            return CalorieGoalListResponse(
                success=False,
                message=f"Error fetching goals: {str(e)}",
                data=[],
                total=0
            )
    
    @strawberry.field
    async def get_user_calorie_events(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> CalorieEventListResponse:
        """Get user's calorie events with filtering."""
        try:
            # Use repository directly
            from app.infrastructure.repositories.repositories import (
                SupabaseCalorieEventRepository
            )
            
            # Initialize repository
            repository = SupabaseCalorieEventRepository()
            
            # Convert string dates to datetime if provided
            from datetime import datetime
            start_time = None
            end_time = None
            if start_date:
                start_time = datetime.fromisoformat(start_date)
            if end_date:
                end_time = datetime.fromisoformat(end_date)
            
            # Get events directly from repository
            events = await repository.get_events_by_user(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            # Convert to GraphQL types with normalized event_type
            event_data = []
            for event in events or []:
                # Normalize event_type to lowercase
                normalized_event_type = (
                    event.event_type.lower() if event.event_type else ""
                )
                
                event_data.append(CalorieEventType(
                    id=strawberry.ID(str(event.id)),
                    user_id=user_id,
                    event_type=normalized_event_type,
                    value=float(event.calories),
                    source=event.source or "",
                    event_timestamp=str(event.event_timestamp),
                    created_at=str(event.created_at)
                ))
            
            total_count = len(event_data)
            
            return CalorieEventListResponse(
                success=True,
                message=f"Found {total_count} events",
                data=event_data,
                total=total_count
            )
            
        except Exception as e:
            logger.error(f"Error in get_user_calorie_events: {str(e)}")
            return CalorieEventListResponse(
                success=False,
                message=f"Error fetching events: {str(e)}",
                data=[],
                total=0
            )
    
    @strawberry.field
    async def get_daily_calorie_events(
        self,
        user_id: str,
        target_date: str
    ) -> CalorieEventListResponse:
        """Get user's calorie events for a specific day."""
        try:
            # Use repository directly
            from app.infrastructure.repositories.repositories import (
                SupabaseCalorieEventRepository
            )
            from datetime import datetime
            
            # Parse target_date
            target_dt = datetime.fromisoformat(target_date).date()
            start_time = datetime.combine(target_dt, datetime.min.time())
            end_time = datetime.combine(target_dt, datetime.max.time())
            
            # Initialize repository
            repository = SupabaseCalorieEventRepository()
            
            # Get events for specific day
            events = await repository.get_events_by_user(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Convert to GraphQL types with normalized event_type
            event_data = []
            for event in events or []:
                normalized_event_type = (
                    event.event_type.lower() if event.event_type else ""
                )
                
                event_data.append(CalorieEventType(
                    id=strawberry.ID(str(event.id)),
                    user_id=user_id,
                    event_type=normalized_event_type,
                    value=float(event.calories),
                    source=event.source or "",
                    event_timestamp=str(event.event_timestamp),
                    created_at=str(event.created_at)
                ))
            
            return CalorieEventListResponse(
                success=True,
                message=f"Found {len(event_data)} events for {target_date}",
                data=event_data,
                total=len(event_data)
            )
            
        except Exception as e:
            logger.error(f"Error in get_daily_calorie_events: {str(e)}")
            return CalorieEventListResponse(
                success=False,
                message=f"Error fetching daily events: {str(e)}",
                data=[],
                total=0
            )
    
    @strawberry.field
    async def get_user_daily_balances(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = 30,
        offset: Optional[int] = 0
    ) -> DailyBalanceListResponse:
        """Get user's daily balances with date filtering."""
        try:
            # Create service instances manually for GraphQL
            from app.infrastructure.repositories.repositories import (
                SupabaseDailyBalanceRepository
            )
            from datetime import datetime, date, timedelta
            
            # Create repository instance
            balance_repo = SupabaseDailyBalanceRepository()
            
            # Parse date filters if provided
            start_dt = None
            end_dt = None
            if start_date:
                start_dt = datetime.fromisoformat(start_date).date()
            if end_date:
                end_dt = datetime.fromisoformat(end_date).date()
            
            # If no date filters provided, use a wide range to get all balances
            if not start_dt and not end_dt:
                # Get balances from 1 year ago to 1 year in the future
                start_dt = date.today() - timedelta(days=365)
                end_dt = date.today() + timedelta(days=365)
            elif start_dt and not end_dt:
                # If only start provided, get 1 year from start
                end_dt = start_dt + timedelta(days=365)
            elif end_dt and not start_dt:
                # If only end provided, get 1 year before end
                start_dt = end_dt - timedelta(days=365)
            
            # Get daily balances with filters
            balances = await balance_repo.get_date_range(
                user_id, start_dt, end_dt
            )
            
            # Convert to GraphQL types
            balance_data = []
            for balance in balances or []:
                balance_data.append(DailyBalanceType(
                    id=strawberry.ID(str(balance.id)),
                    user_id=user_id,
                    date=str(balance.date),
                    calories_consumed=float(balance.calories_consumed or 0),
                    calories_burned_exercise=float(balance.calories_burned_exercise or 0),
                    calories_burned_bmr=float(balance.calories_burned_bmr or 0),
                    net_calories=float(balance.net_calories or 0),
                    daily_calorie_target=float(balance.daily_calorie_target) if balance.daily_calorie_target else 2000.0,  # Default target
                    created_at=str(balance.created_at),
                    updated_at=str(balance.updated_at) if balance.updated_at else None
                ))
            
            return DailyBalanceListResponse(
                success=True,
                message="Daily balances retrieved successfully",
                data=balance_data,
                total=len(balance_data)
            )
            
        except Exception as e:
            logger.error(f"Error in get_user_daily_balances: {str(e)}")
            return DailyBalanceListResponse(
                success=False,
                message=f"Error fetching daily balances: {str(e)}",
                data=[],
                total=0
            )
    
    @strawberry.field
    async def get_current_daily_balance(
        self,
        user_id: str
    ) -> DailyBalanceResponse:
        """Get user's balance for today."""
        try:
            from datetime import date, datetime
            
            # Create a default balance for today with daily target included
            balance_data = DailyBalanceType(
                id=strawberry.ID("current-daily-balance"),
                user_id=user_id,
                date=str(date.today()),
                calories_consumed=0.0,
                calories_burned_exercise=0.0,
                calories_burned_bmr=0.0,
                net_calories=0.0,
                daily_calorie_target=2000.0,  # Include expected daily target
                created_at=str(datetime.now()),
                updated_at=str(datetime.now())
            )
            
            return DailyBalanceResponse(
                success=True,
                message="Current balance retrieved successfully",
                data=balance_data
            )
        except Exception as e:
            return DailyBalanceResponse(
                success=False,
                message=f"Error fetching current balance: {str(e)}",
                data=None
            )
    
    @strawberry.field
    async def get_user_metabolic_profile(
        self,
        user_id: str
    ) -> MetabolicProfileResponse:
        """Get user's current metabolic profile."""
        try:
            # Create service instances manually for GraphQL
            from app.infrastructure.repositories.repositories import (
                SupabaseMetabolicProfileRepository
            )
            
            # Create repository instance
            profile_repo = SupabaseMetabolicProfileRepository()
            
            # Get user's metabolic profile
            profile = await profile_repo.get_latest(user_id)
            
            if profile:
                profile_data = MetabolicProfileType(
                    id=strawberry.ID(str(profile.id)),
                    user_id=user_id,
                    bmr_calories=float(profile.bmr_calories),
                    tdee_calories=float(profile.tdee_calories),
                    activity_level=profile.activity_level or "moderate",
                    is_ai_adjusted=profile.is_ai_adjusted or False,
                    is_active=profile.is_active,
                    created_at=str(profile.created_at),
                    updated_at=str(profile.updated_at) if profile.updated_at else None
                )
                
                return MetabolicProfileResponse(
                    success=True,
                    message="Metabolic profile retrieved successfully",
                    data=profile_data
                )
            else:
                return MetabolicProfileResponse(
                    success=True,
                    message="No metabolic profile found for user",
                    data=None
                )
                
        except Exception as e:
            logger.error(f"Error in get_user_metabolic_profile: {str(e)}")
            return MetabolicProfileResponse(
                success=False,
                message=f"Error fetching metabolic profile: {str(e)}",
                data=None
            )
            items = [
                UcalorieUbalanceType(
                    id=strawberry.ID(item["id"]),
                    name=item["name"],
                    description=item.get("description"),
                    created_at=item["created_at"],
                    updated_at=item.get("updated_at")
                )
                for item in data
            ]
            
            return UcalorieUbalanceListResponse(
                success=True,
                message="Successfully retrieved calorie_balances",
                data=items,
                total=len(items)
            )
            
        except Exception as e:
            return UcalorieUbalanceListResponse(
                success=False,
                message=f"Error retrieving calorie_balances: {str(e)}",
                data=[],
                total=0
            )
