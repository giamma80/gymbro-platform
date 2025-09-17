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
    CalorieEvent, CalorieGoal, DailyBalance, MetabolicProfile,
    EventType, EventSource, GenderType, ActivityLevel, GoalType,
    HourlyCalorieSummary, DailyCalorieSummary, WeeklyCalorieSummary,
    MonthlyCalorieSummary, DailyBalanceSummary
)
from app.domain.repositories import (
    ICalorieEventRepository, ICalorieGoalRepository,
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
        balance_repo: IDailyBalanceRepository
    ):
        self.event_repo = event_repo
        self.balance_repo = balance_repo
    
    async def record_calorie_consumed(
        self,
        user_id: str,
        calories: Decimal,
        source: EventSource = EventSource.MANUAL,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> CalorieEvent:
        """Record calorie consumption event - optimized for mobile."""
        event = CalorieEvent(
            id=uuid4(),
            user_id=user_id,
            event_type=EventType.CONSUMED,
            event_timestamp=timestamp or datetime.utcnow(),
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
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> CalorieEvent:
        """Record exercise calorie burn event."""
        event = CalorieEvent(
            id=uuid4(),
            user_id=user_id,
            event_type=EventType.BURNED_EXERCISE,
            event_timestamp=timestamp or datetime.utcnow(),
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
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> CalorieEvent:
        """Record weight measurement event."""
        event = CalorieEvent(
            id=uuid4(),
            user_id=user_id,
            event_type=EventType.WEIGHT,
            event_timestamp=timestamp or datetime.utcnow(),
            value=weight_kg,
            source=source,
            confidence_score=Decimal("0.95"),  # Weight scales quite accurate
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            created_event = await self.event_repo.create(event)
            
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


class CalorieGoalService:
    """Service for dynamic calorie goal management."""
    
    def __init__(
        self,
        goal_repo: ICalorieGoalRepository,
        metabolic_service: 'MetabolicCalculationService'
    ):
        self.goal_repo = goal_repo
        self.metabolic_service = metabolic_service
    
    async def create_weight_loss_goal(
        self, 
        user_id: UUID, 
        target_weight_kg: Decimal, 
        weekly_loss_kg: Decimal,
        # Parameter Passing Pattern - User metrics provided by client
        current_weight_kg: Decimal,
        height_cm: Decimal,
        age: int,
        gender: GenderType,
        activity_level: ActivityLevel
    ) -> CalorieGoal:
        """
        Create intelligent weight loss goal using Parameter Passing pattern.
        
        User metrics are provided by client (mobile app, N8N orchestrator)
        ensuring microservice decoupling and reusability.
        """
        try:
            # Calculate metabolic profile with provided user metrics
            metabolic_profile = await self.metabolic_service.calculate_metabolic_profile(
                user_id=user_id,
                weight_kg=current_weight_kg,
                height_cm=height_cm,
                age=age,
                gender=gender,
                activity_level=activity_level
            )
            
            # Calculate daily calorie deficit (3500 cal = 1 lb = 0.45 kg)
            weekly_calorie_deficit = weekly_loss_kg * Decimal("7700")  # Cal per kg
            daily_deficit = weekly_calorie_deficit / 7
            
            daily_target = metabolic_profile.tdee_calories - daily_deficit
            
            # Calculate end_date if target_weight_kg is provided
            end_date = None
            logger.info(f"End date calculation - target_weight_kg: {target_weight_kg}, user_weight_kg: {user_weight_kg}, weekly_weight_change_kg: {weekly_weight_change_kg}")
            logger.info(f"Types: target_weight_kg: {type(target_weight_kg)}, user_weight_kg: {type(user_weight_kg)}, weekly_weight_change_kg: {type(weekly_weight_change_kg)}")
            
            if target_weight_kg and user_weight_kg and weekly_weight_change_kg:
                logger.info("All parameters present for end_date calculation")
                # Calculate weeks needed to reach target
                weight_diff = abs(float(user_weight_kg - target_weight_kg))
                weeks_needed = weight_diff / float(weekly_weight_change_kg)
                
                logger.info(f"Weight difference: {weight_diff} kg, Weeks needed: {weeks_needed}")
                
                # Calculate end date
                end_date = date.today() + timedelta(weeks=int(weeks_needed))
                logger.info(f"Calculated end_date: {end_date}")
            else:
                logger.info("Missing parameters for end_date calculation - will be null")
            
            # Create goal
            goal = CalorieGoal(
                id=uuid4(),
                user_id=user_id,
                goal_type=GoalType.WEIGHT_LOSS,
                daily_calorie_target=daily_target,
                daily_deficit_target=daily_deficit,
                weekly_weight_change_kg=-weekly_loss_kg,
                start_date=date.today(),
                end_date=end_date,
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
            
            # NOTE: target_weight_kg should be updated in user-management service
            # via frontend orchestration or N8N workflow
            
            return await self.goal_repo.create(goal)
            
        except Exception as e:
            logger.error(f"Failed to create weight loss goal: {e}")
            raise
    
    async def create_goal(
        self,
        user_id: str,
        goal_type: GoalType,
        target_weight_kg: Optional[Decimal] = None,
        target_date: Optional[DateType] = None,
        weekly_weight_change_kg: Optional[Decimal] = None,
        activity_level: Optional[str] = None,
        custom_calorie_target: Optional[Decimal] = None,
        # Parameter Passing - User metrics provided by client
        user_weight_kg: Optional[Decimal] = None,
        user_height_cm: Optional[Decimal] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None
    ) -> CalorieGoal:
        """
        Create calorie goal using Parameter Passing pattern.
        
        User metrics are provided by client ensuring microservice decoupling.
        """
        logger.info("🔥🔥🔥 STARTING CREATE_GOAL METHOD - DEBUG VERSION LOADED! 🔥🔥🔥")
        logger.info("TEST LOG: Code version with end_date calculation active")
        try:
            # Convert user_id to UUID for domain layer compatibility
            from uuid import UUID
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                # For non-UUID user_ids, generate deterministic UUID
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()
                # Format as proper UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  
                formatted_hash = f"{user_hash[:8]}-{user_hash[8:12]}-{user_hash[12:16]}-{user_hash[16:20]}-{user_hash[20:32]}"
                user_uuid = UUID(formatted_hash)
                logger.info(f"Generated UUID {user_uuid} for user_id {user_id}")
            
            # If custom target provided, use it directly
            if custom_calorie_target:
                daily_target = custom_calorie_target
            elif all([user_weight_kg, user_height_cm, user_age, user_gender]):
                # Calculate target using provided user metrics
                from app.domain.entities import GenderType, ActivityLevel
                
                gender_enum = GenderType(user_gender) if user_gender else GenderType.OTHER
                activity_enum = ActivityLevel(activity_level) if activity_level else ActivityLevel.MODERATE
                
                # Calculate metabolic profile
                metabolic_profile = await self.metabolic_service.calculate_metabolic_profile(
                    user_id=str(user_uuid),  # Pass as string to metabolic service
                    weight_kg=user_weight_kg,
                    height_cm=user_height_cm,
                    age=user_age,
                    gender=gender_enum,
                    activity_level=activity_enum
                )
                
                if goal_type == GoalType.WEIGHT_LOSS and weekly_weight_change_kg:
                    # Calculate calorie deficit for weight loss
                    weekly_calorie_deficit = abs(weekly_weight_change_kg) * Decimal("7700")  # Cal per kg
                    daily_deficit = weekly_calorie_deficit / 7
                    daily_target = metabolic_profile.tdee_calories - daily_deficit
                elif goal_type == GoalType.WEIGHT_GAIN and weekly_weight_change_kg:
                    # Calculate calorie surplus for weight gain
                    weekly_calorie_surplus = weekly_weight_change_kg * Decimal("7700")  # Cal per kg
                    daily_surplus = weekly_calorie_surplus / 7
                    daily_target = metabolic_profile.tdee_calories + daily_surplus
                else:
                    # Maintain weight
                    daily_target = metabolic_profile.tdee_calories
            else:
                # Fallback to default if no user metrics provided
                daily_target = Decimal("2000")  # Default calorie target
            
            # Create goal entity
            from datetime import datetime, timedelta
            
            # Calculate end_date using extracted method
            calculated_end_date = self._calculate_end_date(
                target_date, target_weight_kg, user_weight_kg, weekly_weight_change_kg
            )
            
            goal = CalorieGoal(
                id=uuid4(),
                user_id=user_uuid,  # Use UUID for domain entity
                goal_type=goal_type,
                daily_calorie_target=daily_target,
                daily_deficit_target=daily_target - Decimal("2000") if goal_type == GoalType.WEIGHT_LOSS else None,
                weekly_weight_change_kg=weekly_weight_change_kg or Decimal("0"),
                start_date=date.today(),
                end_date=calculated_end_date,
                is_active=True,
                ai_optimized=bool(all([user_weight_kg, user_height_cm, user_age, user_gender])),
                optimization_metadata={
                    "method": "parameter_passing_pattern",
                    "user_metrics_provided": bool(all([user_weight_kg, user_height_cm, user_age, user_gender])),
                    "custom_target": bool(custom_calorie_target)
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return await self.goal_repo.create(goal)
            
        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            raise
    
    async def get_user_goals(self, user_id: str, active_only: bool = True) -> List[CalorieGoal]:
        """Get all goals for user."""
        try:
            # Convert user_id to UUID for repository compatibility
            from uuid import UUID
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                # Generate same deterministic UUID as create_goal
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()
                formatted_hash = (
                    f"{user_hash[:8]}-{user_hash[8:12]}-"
                    f"{user_hash[12:16]}-{user_hash[16:20]}-{user_hash[20:32]}"
                )
                user_uuid = UUID(formatted_hash)
            
            if active_only:
                active_goal = await self.goal_repo.get_active_goal(user_uuid)
                return [active_goal] if active_goal else []
            else:
                # This would require a new repository method
                # For now, return active goal only
                active_goal = await self.goal_repo.get_active_goal(user_uuid)
                return [active_goal] if active_goal else []
                
        except Exception as e:
            logger.error(f"Failed to get user goals: {e}")
            raise
    
    async def get_active_goal(self, user_id: str) -> Optional[CalorieGoal]:
        """Get user's currently active goal."""
        try:
            # Convert user_id to UUID for repository compatibility
            from uuid import UUID
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                # Generate same deterministic UUID as create_goal
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()
                formatted_hash = (
                    f"{user_hash[:8]}-{user_hash[8:12]}-"
                    f"{user_hash[12:16]}-{user_hash[16:20]}-{user_hash[20:32]}"
                )
                user_uuid = UUID(formatted_hash)
            
            return await self.goal_repo.get_active_goal(user_uuid)
            
        except Exception as e:
            logger.error(f"Failed to get active goal for {user_id}: {e}")
            raise
    
    def _calculate_end_date(
        self, 
        target_date: Optional[DateType], 
        target_weight_kg: Optional[Decimal],
        user_weight_kg: Optional[Decimal], 
        weekly_weight_change_kg: Optional[Decimal]
    ) -> Optional[DateType]:
        """Calculate end_date based on weight targets and weekly change rate."""
        if target_date:
            return target_date
            
        if target_weight_kg and user_weight_kg and weekly_weight_change_kg:
            logger.info("All parameters present for end_date calculation")
            # Calculate weeks needed to reach target
            weight_diff = abs(float(user_weight_kg) - float(target_weight_kg))
            weeks_needed = weight_diff / abs(float(weekly_weight_change_kg))
            
            logger.info(f"Weight difference: {weight_diff} kg, Weeks needed: {weeks_needed}")
            
            # Calculate end date
            calculated_end_date = date.today() + timedelta(weeks=int(weeks_needed))
            logger.info(f"Calculated end_date: {calculated_end_date}")
            return calculated_end_date
        elif target_weight_kg:
            logger.info("Missing user_weight_kg or weekly_weight_change_kg for end_date calculation")
        else:
            logger.info(f"Using provided target_date: {target_date} or no target_weight_kg: {target_weight_kg}")
        
        return None

    async def get_current_goal(self, user_id: str) -> Optional[CalorieGoal]:
        """Get current active goal for user - alias for get_active_goal."""
        return await self.get_active_goal(user_id)

    async def update_goal(
        self, 
        goal_id: str, 
        user_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[CalorieGoal]:
        """Update an existing calorie goal with provided changes."""
        try:
            # Get all user goals and find the specific one
            all_goals = await self.goal_repo.get_user_goals(user_id, include_inactive=True)
            current_goal = next((goal for goal in all_goals if str(goal.id) == goal_id), None)
            
            if not current_goal:
                logger.error(f"Goal {goal_id} not found for user {user_id}")
                return None
            
            # Recalculate end_date if weight-related parameters change
            # For update, we need to extract current parameters and apply updates
            target_weight_kg = None  # Not stored in goal, would need to be passed
            user_weight_kg = None    # Not stored in goal, would need to be passed
            weekly_weight_change_kg = updates.get('weekly_weight_change_kg', current_goal.weekly_weight_change_kg)
            
            # Use current end_date if no recalculation needed
            end_date = updates.get('end_date', current_goal.end_date)
            
            # Apply updates
            updated_goal = CalorieGoal(
                id=current_goal.id,
                user_id=current_goal.user_id,
                goal_type=GoalType(updates.get('goal_type', current_goal.goal_type.value)) if 'goal_type' in updates else current_goal.goal_type,
                daily_calorie_target=Decimal(str(updates.get('daily_calorie_target', current_goal.daily_calorie_target))),
                daily_deficit_target=Decimal(str(updates.get('daily_deficit_target', current_goal.daily_deficit_target))),
                weekly_weight_change_kg=Decimal(str(weekly_weight_change_kg)),
                start_date=current_goal.start_date,
                end_date=end_date,
                is_active=updates.get('is_active', current_goal.is_active),
                ai_optimized=current_goal.ai_optimized,
                optimization_metadata=current_goal.optimization_metadata,
                created_at=current_goal.created_at,
                updated_at=datetime.utcnow()
            )
            
            return await self.goal_repo.update(updated_goal)
            
        except Exception as e:
            logger.error(f"Failed to update goal {goal_id}: {e}")
            raise
    
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
        profile_repo: IMetabolicProfileRepository
    ):
        self.profile_repo = profile_repo
    
    async def calculate_bmr_mifflin(
        self,
        weight_kg: Decimal,
        height_cm: Decimal,
        age: int,
        gender: GenderType
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
    
    async def calculate_metabolic_profile(
        self,
        user_id: UUID,
        weight_kg: Decimal,
        height_cm: Decimal,
        age: int,
        gender: GenderType,
        activity_level: ActivityLevel
    ) -> MetabolicProfile:
        """
        Calculate metabolic profile with user data passed as parameters.
        
        This implements the Parameter Passing pattern for microservice
        decoupling:
        - User metrics provided by client/orchestrator (N8N, mobile app)
        - No direct access to user-management service
        - Ensures reusability and clean architecture
        """
        try:
            # Calculate BMR using Mifflin-St Jeor equation
            bmr = await self.calculate_bmr_mifflin(
                weight_kg, height_cm, age, gender
            )
            
            # Calculate TDEE from BMR and activity level
            tdee = await self.calculate_tdee(bmr, activity_level)
            
            # Create metabolic profile with NEW entity structure
            # Use database schema fields only
            profile = MetabolicProfile(
                id=uuid4(),
                user_id=user_id,
                calculated_at=datetime.utcnow(),
                bmr_calories=bmr,
                tdee_calories=tdee,
                rmr_calories=bmr * Decimal("1.05"),  # RMR typically 5% higher than BMR
                calculation_method="mifflin_st_jeor",
                accuracy_score=Decimal("0.85"),
                
                # Activity level and multipliers
                activity_level=activity_level.value,  # Convert enum to string
                sedentary_multiplier=Decimal("1.2"),
                light_multiplier=Decimal("1.375"),
                moderate_multiplier=Decimal("1.55"),
                high_multiplier=Decimal("1.725"),
                extreme_multiplier=Decimal("1.9"),
                
                # AI fields
                ai_adjusted=False,
                adjustment_factor=Decimal("1.0"),
                learning_iterations=0,
                
                # Timestamps and status (only DB fields)
                expires_at=datetime.utcnow() + timedelta(days=30),
                is_active=True
                # No created_at, updated_at - not in DB schema
            )
            
            # Save to repository
            await self.profile_repo.create(profile)
            
            # DEBUG: Check what we get back
            print(f"DEBUG: Profile after create - rmr_calories: {profile.rmr_calories}")
            print(f"DEBUG: Profile type: {type(profile)}")
            
            logger.info(
                f"Metabolic profile calculated for user {user_id}: "
                f"BMR={bmr}, TDEE={tdee}"
            )
            return profile
            
        except Exception as e:
            logger.error(
                f"Failed to calculate metabolic profile for user {user_id}: {e}"
            )
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
    """📈 TIMELINE ANALYTICS SERVICE - Mobile dashboard optimization."""
    
    def __init__(
        self,
        analytics_repo: ITemporalAnalyticsRepository,
        event_repo: ICalorieEventRepository,
        balance_repo: IDailyBalanceRepository
    ):
        self.analytics_repo = analytics_repo
        self.event_repo = event_repo
        self.balance_repo = balance_repo
    
    async def get_hourly_analytics(
        self,
        user_id: str,
        date: DateType,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Get hourly analytics using pre-computed temporal views."""
        try:
            # Use hourly_calorie_summary view
            return await self.analytics_repo.get_hourly_summary(
                user_id=user_id,
                target_date=date,
                hours_back=hours_back
            )
        except Exception as e:
            logger.error(f"Failed to get hourly analytics: {e}")
            raise
    
    async def get_daily_analytics(
        self,
        user_id: str,
        start_date: DateType,
        end_date: DateType,
        include_trends: bool = True
    ) -> List[Dict[str, Any]]:
        """Get daily analytics with trend calculations."""
        try:
            daily_data = await self.analytics_repo.get_daily_summary(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if include_trends:
                # Add trend calculations
                for i, day in enumerate(daily_data):
                    if i > 0:
                        prev_day = daily_data[i-1]
                        day['trend_direction'] = self._calculate_trend(
                            day['net_calories'], prev_day['net_calories']
                        )
            
            return daily_data
        except Exception as e:
            logger.error(f"Failed to get daily analytics: {e}")
            raise
    
    async def get_weekly_analytics(
        self,
        user_id: str,
        weeks_back: int = 12,
        include_patterns: bool = True
    ) -> List[Dict[str, Any]]:
        """Get weekly analytics with pattern recognition."""
        try:
            weekly_data = await self.analytics_repo.get_weekly_summary(
                user_id=user_id,
                weeks_back=weeks_back
            )
            
            if include_patterns:
                # Add weekday pattern analysis
                for week in weekly_data:
                    week['weekday_patterns'] = await self._analyze_weekday_patterns(
                        user_id, week['week_start'], week['week_end']
                    )
            
            return weekly_data
        except Exception as e:
            logger.error(f"Failed to get weekly analytics: {e}")
            raise
    
    async def get_monthly_analytics(
        self,
        user_id: str,
        months_back: int = 12,
        include_yearly_trends: bool = True
    ) -> List[Dict[str, Any]]:
        """Get monthly analytics with long-term trends."""
        try:
            monthly_data = await self.analytics_repo.get_monthly_summary(
                user_id=user_id,
                months_back=months_back
            )
            
            if include_yearly_trends:
                # Add seasonal analysis
                for month in monthly_data:
                    month['seasonal_factor'] = self._calculate_seasonal_factor(
                        month['month']
                    )
            
            return monthly_data
        except Exception as e:
            logger.error(f"Failed to get monthly analytics: {e}")
            raise
    
    async def get_balance_timeline(
        self,
        user_id: str,
        period: str = "week",
        include_goals: bool = True
    ) -> List[Dict[str, Any]]:
        """Get calorie balance timeline with goal tracking."""
        try:
            # Determine date range based on period
            end_date = DateType.today()
            if period == "day":
                start_date = end_date - timedelta(days=1)
            elif period == "week":
                start_date = end_date - timedelta(weeks=1)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "quarter":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(weeks=1)
            
            balance_data = await self.balance_repo.get_balance_timeline(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if include_goals:
                # Enrich with goal data
                goal_service = CalorieGoalService(None, None)  # TODO: Proper DI
                for point in balance_data:
                    point['goal_data'] = await goal_service.get_goal_for_date(
                        user_id, point.get('date', end_date)
                    )
            
            return balance_data
        except Exception as e:
            logger.error(f"Failed to get balance timeline: {e}")
            raise
    
    async def get_intraday_analytics(
        self,
        user_id: str,
        date: DateType,
        resolution_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """Get high-resolution intraday analytics."""
        try:
            # Generate time slots based on resolution
            time_slots = []
            current_time = datetime.combine(date, datetime.min.time())
            end_time = current_time + timedelta(days=1)
            
            while current_time < end_time:
                slot_end = current_time + timedelta(minutes=resolution_minutes)
                
                # Get events for this time slot
                slot_events = await self.event_repo.get_events_by_time_range(
                    user_id=user_id,
                    start_time=current_time,
                    end_time=slot_end
                )
                
                # Calculate slot metrics
                calories_consumed = sum(
                    e.value for e in slot_events 
                    if e.event_type == EventType.CONSUMED
                )
                calories_burned = sum(
                    e.value for e in slot_events 
                    if e.event_type in [EventType.BURNED_EXERCISE, EventType.BURNED_BMR]
                )
                
                time_slots.append({
                    'time_slot': current_time.strftime('%H:%M'),
                    'calories_consumed': calories_consumed,
                    'calories_burned': calories_burned,
                    'cumulative_balance': calories_consumed - calories_burned,
                    'activity_intensity': self._calculate_activity_intensity(slot_events)
                })
                
                current_time = slot_end
            
            return time_slots
        except Exception as e:
            logger.error(f"Failed to get intraday analytics: {e}")
            raise
    
    async def get_pattern_analytics(
        self,
        user_id: str,
        analysis_type: str = "behavioral",
        lookback_days: int = 90,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get behavioral pattern analytics with AI insights."""
        try:
            patterns = []
            
            if analysis_type == "behavioral":
                patterns.extend(await self._detect_eating_patterns(user_id, lookback_days))
            elif analysis_type == "seasonal":
                patterns.extend(await self._detect_seasonal_patterns(user_id, lookback_days))
            elif analysis_type == "weekly":
                patterns.extend(await self._detect_weekly_patterns(user_id, lookback_days))
            elif analysis_type == "daily":
                patterns.extend(await self._detect_daily_patterns(user_id, lookback_days))
            
            # Filter by confidence threshold
            return [p for p in patterns if p.get('confidence_score', 0) >= min_confidence]
            
        except Exception as e:
            logger.error(f"Failed to get pattern analytics: {e}")
            raise
    
    async def generate_real_time_analytics(
        self,
        user_id: str,
        recent_events: List[CalorieEvent],
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """Generate real-time metrics for live dashboard."""
        try:
            today = DateType.today()
            
            # Get today's balance
            today_balance = await self.balance_repo.get_daily_balance(user_id, today)
            
            # Calculate current metrics
            current_balance = today_balance.net_calories if today_balance else Decimal("0")
            
            # Calculate rates from recent events (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_events_filtered = [
                e for e in recent_events 
                if e.event_timestamp >= one_hour_ago
            ]
            
            consumed_last_hour = sum(
                e.value for e in recent_events_filtered 
                if e.event_type == EventType.CONSUMED
            )
            burned_last_hour = sum(
                e.value for e in recent_events_filtered 
                if e.event_type in [EventType.BURNED_EXERCISE, EventType.BURNED_BMR]
            )
            
            metrics = {
                'current_balance': current_balance,
                'burn_rate_per_hour': burned_last_hour,
                'consumption_rate_per_hour': consumed_last_hour,
            }
            
            if include_predictions:
                # Add predictions
                metrics.update(await self._generate_predictions(user_id, current_balance))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to generate real-time analytics: {e}")
            raise
    
    async def export_timeline_data(
        self,
        user_id: str,
        format: str = "json",
        start_date: DateType = None,
        end_date: DateType = None,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """Export timeline data for external analysis."""
        try:
            # Get data based on granularity
            if granularity == "hourly":
                data = await self.analytics_repo.get_hourly_export(
                    user_id, start_date, end_date
                )
            elif granularity == "daily":
                data = await self.analytics_repo.get_daily_export(
                    user_id, start_date, end_date
                )
            elif granularity == "weekly":
                data = await self.analytics_repo.get_weekly_export(
                    user_id, start_date, end_date
                )
            else:
                data = []
            
            # Format data based on format
            if format == "json":
                export_data = data
            elif format == "csv":
                export_data = self._convert_to_csv(data)
            elif format == "xlsx":
                export_data = self._convert_to_xlsx(data)
            else:
                export_data = data
            
            return {
                'export_format': format,
                'inline_data': export_data,
                'record_count': len(data),
                'export_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to export timeline data: {e}")
            raise
    
    # Private helper methods
    def _calculate_trend(self, current: Decimal, previous: Decimal) -> str:
        """Calculate trend direction."""
        if current > previous:
            return "increasing"
        elif current < previous:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_seasonal_factor(self, month: int) -> Decimal:
        """Calculate seasonal adjustment factor."""
        # Simple seasonal adjustment - could be more sophisticated
        seasonal_factors = {
            12: Decimal("1.1"), 1: Decimal("1.1"), 2: Decimal("1.05"),  # Winter
            3: Decimal("1.0"), 4: Decimal("0.95"), 5: Decimal("0.95"),   # Spring
            6: Decimal("0.9"), 7: Decimal("0.9"), 8: Decimal("0.9"),     # Summer
            9: Decimal("0.95"), 10: Decimal("1.0"), 11: Decimal("1.05")  # Fall
        }
        return seasonal_factors.get(month, Decimal("1.0"))
    
    def _calculate_activity_intensity(self, events: List[CalorieEvent]) -> str:
        """Calculate activity intensity for time slot."""
        total_activity = sum(
            e.value for e in events 
            if e.event_type == EventType.BURNED_EXERCISE
        )
        
        if total_activity > 200:
            return "high"
        elif total_activity > 100:
            return "moderate"
        elif total_activity > 50:
            return "light"
        else:
            return "minimal"
    
    async def _analyze_weekday_patterns(
        self, user_id: str, start_date: DateType, end_date: DateType
    ) -> Dict[str, Decimal]:
        """Analyze weekday eating patterns."""
        # This would analyze patterns by weekday
        # Return placeholder data for now
        return {
            "monday": Decimal("2000"),
            "tuesday": Decimal("1950"),
            "wednesday": Decimal("2100"),
            "thursday": Decimal("2050"),
            "friday": Decimal("2200"),
            "saturday": Decimal("2300"),
            "sunday": Decimal("2100")
        }
    
    async def _detect_eating_patterns(
        self, user_id: str, lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect eating behavior patterns."""
        # Placeholder pattern detection
        return [{
            'pattern_id': 'late_night_eating',
            'pattern_type': 'behavioral',
            'description': 'Tendency to consume calories after 9 PM',
            'confidence_score': Decimal("0.85"),
            'frequency': 'daily',
            'impact_score': Decimal("0.3"),
            'recommendations': ['Try to finish eating by 8 PM']
        }]
    
    async def _detect_seasonal_patterns(
        self, user_id: str, lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect seasonal eating patterns."""
        return []
    
    async def _detect_weekly_patterns(
        self, user_id: str, lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect weekly eating patterns."""
        return []
    
    async def _detect_daily_patterns(
        self, user_id: str, lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect daily eating patterns."""
        return []
    
    async def _generate_predictions(
        self, user_id: str, current_balance: Decimal
    ) -> Dict[str, Any]:
        """Generate predictions for end of day."""
        # Simple prediction logic - could be ML-based
        return {
            'projected_end_of_day': current_balance + Decimal("500"),
            'calories_remaining': Decimal("300"),
            'goal_achievement_probability': Decimal("0.75"),
            'next_meal_recommendation': 'Light protein-rich meal'
        }
    
    def _convert_to_csv(self, data: List[Dict]) -> str:
        """Convert data to CSV format."""
        # Placeholder CSV conversion
        return "date,calories_consumed,calories_burned,net_calories\n"
    
    def _convert_to_xlsx(self, data: List[Dict]) -> str:
        """Convert data to XLSX format."""
        # Placeholder XLSX conversion
        return "XLSX_DATA_PLACEHOLDER"
    
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
