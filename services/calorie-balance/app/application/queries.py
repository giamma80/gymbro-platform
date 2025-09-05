from typing import List, Optional, Dict, Any
from datetime import date as date_type, datetime, timedelta
from decimal import Decimal

from ..domain import (
    User, CalorieGoal, DailyBalance, MetabolicProfile,
    UserRepository, CalorieGoalRepository, DailyBalanceRepository, MetabolicProfileRepository,
    CalorieCalculationService
)


class GetUserQuery:
    """Query to get user by ID"""
    def __init__(self, user_id: str):
        self.user_id = user_id


class GetCalorieGoalQuery:
    """Query to get active calorie goal for user"""
    def __init__(self, user_id: str):
        self.user_id = user_id


class GetDailyBalanceQuery:
    """Query to get daily balance for specific date"""
    def __init__(self, user_id: str, date: date_type):
        self.user_id = user_id
        self.date = date


class GetProgressQuery:
    """Query to get progress data for date range"""
    def __init__(
        self, 
        user_id: str, 
        start_date: date_type, 
        end_date: date_type
    ):
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date


class GetMetabolicProfileQuery:
    """Query to get current metabolic profile"""
    def __init__(self, user_id: str):
        self.user_id = user_id


class UserQueryHandler:
    """Query handler for user-related operations"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def handle_get_user(self, query: GetUserQuery) -> Optional[User]:
        """Handle get user query"""
        return await self.user_repo.get_by_id(query.user_id)


class CalorieGoalQueryHandler:
    """Query handler for calorie goal operations"""
    
    def __init__(self, goal_repo: CalorieGoalRepository):
        self.goal_repo = goal_repo
    
    async def handle_get_goal(self, query: GetCalorieGoalQuery) -> Optional[CalorieGoal]:
        """Handle get active calorie goal query"""
        return await self.goal_repo.get_active_goal_by_user(query.user_id)


class DailyBalanceQueryHandler:
    """Query handler for daily balance operations"""
    
    def __init__(self, balance_repo: DailyBalanceRepository):
        self.balance_repo = balance_repo
    
    async def handle_get_balance(self, query: GetDailyBalanceQuery) -> Optional[DailyBalance]:
        """Handle get daily balance query"""
        return await self.balance_repo.get_by_user_and_date(
            query.user_id, 
            query.date
        )


class ProgressQueryHandler:
    """Query handler for progress analytics"""
    
    def __init__(
        self,
        balance_repo: DailyBalanceRepository,
        goal_repo: CalorieGoalRepository,
        calorie_service: CalorieCalculationService
    ):
        self.balance_repo = balance_repo
        self.goal_repo = goal_repo
        self.calorie_service = calorie_service
    
    async def handle_get_progress(self, query: GetProgressQuery) -> Dict[str, Any]:
        """Handle get progress data query"""
        # Get daily balances for the period
        balances = await self.balance_repo.get_range_by_user(
            query.user_id,
            query.start_date,
            query.end_date
        )
        
        # Get active goal
        goal = await self.goal_repo.get_active_goal_by_user(query.user_id)
        
        if not goal:
            return {
                "error": "No active calorie goal found",
                "balances": []
            }
        
        # Calculate progress metrics
        metrics = self.calorie_service.calculate_progress_metrics(balances, goal)
        
        return {
            "goal": goal,
            "balances": balances,
            "metrics": metrics,
            "period": {
                "start_date": query.start_date,
                "end_date": query.end_date,
                "days": (query.end_date - query.start_date).days + 1
            }
        }


class MetabolicProfileQueryHandler:
    """Query handler for metabolic profile operations"""
    
    def __init__(self, profile_repo: MetabolicProfileRepository):
        self.profile_repo = profile_repo
    
    async def handle_get_profile(self, query: GetMetabolicProfileQuery) -> Optional[MetabolicProfile]:
        """Handle get metabolic profile query"""
        return await self.profile_repo.get_current_by_user(query.user_id)
