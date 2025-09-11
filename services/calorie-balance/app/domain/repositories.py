"""
Domain Repositories - Calorie Balance Service

Abstract repository interfaces for the event-driven calorie tracking domain.
These define the contracts that infrastructure implementations must fulfill.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from datetime import date as DateType
from decimal import Decimal

# Import domain entities
from app.domain.entities import (
    User, CalorieEvent, CalorieGoal, DailyBalance, MetabolicProfile,
    HourlyCalorieSummary, DailyCalorieSummary, WeeklyCalorieSummary,
    MonthlyCalorieSummary, DailyBalanceSummary, EventType
)


# =============================================================================
# CORE REPOSITORIES - Event-Driven Architecture
# =============================================================================

class IUserRepository(ABC):
    """Repository for user metabolic profiles."""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create new user profile."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> Optional[User]:
        """Update existing user profile."""
        pass
    
    @abstractmethod
    async def update_metabolic_rates(
        self, user_id: str, bmr: Decimal, tdee: Decimal
    ) -> bool:
        """Update cached BMR/TDEE values."""
        pass


class ICalorieEventRepository(ABC):
    """🔥 HIGH-FREQUENCY REPOSITORY - Core of event-driven architecture."""
    
    @abstractmethod
    async def create(self, event: CalorieEvent) -> CalorieEvent:
        """Create new calorie event - optimized for high frequency."""
        pass
    
    @abstractmethod
    async def create_batch(
        self, events: List[CalorieEvent]
    ) -> List[CalorieEvent]:
        """Batch create events for mobile sync optimization."""
        pass
    
    @abstractmethod
    async def get_events_by_user(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        limit: int = 1000
    ) -> List[CalorieEvent]:
        """Get user events with temporal and type filtering."""
        pass
    
    @abstractmethod
    async def get_recent_events(
        self, user_id: str, limit: int = 100
    ) -> List[CalorieEvent]:
        """Get most recent events for timeline display."""
        pass
    
    @abstractmethod
    async def get_events_by_date_range(
        self,
        user_id: str,
        start_date: DateType,
        end_date: DateType
    ) -> List[CalorieEvent]:
        """Get events for date range analysis."""
        pass
    
    @abstractmethod
    async def update(self, event: CalorieEvent) -> Optional[CalorieEvent]:
        """Update event (rare operation in event-driven system)."""
        pass
    
    @abstractmethod
    async def delete(self, event_id: UUID) -> bool:
        """Delete event (rare operation, prefer soft delete)."""
        pass


class ICalorieGoalRepository(ABC):
    """Repository for dynamic calorie goals."""
    
    @abstractmethod
    async def get_active_goal(self, user_id: str) -> Optional[CalorieGoal]:
        """Get user's currently active goal."""
        pass
    
    @abstractmethod
    async def get_user_goals(
        self, user_id: str, include_inactive: bool = False
    ) -> List[CalorieGoal]:
        """Get all user goals with optional inactive inclusion."""
        pass
    
    @abstractmethod
    async def create(self, goal: CalorieGoal) -> CalorieGoal:
        """Create new goal (auto-deactivates conflicting goals)."""
        pass
    
    @abstractmethod
    async def update(self, goal: CalorieGoal) -> Optional[CalorieGoal]:
        """Update existing goal."""
        pass
    
    @abstractmethod
    async def deactivate_goal(self, goal_id: UUID) -> bool:
        """Deactivate goal (soft deletion)."""
        pass


class IDailyBalanceRepository(ABC):
    """Repository for aggregated daily balances."""
    
    @abstractmethod
    async def get_by_user_date(
        self, user_id: str, date: DateType
    ) -> Optional[DailyBalance]:
        """Get daily balance for specific date."""
        pass
    
    @abstractmethod
    async def get_date_range(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[DailyBalance]:
        """Get daily balances for date range."""
        pass
    
    @abstractmethod
    async def upsert(self, balance: DailyBalance) -> DailyBalance:
        """Create or update daily balance (upsert for aggregation)."""
        pass
    
    @abstractmethod
    async def recalculate_balance(
        self, user_id: str, date: DateType
    ) -> DailyBalance:
        """Recalculate balance from events (data consistency)."""
        pass


class IMetabolicProfileRepository(ABC):
    """Repository for metabolic calculations."""
    
    @abstractmethod
    async def get_latest(self, user_id: str) -> Optional[MetabolicProfile]:
        """Get user's latest metabolic profile."""
        pass
    
    @abstractmethod
    async def get_history(
        self, user_id: str, limit: int = 10
    ) -> List[MetabolicProfile]:
        """Get metabolic profile history."""
        pass
    
    @abstractmethod
    async def create(self, profile: MetabolicProfile) -> MetabolicProfile:
        """Create new metabolic profile."""
        pass


# =============================================================================
# ANALYTICS REPOSITORIES - Temporal Views Access
# =============================================================================

class ITemporalAnalyticsRepository(ABC):
    """Repository for temporal analytics views (5-level aggregation)."""
    
    # Hourly aggregation
    @abstractmethod
    async def get_hourly_summary(
        self, user_id: str, date: DateType
    ) -> List[HourlyCalorieSummary]:
        """Get hourly calorie summary for a specific date."""
        pass
    
    # Daily aggregation
    @abstractmethod
    async def get_daily_summary(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[DailyCalorieSummary]:
        """Get daily summaries for date range."""
        pass
    
    # Weekly aggregation
    @abstractmethod
    async def get_weekly_summary(
        self, user_id: str, year: int, week_number: Optional[int] = None
    ) -> List[WeeklyCalorieSummary]:
        """Get weekly summaries for year (optional specific week)."""
        pass
    
    # Monthly aggregation
    @abstractmethod
    async def get_monthly_summary(
        self, user_id: str, year: int, month: Optional[int] = None
    ) -> List[MonthlyCalorieSummary]:
        """Get monthly summaries for year (optional specific month)."""
        pass
    
    # Daily balance with goals comparison
    @abstractmethod
    async def get_balance_summary(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[DailyBalanceSummary]:
        """Get daily balance with goal comparison."""
        pass


# =============================================================================
# SEARCH AND FILTERING REPOSITORY
# =============================================================================

class ICalorieSearchRepository(ABC):
    """Repository for complex search and filtering operations."""
    
    @abstractmethod
    async def search_events(
        self,
        user_id: str,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Complex event search with pagination."""
        pass
    
    @abstractmethod
    async def get_statistics(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        pass
    
    @abstractmethod
    async def get_trends(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get user trends analysis."""
        pass
# class IAnotherRepository(ABC):
#     pass
