"""
Application Services - Calorie Balance Service

Business logic orchestration for event-driven calorie tracking.
Use case implementation and cross-cutting concerns.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date as DateType, timedelta
from decimal import Decimal
import logging
from datetime import date  # For date.today() usage

# Domain entities and repositories
from app.domain.entities import (
    User, CalorieEvent, CalorieGoal, DailyBalance, MetabolicProfile,
    EventType, EventSource, GenderType, ActivityLevel, GoalType,
    HourlyCalorieSummary, DailyCalorieSummary, WeeklyCalorieSummary,
    MonthlyCalorieSummary, DailyBalanceSummary
)
from app.domain.repositories import (
    IUserRepository, ICalorieEventRepository, ICalorieGoalRepository,
    IDailyBalanceRepository, IMetabolicProfileRepository,
    ITemporalAnalyticsRepository, ICalorieSearchRepository
)

logger = logging.getLogger(__name__)


# =============================================================================
# CORE BUSINESS SERVICES - Event-Driven Architecture
# =============================================================================

class CalorieEventService:
    """🔥 HIGH-FREQUENCY SERVICE - Core of event-driven architecture."""
    
    def __init__(
        self,
        event_repo: ICalorieEventRepository,
        balance_repo: IDailyBalanceRepository,
        user_repo: IUserRepository
    ):
        self.event_repo = event_repo
        self.balance_repo = balance_repo
        self.user_repo = user_repo
    
    async def record_calorie_consumed(
        self,
        user_id: str,
        calories: Decimal,
        source: EventSource = EventSource.MANUAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CalorieEvent:
        """Record calorie consumption event - optimized for mobile."""
        event = CalorieEvent(
            id=uuid4(),
            user_id=user_id,
            event_type=EventType.CONSUMED,
            event_timestamp=datetime.utcnow(),
            value=calories,
            source=source,
            confidence_score=Decimal("1.0"),
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            # Store high-frequency event
            created_event = await self.event_repo.create(event)
            
            # Trigger daily balance update (async in production)
            await self._update_daily_balance(user_id, event.event_timestamp.date())
            
            return created_event
            
        except Exception as e:
            logger.error(f"Failed to record calories consumed: {e}")
            raise
    
    async def record_calorie_burned_exercise(
        self,
        user_id: str,
        calories: Decimal,
        source: EventSource = EventSource.FITNESS_TRACKER,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CalorieEvent:
        """Record exercise calorie burn event."""
        event = CalorieEvent(
            id=uuid4(),
            user_id=user_id,
            event_type=EventType.BURNED_EXERCISE,
            event_timestamp=datetime.utcnow(),
            value=calories,
            source=source,
            confidence_score=Decimal("0.85"),  # Exercise tracking less precise
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            created_event = await self.event_repo.create(event)
            await self._update_daily_balance(user_id, event.event_timestamp.date())
            return created_event
            
        except Exception as e:
            logger.error(f"Failed to record calories burned: {e}")
            raise
    
    async def record_weight_measurement(
        self,
        user_id: str,
        weight_kg: Decimal,
        source: EventSource = EventSource.SMART_SCALE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CalorieEvent:
        """Record weight measurement event."""
        event = CalorieEvent(
            id=uuid4(),
            user_id=user_id,
            event_type=EventType.WEIGHT,
            event_timestamp=datetime.utcnow(),
            value=weight_kg,
            source=source,
            confidence_score=Decimal("0.95"),  # Weight scales quite accurate
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            created_event = await self.event_repo.create(event)
            
            # Update user's current weight
            await self._update_user_weight(user_id, weight_kg)
            
            # Update daily balance with weight
            await self._update_daily_balance_weight(
                user_id, event.event_timestamp.date(), weight_kg
            )
            
            return created_event
            
        except Exception as e:
            logger.error(f"Failed to record weight: {e}")
            raise
    
    async def batch_record_events(
        self, user_id: str, events_data: List[Dict[str, Any]]
    ) -> List[CalorieEvent]:
        """Batch record events for mobile sync optimization."""
        try:
            events = []
            for event_data in events_data:
                event = CalorieEvent(
                    id=uuid4(),
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    **event_data
                )
                events.append(event)
            
            # Batch insert for performance
            created_events = await self.event_repo.create_batch(events)
            
            # Update daily balances for affected dates
            affected_dates = set(
                event.event_timestamp.date() for event in created_events
            )
            for date in affected_dates:
                await self._update_daily_balance(user_id, date)
            
            return created_events
            
        except Exception as e:
            logger.error(f"Failed to batch record events: {e}")
            raise
    
    async def get_recent_timeline(
        self, user_id: str, limit: int = 100
    ) -> List[CalorieEvent]:
        """Get recent events for timeline display."""
        return await self.event_repo.get_recent_events(user_id, limit)
    
    async def get_events_by_date_range(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> List[CalorieEvent]:
        """Get events for specific date range."""
        return await self.event_repo.get_events_by_date_range(
            user_id, start_date, end_date
        )
    
    async def _update_daily_balance(
        self, user_id: str, date: DateType
    ) -> None:
        """Update daily balance aggregation (background task)."""
        try:
            # In production, this would be an async background task
            await self.balance_repo.recalculate_balance(user_id, date)
            
        except Exception as e:
            logger.warning(f"Failed to update daily balance: {e}")
    
    async def _update_daily_balance_weight(
        self, user_id: str, date: DateType, weight: Decimal
    ) -> None:
        """Update daily balance with weight measurement."""
        try:
            balance = await self.balance_repo.get_by_user_date(user_id, date)
            if balance:
                # Determine morning vs evening weight
                current_hour = datetime.utcnow().hour
                if current_hour < 12:
                    balance.morning_weight_kg = weight
                else:
                    balance.evening_weight_kg = weight
                
                await self.balance_repo.upsert(balance)
            
        except Exception as e:
            logger.warning(f"Failed to update balance weight: {e}")
    
    async def _update_user_weight(self, user_id: str, weight: Decimal) -> None:
        """Update user's current weight for BMR recalculation."""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if user:
                user.current_weight_kg = weight
                await self.user_repo.update(user)
            
        except Exception as e:
            logger.warning(f"Failed to update user weight: {e}")


class CalorieGoalService:
    """Service for dynamic calorie goal management."""
    
    def __init__(
        self,
        goal_repo: ICalorieGoalRepository,
        user_repo: IUserRepository,
        metabolic_service: 'MetabolicCalculationService'
    ):
        self.goal_repo = goal_repo
        self.user_repo = user_repo
        self.metabolic_service = metabolic_service
    
    async def create_weight_loss_goal(
        self,
        user_id: str,
        target_weight_kg: Decimal,
        weekly_loss_kg: Decimal = Decimal("0.5")
    ) -> CalorieGoal:
        """Create AI-optimized weight loss goal."""
        try:
            # Calculate calorie target based on metabolic profile
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get latest metabolic profile
            metabolic_profile = await self.metabolic_service.get_or_calculate_profile(user_id)
            
            # Calculate daily calorie deficit (3500 cal = 1 lb = 0.45 kg)
            weekly_calorie_deficit = weekly_loss_kg * Decimal("7700")  # Cal per kg
            daily_deficit = weekly_calorie_deficit / 7
            
            daily_target = metabolic_profile.tdee_calories - daily_deficit
            
            # Create goal
            goal = CalorieGoal(
                id=uuid4(),
                user_id=user_id,
                goal_type=GoalType.WEIGHT_LOSS,
                daily_calorie_target=daily_target,
                daily_deficit_target=daily_deficit,
                weekly_weight_change_kg=-weekly_loss_kg,
                start_date=date.today(),
                end_date=None,
                is_active=True,
                ai_optimized=True,
                optimization_metadata={
                    "target_weight_kg": str(target_weight_kg),
                    "calculated_from_tdee": str(metabolic_profile.tdee_calories),
                    "method": "calorie_deficit_3500_rule"
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Update user target weight
            user.target_weight_kg = target_weight_kg
            await self.user_repo.update(user)
            
            return await self.goal_repo.create(goal)
            
        except Exception as e:
            logger.error(f"Failed to create weight loss goal: {e}")
            raise
    
    async def get_active_goal(self, user_id: str) -> Optional[CalorieGoal]:
        """Get user's currently active goal."""
        return await self.goal_repo.get_active_goal(user_id)
    
    async def optimize_goal_ai(self, user_id: str) -> Optional[CalorieGoal]:
        """AI-optimize existing goal based on progress data."""
        # This would integrate with AI/ML service for goal optimization
        # Based on actual vs predicted progress
        try:
            current_goal = await self.goal_repo.get_active_goal(user_id)
            if not current_goal:
                return None
            
            # TODO: Implement AI optimization logic
            # - Analyze progress vs target
            # - Adjust calorie targets
            # - Update goal parameters
            
            return current_goal
            
        except Exception as e:
            logger.error(f"Failed to optimize goal: {e}")
            return None


class MetabolicCalculationService:
    """Service for BMR/TDEE calculations and metabolic profiling."""
    
    def __init__(
        self,
        user_repo: IUserRepository,
        profile_repo: IMetabolicProfileRepository
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
    
    async def calculate_bmr_mifflin(
        self, weight_kg: Decimal, height_cm: Decimal, age: int, gender: GenderType
    ) -> Decimal:
        """Calculate BMR using Mifflin-St Jeor equation."""
        # Men: BMR = 10W + 6.25H - 5A + 5
        # Women: BMR = 10W + 6.25H - 5A - 161
        
        base = 10 * weight_kg + Decimal("6.25") * height_cm - 5 * age
        
        if gender == GenderType.MALE:
            return base + 5
        elif gender == GenderType.FEMALE:
            return base - 161
        else:  # OTHER
            return base - 78  # Average of male/female
    
    async def calculate_tdee(
        self, bmr: Decimal, activity_level: ActivityLevel
    ) -> Decimal:
        """Calculate TDEE from BMR and activity level."""
        multipliers = {
            ActivityLevel.SEDENTARY: Decimal("1.2"),
            ActivityLevel.LIGHT: Decimal("1.375"),
            ActivityLevel.MODERATE: Decimal("1.55"),
            ActivityLevel.HIGH: Decimal("1.725"),
            ActivityLevel.EXTREME: Decimal("1.9")
        }
        
        return bmr * multipliers[activity_level]
    
    async def get_or_calculate_profile(
        self, user_id: str
    ) -> MetabolicProfile:
        """Get latest profile or calculate new one."""
        try:
            # Try to get recent profile (within 30 days)
            profile = await self.profile_repo.get_latest(user_id)
            if (profile and 
                (datetime.utcnow() - profile.calculation_date).days < 30):
                return profile
            
            # Calculate new profile
            user = await self.user_repo.get_by_id(user_id)
            if not user or not all([
                user.current_weight_kg, user.height_cm, user.age, user.gender
            ]):
                raise ValueError("Insufficient user data for metabolic calculation")
            
            bmr = await self.calculate_bmr_mifflin(
                user.current_weight_kg, user.height_cm, 
                user.age, user.gender
            )
            
            tdee = await self.calculate_tdee(bmr, user.activity_level)
            
            # Create new profile
            profile = MetabolicProfile(
                id=uuid4(),
                user_id=user_id,
                bmr_calories=bmr,
                tdee_calories=tdee,
                calculation_method="mifflin_st_jeor",
                calculation_date=datetime.utcnow(),
                activity_multiplier=await self._get_activity_multiplier(
                    user.activity_level
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store profile and update user cache
            profile = await self.profile_repo.create(profile)
            await self.user_repo.update_metabolic_rates(user_id, bmr, tdee)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get/calculate metabolic profile: {e}")
            raise
    
    async def _get_activity_multiplier(
        self, activity_level: ActivityLevel
    ) -> Decimal:
        """Get activity multiplier for TDEE calculation."""
        multipliers = {
            ActivityLevel.SEDENTARY: Decimal("1.2"),
            ActivityLevel.LIGHT: Decimal("1.375"),
            ActivityLevel.MODERATE: Decimal("1.55"),
            ActivityLevel.HIGH: Decimal("1.725"),
            ActivityLevel.EXTREME: Decimal("1.9")
        }
        return multipliers[activity_level]


class AnalyticsService:
    """Service for temporal analytics and insights."""
    
    def __init__(
        self,
        analytics_repo: ITemporalAnalyticsRepository,
        search_repo: ICalorieSearchRepository
    ):
        self.analytics_repo = analytics_repo
        self.search_repo = search_repo
    
    async def get_daily_dashboard(
        self, user_id: str, date: DateType
    ) -> Dict[str, Any]:
        """Get comprehensive daily dashboard data."""
        try:
            # Get daily summary
            daily_summaries = await self.analytics_repo.get_daily_summary(
                user_id, date, date
            )
            daily = daily_summaries[0] if daily_summaries else None
            
            # Get hourly breakdown
            hourly = await self.analytics_repo.get_hourly_summary(user_id, date)
            
            # Get balance with goals
            balance_summaries = await self.analytics_repo.get_balance_summary(
                user_id, date, date
            )
            balance = balance_summaries[0] if balance_summaries else None
            
            return {
                "date": date.isoformat(),
                "daily_summary": daily,
                "hourly_breakdown": hourly,
                "goal_progress": balance,
                "insights": await self._generate_daily_insights(daily, balance)
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily dashboard: {e}")
            return {}
    
    async def get_weekly_trends(
        self, user_id: str, weeks_back: int = 4
    ) -> Dict[str, Any]:
        """Get weekly trends and progress analysis."""
        try:
            current_year = datetime.utcnow().year
            current_week = datetime.utcnow().isocalendar()[1]
            
            weeks = []
            for i in range(weeks_back):
                week_num = current_week - i
                if week_num < 1:
                    week_num += 52
                    year = current_year - 1
                else:
                    year = current_year
                
                weekly = await self.analytics_repo.get_weekly_summary(
                    user_id, year, week_num
                )
                if weekly:
                    weeks.extend(weekly)
            
            return {
                "weekly_summaries": weeks,
                "trends": await self._analyze_weekly_trends(weeks),
                "recommendations": await self._generate_recommendations(weeks)
            }
            
        except Exception as e:
            logger.error(f"Failed to get weekly trends: {e}")
            return {}
    
    async def _generate_daily_insights(
        self, daily: Optional[DailyCalorieSummary],
        balance: Optional[DailyBalanceSummary]
    ) -> List[str]:
        """Generate AI-powered daily insights."""
        insights = []
        
        if daily:
            # Calorie distribution insights
            if daily.calories_consumed > daily.calories_burned_exercise * 2:
                insights.append(
                    "Consider increasing physical activity to balance intake"
                )
            
            if daily.active_hours < 8:
                insights.append(
                    "Try to spread calorie intake across more hours"
                )
        
        if balance and balance.target_deviation:
            if balance.target_deviation > 200:
                insights.append("Calorie intake significantly above target")
            elif balance.target_deviation < -200:
                insights.append("Consider eating more to meet energy needs")
        
        return insights
    
    async def _analyze_weekly_trends(
        self, weeks: List[WeeklyCalorieSummary]
    ) -> Dict[str, Any]:
        """Analyze trends in weekly data."""
        if len(weeks) < 2:
            return {}
        
        # Calculate trend slopes
        net_calorie_trend = []
        weight_change_trend = []
        
        for i in range(1, len(weeks)):
            prev_week = weeks[i-1]
            curr_week = weeks[i]
            
            net_calorie_trend.append(
                curr_week.weekly_net_calories - prev_week.weekly_net_calories
            )
            
            if (curr_week.week_end_weight and prev_week.week_start_weight):
                weight_change = (
                    curr_week.week_end_weight - prev_week.week_start_weight
                )
                weight_change_trend.append(weight_change)
        
        return {
            "net_calorie_trend": "increasing" if sum(net_calorie_trend) > 0 
                               else "decreasing",
            "average_weight_change_per_week": (
                sum(weight_change_trend) / len(weight_change_trend) 
                if weight_change_trend else None
            ),
            "consistency_score": await self._calculate_consistency_score(weeks)
        }
    
    async def _generate_recommendations(
        self, weeks: List[WeeklyCalorieSummary]
    ) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if weeks:
            latest_week = weeks[0]
            if latest_week.active_days < 5:
                recommendations.append(
                    "Try to be active at least 5 days per week"
                )
            
            avg_daily_net = latest_week.weekly_net_calories / 7
            if avg_daily_net > 500:
                recommendations.append(
                    "Consider increasing daily physical activity"
                )
        
        return recommendations
    
    async def _calculate_consistency_score(
        self, weeks: List[WeeklyCalorieSummary]
    ) -> float:
        """Calculate consistency score based on weekly variation."""
        if len(weeks) < 2:
            return 1.0
        
        # Calculate coefficient of variation for net calories
        net_calories = [week.weekly_net_calories for week in weeks]
        mean = sum(net_calories) / len(net_calories)
        variance = sum((x - mean) ** 2 for x in net_calories) / len(net_calories)
        std_dev = variance ** 0.5
        
        cv = std_dev / mean if mean != 0 else 0
        
        # Convert to 0-1 score (lower CV = higher consistency)
        return max(0, 1 - cv / 2)  # Normalize assuming max CV of 2
