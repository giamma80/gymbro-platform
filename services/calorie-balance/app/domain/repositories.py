"""
Domain Repositories - Calorie Balance Service

Abstract repository interfaces for the event-driven calorie tracking domain.
These define the contracts that infrastructure implementations must fulfill.

Cross-Schema Architecture:
- IUserRepository removed - users managed by user-management service
- All user_id parameters now use UUID type for cross-schema FK consistency
- Focus on calorie events, goals, and metabolic calculations repositories
"""

from abc import ABC, abstractmethod
from datetime import date as DateType
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

# Import domain entities
from app.domain.entities import (
    CalorieEvent,
    CalorieGoal,
    DailyBalance,
    DailyBalanceSummary,
    DailyCalorieSummary,
    EventType,
    HourlyCalorieSummary,
    MetabolicProfile,
    MonthlyCalorieSummary,
    WeeklyCalorieSummary,
)

# =============================================================================
# CORE REPOSITORIES - Event-Driven Architecture
# =============================================================================
# NOTE: User repository not needed - users managed by user-management service


class ICalorieEventRepository(ABC):
    """🔥 HIGH-FREQUENCY REPOSITORY - Core of event-driven architecture."""

    @abstractmethod
    async def create(self, event: CalorieEvent) -> CalorieEvent:
        """Create new calorie event - optimized for high frequency."""
        pass

    @abstractmethod
    async def create_batch(self, events: List[CalorieEvent]) -> List[CalorieEvent]:
        """Batch create events for mobile sync optimization."""
        pass

    @abstractmethod
    async def get_events_by_user(
        self,
        user_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        limit: int = 1000,
    ) -> List[CalorieEvent]:
        """Get user events with temporal and type filtering."""
        pass

    @abstractmethod
    async def get_recent_events(
        self, user_id: UUID, limit: int = 100
    ) -> List[CalorieEvent]:
        """Get most recent events for timeline display."""
        pass

    @abstractmethod
    async def get_events_by_date_range(
        self, user_id: UUID, start_date: DateType, end_date: DateType
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
    async def get_active_goal(self, user_id: UUID) -> Optional[CalorieGoal]:
        """Get user's currently active goal."""
        pass

    @abstractmethod
    async def get_user_goals(
        self, user_id: UUID, include_inactive: bool = False
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
        self, user_id: UUID, date: DateType
    ) -> Optional[DailyBalance]:
        """Get daily balance for specific date."""
        pass

    @abstractmethod
    async def get_date_range(
        self, user_id: UUID, start_date: DateType, end_date: DateType
    ) -> List[DailyBalance]:
        """Get daily balances for date range."""
        pass

    @abstractmethod
    async def upsert(self, balance: DailyBalance) -> DailyBalance:
        """Create or update daily balance (upsert for aggregation)."""
        pass

    @abstractmethod
    async def recalculate_balance(self, user_id: UUID, date: DateType) -> DailyBalance:
        """Recalculate balance from events (data consistency)."""
        pass


class IMetabolicProfileRepository(ABC):
    """Repository for metabolic calculations."""

    @abstractmethod
    async def get_latest(self, user_id: UUID) -> Optional[MetabolicProfile]:
        """Get user's latest metabolic profile."""
        pass

    @abstractmethod
    async def get_history(
        self, user_id: UUID, limit: int = 10
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
        self, user_id: UUID, date: DateType
    ) -> List[HourlyCalorieSummary]:
        """Get hourly calorie summary for a specific date."""
        pass

    # Daily aggregation
    @abstractmethod
    async def get_daily_summary(
        self, user_id: UUID, start_date: DateType, end_date: DateType
    ) -> List[DailyCalorieSummary]:
        """Get daily summaries for date range."""
        pass

    # Weekly aggregation
    @abstractmethod
    async def get_weekly_summary(
        self, user_id: UUID, year: int, week_number: Optional[int] = None
    ) -> List[WeeklyCalorieSummary]:
        """Get weekly summaries for year (optional specific week)."""
        pass

    # Monthly aggregation
    @abstractmethod
    async def get_monthly_summary(
        self, user_id: UUID, year: int, month: Optional[int] = None
    ) -> List[MonthlyCalorieSummary]:
        """Get monthly summaries for year (optional specific month)."""
        pass

    # Daily balance with goals comparison
    @abstractmethod
    async def get_balance_summary(
        self, user_id: UUID, start_date: DateType, end_date: DateType
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
        user_id: UUID,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """Complex event search with pagination."""
        pass

    @abstractmethod
    async def get_statistics(
        self, user_id: UUID, start_date: DateType, end_date: DateType
    ) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        pass

    @abstractmethod
    async def get_trends(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get user trends analysis."""
        pass


# class IAnotherRepository(ABC):
#     pass
