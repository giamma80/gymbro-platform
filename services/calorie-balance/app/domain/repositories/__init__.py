from typing import List, Optional
from uuid import UUID
from datetime import date as date_type
from decimal import Decimal

from ..entities import User, CalorieGoal, DailyBalance, MetabolicProfile, GoalType
from ...core.interfaces import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository interface for User entity"""
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user ID"""
        pass
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass


class CalorieGoalRepository(BaseRepository[CalorieGoal]):
    """Repository interface for CalorieGoal entity"""
    
    async def get_active_goal_by_user(self, user_id: str) -> Optional[CalorieGoal]:
        """Get active calorie goal for user"""
        pass
    
    async def get_goals_by_user(self, user_id: str, include_inactive: bool = False) -> List[CalorieGoal]:
        """Get all goals for user"""
        pass
    
    async def deactivate_user_goals(self, user_id: str) -> None:
        """Deactivate all goals for user"""
        pass


class DailyBalanceRepository(BaseRepository[DailyBalance]):
    """Repository interface for DailyBalance entity"""
    
    async def get_by_user_and_date(self, user_id: str, date: date_type) -> Optional[DailyBalance]:
        """Get daily balance for specific user and date"""
        pass
    
    async def get_range_by_user(
        self, 
        user_id: str, 
        start_date: date_type, 
        end_date: date_type
    ) -> List[DailyBalance]:
        """Get daily balances for user within date range"""
        pass
    
    async def get_latest_by_user(self, user_id: str, limit: int = 30) -> List[DailyBalance]:
        """Get latest daily balances for user"""
        pass


class MetabolicProfileRepository(BaseRepository[MetabolicProfile]):
    """Repository interface for MetabolicProfile entity"""
    
    async def get_current_by_user(self, user_id: str) -> Optional[MetabolicProfile]:
        """Get current valid metabolic profile for user"""
        pass
    
    async def get_latest_by_user(self, user_id: str) -> Optional[MetabolicProfile]:
        """Get latest metabolic profile for user (even if expired)"""
        pass
    
    async def delete_expired_profiles(self) -> int:
        """Delete expired metabolic profiles"""
        pass
