"""
Supabase Repository Implementations - Calorie Balance Service

Concrete implementations of domain repository interfaces using Supabase
for the event-driven calorie tracking system.

⚠️  SCHEMA MANAGER PATTERN - MUST FOLLOW:
   1. self.client = get_supabase_client()
   2. self.schema_manager = get_schema_manager()  
   3. self.table = self.schema_manager.table_name  # Pre-configured object!
   4. Use: self.table.select() (NOT self.table)
   
   See docs/databases/cross-schema-patterns.md for complete guide.
"""

import logging
from datetime import date as DateType
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

# Core dependencies
from app.core.database import get_supabase_client

# Core exceptions
from app.core.exceptions import SupabaseError
from app.core.schema_tables import get_schema_manager
from app.domain.entities import (
    CalorieEvent,
    CalorieGoal,
    DailyBalance,
    DailyBalanceSummary,
    DailyCalorieSummary,
    EventType,
    GoalType,
    HourlyCalorieSummary,
    MetabolicProfile,
    MonthlyCalorieSummary,
)

# Domain interfaces and entities
from app.domain.repositories import (
    ICalorieEventRepository,
    ICalorieGoalRepository,
    ICalorieSearchRepository,
    IDailyBalanceRepository,
    IMetabolicProfileRepository,
    ITemporalAnalyticsRepository,
)

logger = logging.getLogger(__name__)


# =============================================================================
# CORE REPOSITORIES - Supabase Implementations
# =============================================================================
# NOTE: User management is handled by user-management microservice
# This service only maintains calorie-specific data with user_id foreign keys


class SupabaseCalorieEventRepository(ICalorieEventRepository):
    """🔥 HIGH-FREQUENCY SUPABASE REPOSITORY - Event-driven core."""

    def __init__(self):
        """Initialize with Supabase client optimized for high-frequency ops."""
        self.client = get_supabase_client()
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.calorie_events
        # Index hints for high-frequency queries
        self._user_time_index = "idx_calorie_events_user_time"

    async def create(self, event: CalorieEvent) -> CalorieEvent:
        """Create single calorie event - optimized for mobile apps."""
        try:
            # Use model_dump with serialize for proper date handling
            event_dict = event.model_dump(mode="json")
            # Convert UUID to string for Supabase
            event_dict["id"] = str(event_dict["id"])

            response = self.table.insert(event_dict).execute()

            if response.data:
                return CalorieEvent(**response.data[0])
            else:
                raise Exception("No data returned from event creation")

        except Exception as e:
            logger.error(f"Failed to create calorie event: {e}")
            raise

    async def create_batch(self, events: List[CalorieEvent]) -> List[CalorieEvent]:
        """Batch create for mobile sync optimization."""
        try:
            events_data = []
            for event in events:
                event_dict = event.dict()
                event_dict["id"] = str(event_dict["id"])
                events_data.append(event_dict)

            response = self.table.insert(events_data).execute()

            return [CalorieEvent(**data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to batch create {len(events)} events: {e}")
            raise

    def _map_event_from_db(self, data: Dict) -> CalorieEvent:
        """Map database row to CalorieEvent entity."""
        # Convert string UUID to UUID object if needed
        if isinstance(data.get("user_id"), str):
            data["user_id"] = UUID(data["user_id"])
        if isinstance(data.get("id"), str):
            data["id"] = UUID(data["id"])

        return CalorieEvent(**data)

    def _map_profile_from_db(self, data: Dict) -> MetabolicProfile:
        """Map database row to MetabolicProfile entity."""
        # Convert string UUID to UUID object if needed
        if isinstance(data.get("user_id"), str):
            data["user_id"] = UUID(data["user_id"])
        if isinstance(data.get("id"), str):
            data["id"] = UUID(data["id"])

        return MetabolicProfile(**data)

    async def get_events_by_user(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        limit: int = 1000,
    ) -> List[CalorieEvent]:
        """Get user events with high-performance temporal filtering."""
        try:
            query = self.table.select("*").eq("user_id", user_id)

            if start_time:
                query = query.gte("event_timestamp", start_time.isoformat())
            if end_time:
                query = query.lte("event_timestamp", end_time.isoformat())
            if event_types:
                query = query.in_("event_type", [et.value for et in event_types])

            query = query.order("event_timestamp", desc=True).limit(limit)
            response = query.execute()

            return [self._map_event_from_db(data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to get events for user {user_id}: {e}")
            return []

    async def get_recent_events(
        self, user_id: str, limit: int = 100
    ) -> List[CalorieEvent]:
        """Get most recent events for timeline display."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", user_id)
                .order("event_timestamp", desc=True)
                .limit(limit)
                .execute()
            )

            # Convert database records to CalorieEvent entities
            events = []
            for data in response.data:
                try:
                    # Convert string user_id to UUID
                    if isinstance(data.get("user_id"), str):
                        data["user_id"] = UUID(data["user_id"])

                    # Convert string event_type to EventType enum
                    if isinstance(data.get("event_type"), str):
                        from app.domain.entities import EventType

                        data["event_type"] = EventType(data["event_type"])

                    # Convert string source to EventSource enum
                    if isinstance(data.get("source"), str):
                        from app.domain.entities import EventSource

                        data["source"] = EventSource(data["source"])

                    # Convert string value to Decimal
                    if data.get("value") and not isinstance(data["value"], Decimal):
                        data["value"] = Decimal(str(data["value"]))

                    # Convert confidence_score to Decimal if present
                    if data.get("confidence_score") and not isinstance(
                        data["confidence_score"], Decimal
                    ):
                        data["confidence_score"] = Decimal(
                            str(data["confidence_score"])
                        )

                    events.append(CalorieEvent(**data))

                except Exception as conversion_error:
                    logger.error(f"Failed to convert event data: {conversion_error}")
                    continue

            return events

        except Exception as e:
            logger.error(f"Failed to get recent events for {user_id}: {e}")
            return []

    async def get_events_in_range(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[CalorieEvent]:
        """Get events for date range analysis."""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(
            end_date, datetime.max.time().replace(microsecond=0)
        )

        return await self.get_events_by_user(user_id, start_datetime, end_datetime)

    async def get_events_by_date_range(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[CalorieEvent]:
        """Get events for date range analysis - alias for compatibility."""
        return await self.get_events_in_range(user_id, start_date, end_date)

    async def update(self, event: CalorieEvent) -> Optional[CalorieEvent]:
        """Update event (rare in event-driven system)."""
        try:
            event_dict = event.dict(exclude={"created_at"})
            event_dict["id"] = str(event_dict["id"])

            response = self.table.update(event_dict).eq("id", str(event.id)).execute()

            if response.data and len(response.data) > 0:
                return self._map_event_from_db(response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update event {event.id}: {e}")
            return None

    async def delete(self, event_id: UUID) -> bool:
        """Delete event (prefer soft delete in production)."""
        try:
            response = self.table.delete().eq("id", str(event_id)).execute()

            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            return False


class SupabaseCalorieGoalRepository(ICalorieGoalRepository):
    """Supabase implementation for dynamic calorie goals."""

    def __init__(self):
        """Initialize with Supabase client."""
        self.client: Client = get_supabase_client()
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.calorie_goals

    def _map_goal_from_db(self, data: Dict) -> CalorieGoal:
        """Map database row to CalorieGoal entity with type conversion."""
        # Convert string IDs to UUID
        if "user_id" in data:
            data["user_id"] = UUID(data["user_id"])
        if "id" in data:
            data["id"] = UUID(data["id"])

        # Convert string dates to date objects
        date_fields = ["start_date", "end_date"]
        for field in date_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field]).date()

        # Convert string datetimes to datetime objects
        datetime_fields = ["created_at", "updated_at"]
        for field in datetime_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    # Handle timezone suffix
                    datetime_str = data[field].replace("Z", "+00:00")
                    data[field] = datetime.fromisoformat(datetime_str)

        # Convert numeric fields to Decimal
        decimal_fields = [
            "daily_calorie_target",
            "daily_deficit_target",
            "weekly_weight_change_kg",
        ]
        for field in decimal_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], Decimal):
                    data[field] = Decimal(str(data[field]))

        # Convert string enum to GoalType
        if "goal_type" in data and data["goal_type"]:
            if isinstance(data["goal_type"], str):
                data["goal_type"] = GoalType(data["goal_type"])

        return CalorieGoal(**data)

    async def get_active_goal(self, user_id: str) -> Optional[CalorieGoal]:
        """Get user's currently active goal."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return self._map_goal_from_db(response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get active goal for {user_id}: {e}")
            return None

    async def get_user_goals(
        self, user_id: str, include_inactive: bool = False
    ) -> List[CalorieGoal]:
        """Get all user goals with optional inactive inclusion."""
        try:
            query = self.table.select("*").eq("user_id", user_id)

            if not include_inactive:
                query = query.eq("is_active", True)

            response = query.order("created_at", desc=True).execute()

            return [self._map_goal_from_db(data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to get goals for user {user_id}: {e}")
            return []

    async def create(self, goal: CalorieGoal) -> CalorieGoal:
        """Create new goal (auto-deactivates conflicting goals)."""
        try:
            # Debug log
            logger.info(f"🔍 DEBUG: Received goal object type: {type(goal)}")
            logger.info(f"🔍 DEBUG: Goal object: {goal}")

            # Deactivate existing active goals of same type
            await self._deactivate_conflicting_goals(goal.user_id, goal.goal_type)

            # Ensure goal is CalorieGoal object with dict method
            if not hasattr(goal, "dict") and not hasattr(goal, "model_dump"):
                logger.error(f"❌ Goal object invalid: {type(goal)}")
                raise ValueError(f"Invalid goal object type: {type(goal)}")

            # Try both Pydantic v1 (dict) and v2 (model_dump) methods
            if hasattr(goal, "model_dump"):
                goal_dict = goal.model_dump()
                logger.info("🔍 DEBUG: Used model_dump() method")
            elif hasattr(goal, "dict"):
                goal_dict = goal.dict()
                logger.info("🔍 DEBUG: Used dict() method")
            else:
                raise ValueError("Goal object has no serialization method")

            logger.info(f"🔍 DEBUG: goal_dict after serialization: {goal_dict}")

            goal_dict["id"] = str(goal_dict["id"])
            goal_dict["user_id"] = str(goal_dict["user_id"])

            # Convert datetime objects to ISO format strings
            if "created_at" in goal_dict and goal_dict["created_at"]:
                goal_dict["created_at"] = goal_dict["created_at"].isoformat()
            if "updated_at" in goal_dict and goal_dict["updated_at"]:
                goal_dict["updated_at"] = goal_dict["updated_at"].isoformat()

            # Convert date objects to ISO format strings
            if "start_date" in goal_dict and goal_dict["start_date"]:
                goal_dict["start_date"] = goal_dict["start_date"].isoformat()
            if "end_date" in goal_dict and goal_dict["end_date"]:
                goal_dict["end_date"] = goal_dict["end_date"].isoformat()

            # Convert Decimal objects to float for JSON serialization
            decimal_fields = [
                "daily_calorie_target",
                "daily_deficit_target",
                "weekly_weight_change_kg",
            ]
            for field in decimal_fields:
                if field in goal_dict and goal_dict[field] is not None:
                    goal_dict[field] = float(goal_dict[field])

            # Convert enum objects to string
            if "goal_type" in goal_dict and goal_dict["goal_type"]:
                goal_dict["goal_type"] = goal_dict["goal_type"].value

            response = self.table.insert(goal_dict).execute()

            if response.data and len(response.data) > 0:
                return self._map_goal_from_db(response.data[0])
            else:
                raise Exception("No data returned from goal creation")

        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            raise

    async def update(self, goal: CalorieGoal) -> Optional[CalorieGoal]:
        """Update existing goal."""
        try:
            goal_dict = goal.dict(exclude={"id", "created_at"})

            # Convert user_id to string
            goal_dict["user_id"] = str(goal_dict["user_id"])

            # Convert datetime objects to ISO format strings
            if "updated_at" in goal_dict and goal_dict["updated_at"]:
                goal_dict["updated_at"] = goal_dict["updated_at"].isoformat()

            # Convert date objects to ISO format strings
            if "start_date" in goal_dict and goal_dict["start_date"]:
                goal_dict["start_date"] = goal_dict["start_date"].isoformat()
            if "end_date" in goal_dict and goal_dict["end_date"]:
                goal_dict["end_date"] = goal_dict["end_date"].isoformat()

            # Convert Decimal objects to float for JSON serialization
            decimal_fields = [
                "daily_calorie_target",
                "daily_deficit_target",
                "weekly_weight_change_kg",
            ]
            for field in decimal_fields:
                if field in goal_dict and goal_dict[field] is not None:
                    goal_dict[field] = float(goal_dict[field])

            # Convert enum objects to string
            if "goal_type" in goal_dict and goal_dict["goal_type"]:
                goal_dict["goal_type"] = goal_dict["goal_type"].value

            response = self.table.update(goal_dict).eq("id", str(goal.id)).execute()

            if response.data and len(response.data) > 0:
                return self._map_goal_from_db(response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update goal {goal.id}: {e}")
            return None

    async def deactivate_goal(self, goal_id: UUID) -> bool:
        """Deactivate goal (soft deletion)."""
        try:
            response = (
                self.table.update(
                    {"is_active": False, "updated_at": datetime.utcnow().isoformat()}
                )
                .eq("id", str(goal_id))
                .execute()
            )

            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Failed to deactivate goal {goal_id}: {e}")
            return False

    async def _deactivate_conflicting_goals(self, user_id: str, goal_type: str) -> None:
        """Helper to deactivate conflicting active goals."""
        try:
            self.table.update(
                {"is_active": False, "updated_at": datetime.utcnow().isoformat()}
            ).eq("user_id", user_id).eq("goal_type", goal_type).eq(
                "is_active", True
            ).execute()

        except Exception as e:
            logger.warning(f"Failed to deactivate conflicting goals: {e}")


class SupabaseDailyBalanceRepository(IDailyBalanceRepository):
    """Supabase implementation for aggregated daily balances."""

    def __init__(self):
        """Initialize with Supabase client."""
        self.client: Client = get_supabase_client()
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.daily_balances

    async def get_by_user_date(
        self, user_id: str, date: DateType
    ) -> Optional[DailyBalance]:
        """Get daily balance for specific date."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", user_id)
                .eq("date", date.isoformat())
                .execute()
            )

            if response.data and len(response.data) > 0:
                return DailyBalance(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get balance for {user_id} on {date}: {e}")
            return None

    async def get_date_range(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[DailyBalance]:
        """Get daily balances for date range."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", user_id)
                .gte("date", start_date.isoformat())
                .lte("date", end_date.isoformat())
                .order("date", desc=False)
                .execute()
            )

            return [DailyBalance(**data) for data in response.data]

        except Exception as e:
            logger.error(
                f"Failed to get balances for {user_id} "
                f"from {start_date} to {end_date}: {e}"
            )
            return []

    async def upsert(self, balance: DailyBalance) -> DailyBalance:
        """Upsert daily balance (create or update)."""
        try:
            balance_dict = balance.dict()
            balance_dict["id"] = str(balance_dict["id"])

            response = self.table.upsert(
                balance_dict, on_conflict="user_id,date"  # Composite unique constraint
            ).execute()

            if response.data and len(response.data) > 0:
                return DailyBalance(**response.data[0])
            else:
                raise Exception("No data returned from balance upsert")

        except Exception as e:
            logger.error(f"Failed to upsert daily balance: {e}")
            raise

    async def recalculate_balance(self, user_id: str, date: DateType) -> DailyBalance:
        """Recalculate balance from events (data consistency)."""
        # This would typically call a stored procedure or trigger
        # that recalculates from the events table
        try:
            # Call Supabase function in calorie_balance schema
            response = (
                self.client.schema("calorie_balance")
                .rpc(
                    "recalculate_daily_balance",
                    {"p_user_id": user_id, "p_date": date.isoformat()},
                )
                .execute()
            )

            if response.data:
                return DailyBalance(**response.data[0])
            else:
                raise Exception(f"Failed to recalculate balance")

        except Exception as e:
            logger.error(
                f"Failed to recalculate balance for " f"{user_id} on {date}: {e}"
            )
            raise


class SupabaseMetabolicProfileRepository(IMetabolicProfileRepository):
    """Supabase implementation for metabolic calculations."""

    def __init__(self):
        """Initialize with Supabase client."""
        self.schema_manager = get_schema_manager()
        self.table = self.schema_manager.metabolic_profiles

    def _map_profile_from_db(self, data: Dict) -> MetabolicProfile:
        """Map database row to MetabolicProfile entity."""
        # Convert string UUID to UUID object if needed
        if isinstance(data.get("user_id"), str):
            data["user_id"] = UUID(data["user_id"])
        if isinstance(data.get("id"), str):
            data["id"] = UUID(data["id"])

        # Map database column names to entity field names - ALL REAL DATA FROM DB
        mapped_data = {
            "id": data.get("id"),
            "user_id": data.get("user_id"),
            "bmr_calories": Decimal(str(data.get("bmr_calories", 0))),
            "tdee_calories": Decimal(str(data.get("tdee_calories", 0))),
            "calculation_date": datetime.fromisoformat(
                data.get("calculated_at", datetime.now().isoformat())
            ),
            "calculation_method": data.get("calculation_method", "mifflin_st_jeor"),
            "created_at": datetime.fromisoformat(
                data.get("calculated_at", datetime.now().isoformat())
            ),
            "updated_at": datetime.now(),
            # Complete database mapping - all 21 entity fields
            "activity_level": data.get("activity_level", "moderate"),
            "sedentary_multiplier": self._safe_decimal(
                data.get("sedentary_multiplier", 1.2)
            ),
            "light_multiplier": self._safe_decimal(data.get("light_multiplier", 1.375)),
            "moderate_multiplier": self._safe_decimal(
                data.get("moderate_multiplier", 1.55)
            ),
            "high_multiplier": self._safe_decimal(data.get("high_multiplier", 1.725)),
            "extreme_multiplier": self._safe_decimal(
                data.get("extreme_multiplier", 1.9)
            ),
            "rmr_calories": self._safe_decimal(
                data.get("rmr_calories", data.get("bmr_calories")), "1700"
            ),
            "accuracy_score": self._safe_decimal(data.get("accuracy_score"), "0.95"),
            "ai_adjusted": data.get("ai_adjusted", False),
            "adjustment_factor": self._safe_decimal(data.get("adjustment_factor", 1.0)),
            "learning_iterations": int(data.get("learning_iterations", 0)),
            "calculated_at": datetime.fromisoformat(
                data.get("calculated_at", datetime.now().isoformat())
            ),
            "expires_at": datetime.fromisoformat(
                data.get(
                    "expires_at", (datetime.now() + timedelta(days=30)).isoformat()
                )
            )
            if data.get("expires_at")
            else datetime.now() + timedelta(days=30),
            "is_active": data.get("is_active", True),
        }

        return MetabolicProfile(**mapped_data)

    def _safe_decimal(self, value, default_value="1500") -> Decimal:
        """Safely convert value to Decimal, handling various input types."""
        if isinstance(value, Decimal):
            return value
        if value is None:
            return Decimal(str(default_value))
        try:
            # Direct conversion - don't convert to string first if already a number
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            return Decimal(str(value))
        except (ValueError, TypeError, Exception):
            return Decimal(str(default_value))

    async def get_latest(self, user_id: str) -> Optional[MetabolicProfile]:
        """Get user's latest metabolic profile."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", user_id)
                .order("calculated_at", desc=True)
                .limit(1)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return self._map_profile_from_db(response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get latest profile for {user_id}: {e}")
            return None

    async def get_history(
        self, user_id: str, limit: int = 10
    ) -> List[MetabolicProfile]:
        """Get metabolic profile history."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", user_id)
                .order("calculated_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [self._map_profile_from_db(data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to get profile history for {user_id}: {e}")
            return []

    async def create(self, profile: MetabolicProfile) -> MetabolicProfile:
        """Create new metabolic profile."""
        try:
            # Convert entity to dict with database schema mapping
            # Only include fields that exist in the database table
            profile_dict = {
                "id": str(profile.id),
                "user_id": str(profile.user_id),
                "bmr_calories": float(profile.bmr_calories),
                "tdee_calories": float(profile.tdee_calories),
                "rmr_calories": float(profile.rmr_calories),
                "calculation_method": profile.calculation_method,
                "accuracy_score": float(profile.accuracy_score),
                # Activity level and multipliers (from 006 migration)
                "activity_level": profile.activity_level,
                "sedentary_multiplier": float(profile.sedentary_multiplier),
                "light_multiplier": float(profile.light_multiplier),
                "moderate_multiplier": float(profile.moderate_multiplier),
                "high_multiplier": float(profile.high_multiplier),
                "extreme_multiplier": float(profile.extreme_multiplier),
                # AI fields (from original schema)
                "ai_adjusted": profile.ai_adjusted,
                "adjustment_factor": float(profile.adjustment_factor),
                "learning_iterations": profile.learning_iterations,
                # Timestamps (only ones that exist in DB)
                "calculated_at": profile.calculated_at.isoformat(),
                "expires_at": profile.expires_at.isoformat()
                if profile.expires_at
                else None,
                "is_active": profile.is_active,
            }

            response = self.table.insert(profile_dict).execute()

            if response.data and len(response.data) > 0:
                return self._map_profile_from_db(response.data[0])
            else:
                raise Exception("No data returned from profile creation")

        except Exception as e:
            logger.error(f"Failed to create metabolic profile: {e}")
            raise


# Continued in next section due to length...
class SupabaseTemporalAnalyticsRepository(ITemporalAnalyticsRepository):
    """Supabase implementation for 5-level temporal analytics views."""

    def __init__(self):
        """Initialize with Supabase client for analytics views."""
        self.client: Client = get_supabase_client()
        self.schema_manager = get_schema_manager()
        # Views from schema manager (pre-configured with schema)
        self.hourly_view = self.schema_manager.hourly_calorie_summary
        self.daily_view = self.schema_manager.daily_calorie_summary
        self.weekly_view = self.schema_manager.weekly_calorie_summary
        self.monthly_view = self.schema_manager.monthly_calorie_summary
        self.balance_view = self.schema_manager.daily_balance_summary

    async def get_hourly_summary(
        self, user_id: str, date: DateType
    ) -> List[HourlyCalorieSummary]:
        """Get hourly calorie summary for a specific date."""
        try:
            response = (
                self.hourly_view.select("*")
                .eq("user_id", user_id)
                .eq("date", date.isoformat())
                .order("hour")
                .execute()
            )

            return [HourlyCalorieSummary(**data) for data in response.data]

        except Exception as e:
            logger.error(
                f"Failed to get hourly summary for {user_id} " f"on {date}: {e}"
            )
            return []

    async def get_daily_summary(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[DailyCalorieSummary]:
        """Get daily summaries for date range."""
        try:
            response = (
                self.daily_view.select("*")
                .eq("user_id", user_id)
                .gte("date", start_date.isoformat())
                .lte("date", end_date.isoformat())
                .order("date")
                .execute()
            )

            return [DailyCalorieSummary(**data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to get daily summaries for {user_id}: {e}")
            return []

    async def get_weekly_summary(
        self, user_id: str, weeks_back: int = 12
    ) -> List[Dict[str, Any]]:
        """Get weekly summaries for the specified number of weeks back."""
        try:
            # Use our existing get_user_statistics RPC function
            # to get weekly data
            import json
            from datetime import datetime, timedelta

            end_date = datetime.now().date()
            start_date = end_date - timedelta(weeks=weeks_back)

            # Call the RPC function we created in calorie_balance schema
            response = (
                self.client.schema("calorie_balance")
                .rpc(
                    "get_user_statistics",
                    {
                        "p_user_id": user_id,
                        "p_start_date": str(start_date),
                        "p_end_date": str(end_date),
                    },
                )
                .execute()
            )

            if response.data:
                # Parse the JSON response from RPC function
                if isinstance(response.data, dict):
                    stats_data = response.data
                else:
                    stats_data = json.loads(response.data)

                # Create weekly summary format for last weeks_back weeks
                weekly_summaries = []
                current_date = end_date

                for week_num in range(weeks_back):
                    week_end = current_date - timedelta(days=week_num * 7)
                    week_start = week_end - timedelta(days=6)

                    # Use averaged data from statistics (simplified approach)
                    averages = stats_data.get("averages", {})
                    weekly_summary = {
                        "week_start": str(week_start),
                        "week_end": str(week_end),
                        "avg_daily_consumed": float(averages.get("daily_consumed", 0)),
                        "avg_daily_burned": float(averages.get("daily_burned", 0)),
                        "avg_net_calories": float(averages.get("daily_net", 0)),
                        "total_weight_change": None,
                        "active_days": 7,  # Assume full week for now
                        "goal_adherence_pct": None,  # Calculate if needed
                    }
                    weekly_summaries.append(weekly_summary)

                # Reverse to get chronological order (oldest first)
                return list(reversed(weekly_summaries))

            return []

        except Exception as e:
            logger.error(f"Failed to get weekly summaries for {user_id}: {e}")
            return []

    async def get_monthly_summary(
        self, user_id: str, year: int, month: Optional[int] = None
    ) -> List[MonthlyCalorieSummary]:
        """Get monthly summaries for year (optional specific month)."""
        try:
            query = (
                self.monthly_view.select("*").eq("user_id", user_id).eq("year", year)
            )

            if month:
                query = query.eq("month", month)

            response = query.order("month").execute()

            return [MonthlyCalorieSummary(**data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to get monthly summaries for {user_id}: {e}")
            return []

    async def get_balance_summary(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[DailyBalanceSummary]:
        """Get daily balance with goal comparison."""
        try:
            response = (
                self.balance_view.select("*")
                .eq("user_id", user_id)
                .gte("date", start_date.isoformat())
                .lte("date", end_date.isoformat())
                .order("date")
                .execute()
            )

            return [DailyBalanceSummary(**data) for data in response.data]

        except Exception as e:
            logger.error(f"Failed to get balance summaries for {user_id}: {e}")
            return []


class SupabaseCalorieSearchRepository(ICalorieSearchRepository):
    """Supabase implementation for complex search operations."""

    def __init__(self):
        """Initialize with Supabase client."""
        self.client: Client = get_supabase_client()
        self.schema_manager = get_schema_manager()
        self.calorie_events = self.schema_manager.calorie_events

    async def search_events(
        self, user_id: str, filters: Dict[str, Any], page: int = 1, page_size: int = 100
    ) -> Dict[str, Any]:
        """Complex event search with pagination."""
        try:
            offset = (page - 1) * page_size

            query = self.calorie_events.select("*", count="exact").eq(
                "user_id", user_id
            )

            # Apply filters
            for key, value in filters.items():
                if key == "event_type" and value:
                    query = query.eq("event_type", value)
                elif key == "date_from" and value:
                    query = query.gte("event_timestamp", value)
                elif key == "date_to" and value:
                    query = query.lte("event_timestamp", value)
                elif key == "min_value" and value:
                    query = query.gte("value", value)
                elif key == "max_value" and value:
                    query = query.lte("value", value)
                elif key == "source" and value:
                    query = query.eq("source", value)

            response = (
                query.order("event_timestamp", desc=True)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            return {
                "events": [CalorieEvent(**data) for data in response.data],
                "total": response.count,
                "page": page,
                "page_size": page_size,
                "total_pages": (response.count + page_size - 1) // page_size,
            }

        except Exception as e:
            logger.error(f"Failed to search events for {user_id}: {e}")
            return {
                "events": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
            }

    async def get_statistics(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        try:
            # Call RPC function in calorie_balance schema
            response = (
                self.client.schema("calorie_balance")
                .rpc(
                    "get_user_statistics",
                    {
                        "p_user_id": user_id,
                        "p_start_date": start_date.isoformat(),
                        "p_end_date": end_date.isoformat(),
                    },
                )
                .execute()
            )

            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Failed to get statistics for {user_id}: {e}")
            return {}

    async def get_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user trends analysis."""
        try:
            # Call RPC function in calorie_balance schema
            response = (
                self.client.schema("calorie_balance")
                .rpc("get_user_trends", {"p_user_id": user_id, "p_days": days})
                .execute()
            )

            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Failed to get trends for {user_id}: {e}")
            return {}
