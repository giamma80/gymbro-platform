"""
Business Logic Services for Analytics Service
Following GymBro template - Domain-Driven Design
Enhanced with HealthKit integration
"""

from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any

from app.models import (
    DailyStatsRecord,
    TimeRangeStats,
    UserDashboard,
    TimeRangeType,
    TrendDirection,
    ActivityIntensity,
    DashboardFilters,
    DateRangeFilter
)
from app.enhanced_analytics import enhanced_analytics_service


class AnalyticsService:
    """
    Main analytics service implementing business logic
    Following Domain-Driven Design principles
    """
    
    def __init__(self):
        """Initialize analytics service"""
        # Database session would be injected here
        # self.db = db_session
        pass
    
    async def get_daily_stats(
        self,
        user_id: str,
        date_range: Optional[DateRangeFilter] = None,
        time_range: Optional[TimeRangeType] = None
    ) -> List[DailyStatsRecord]:
        """Get daily statistics for user"""
        
        # Determine date range
        if time_range:
            start_date, end_date = self._get_date_range(time_range)
        elif date_range:
            start_date, end_date = date_range.start_date, date_range.end_date
        else:
            # Default: last 30 days
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        
        # Mock data for now - replace with database query
        return self._generate_mock_daily_stats(user_id, start_date, end_date)
    
    async def get_time_range_stats(
        self,
        user_id: str,
        time_range: TimeRangeType,
        reference_date: Optional[date] = None
    ) -> TimeRangeStats:
        """Get aggregated statistics for time range"""
        
        start_date, end_date = self._get_date_range(time_range, reference_date)
        
        # Get daily records
        daily_records = await self.get_daily_stats(
            user_id=user_id,
            date_range=DateRangeFilter(start_date=start_date, end_date=end_date)
        )
        
        # Aggregate statistics
        return self._aggregate_daily_records(
            daily_records, time_range, start_date, end_date
        )
    
    async def generate_dashboard(
        self,
        user_id: str,
        filters: Optional[DashboardFilters] = None
    ) -> UserDashboard:
        """Generate complete user dashboard"""
        
        # Get historical data (90 days for comprehensive dashboard)
        daily_records = await self.get_daily_stats(
            user_id=user_id,
            date_range=DateRangeFilter(
                start_date=date.today() - timedelta(days=90),
                end_date=date.today()
            )
        )
        
        # Calculate current streak
        current_streak = self._calculate_current_streak(daily_records)
        
        # Generate all timeframe statistics
        today_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.TODAY
        )
        yesterday_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.YESTERDAY
        )
        this_week_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.WEEK
        )
        
        # Last week (reference date = 7 days ago)
        last_week_ref_date = date.today() - timedelta(days=7)
        last_week_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.WEEK, last_week_ref_date
        )
        
        this_month_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.MONTH
        )
        
        # Last month
        last_month_date = date.today().replace(day=1) - timedelta(days=1)
        last_month_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.MONTH, last_month_date
        )
        
        this_year_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.YEAR
        )
        all_time_stats = await self.get_time_range_stats(
            user_id, TimeRangeType.ALL_TIME
        )
        
        # Calculate performance indicators
        weekly_goal_progress = min(this_week_stats.activity_percentage * 100, 100)
        monthly_goal_progress = min(this_month_stats.activity_percentage * 100, 100)
        consistency_score = self._calculate_consistency_score(daily_records)
        improvement_score = self._calculate_improvement_score(
            this_week_stats, last_week_stats
        )
        
        return UserDashboard(
            user_id=user_id,
            generated_at=datetime.now(),
            current_weight_kg=75.5,  # Mock - would come from latest record
            current_bmi=22.8,  # Mock - calculated from height/weight
            current_streak=current_streak,
            today=today_stats,
            yesterday=yesterday_stats,
            this_week=this_week_stats,
            last_week=last_week_stats,
            this_month=this_month_stats,
            last_month=last_month_stats,
            this_year=this_year_stats,
            all_time=all_time_stats,
            weekly_goal_progress=weekly_goal_progress,
            monthly_goal_progress=monthly_goal_progress,
            consistency_score=consistency_score,
            improvement_score=improvement_score
        )
    
    async def get_enhanced_dashboard(
        self,
        user_id: str,
        filters: Optional[DashboardFilters] = None
    ) -> Dict[str, Any]:
        """Get enhanced dashboard with HealthKit analytics integration"""
        return await enhanced_analytics_service.get_enhanced_user_dashboard(
            user_id=user_id,
            filters=filters
        )
    
    async def get_trends_analysis(
        self,
        user_id: str,
        metric: str,
        days: int
    ) -> List[DailyStatsRecord]:
        """Get trends analysis for specific metric"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        return await self.get_daily_stats(
            user_id=user_id,
            date_range=DateRangeFilter(start_date=start_date, end_date=end_date)
        )
    
    async def record_daily_stats(
        self,
        user_id: str,
        date: date,
        calories_burned: float,
        calories_consumed: float,
        active_minutes: int,
        steps_count: int,
        workouts_completed: int = 0,
        weight_kg: Optional[float] = None,
        sleep_hours: Optional[float] = None
    ) -> DailyStatsRecord:
        """Record or update daily statistics"""
        
        # Calculate derived fields
        calories_deficit = calories_burned - calories_consumed
        
        # Determine activity intensity
        if active_minutes >= 120:
            intensity = ActivityIntensity.VERY_HIGH
        elif active_minutes >= 60:
            intensity = ActivityIntensity.HIGH
        elif active_minutes >= 30:
            intensity = ActivityIntensity.MODERATE
        else:
            intensity = ActivityIntensity.LOW
        
        # Calculate data completeness
        completeness_fields = [
            calories_burned > 0,
            calories_consumed > 0,
            active_minutes >= 0,
            steps_count > 0,
            weight_kg is not None,
            sleep_hours is not None
        ]
        data_completeness = sum(completeness_fields) / len(completeness_fields)
        
        record = DailyStatsRecord(
            user_id=user_id,
            date=date,
            calories_burned=calories_burned,
            calories_consumed=calories_consumed,
            calories_deficit=calories_deficit,
            active_minutes=active_minutes,
            steps_count=steps_count,
            workouts_completed=workouts_completed,
            activity_intensity=intensity,
            weight_kg=weight_kg,
            sleep_hours=sleep_hours,
            data_completeness=data_completeness,
            is_active_day=active_minutes >= 30,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # In real implementation: save to database
        # await self.db.save(record)
        
        return record
    
    # ===== PRIVATE HELPER METHODS =====
    
    def _get_date_range(
        self, 
        time_range: TimeRangeType, 
        reference_date: Optional[date] = None
    ) -> tuple[date, date]:
        """Calculate date range for TimeRangeType"""
        
        if reference_date is None:
            reference_date = date.today()
            
        if time_range == TimeRangeType.TODAY:
            return reference_date, reference_date
        elif time_range == TimeRangeType.YESTERDAY:
            yesterday = reference_date - timedelta(days=1)
            return yesterday, yesterday
        elif time_range == TimeRangeType.WEEK:
            # Current week (Monday-Sunday)
            start = reference_date - timedelta(days=reference_date.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif time_range == TimeRangeType.MONTH:
            # Current month
            start = reference_date.replace(day=1)
            if reference_date.month == 12:
                end = date(reference_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                next_month = reference_date.replace(month=reference_date.month + 1, day=1)
                end = next_month - timedelta(days=1)
            return start, end
        elif time_range == TimeRangeType.YEAR:
            # Current year
            start = reference_date.replace(month=1, day=1)
            end = reference_date.replace(month=12, day=31)
            return start, end
        elif time_range == TimeRangeType.ALL_TIME:
            # From 2020 to today
            start = date(2020, 1, 1)
            end = reference_date
            return start, end
        else:
            # Default: last week
            return reference_date - timedelta(days=7), reference_date
    
    def _aggregate_daily_records(
        self,
        daily_records: List[DailyStatsRecord],
        time_range: TimeRangeType,
        start_date: date,
        end_date: date
    ) -> TimeRangeStats:
        """Aggregate daily records into time range statistics"""
        
        if not daily_records:
            return self._empty_stats(time_range, start_date, end_date)
        
        # Basic calculations
        total_days = (end_date - start_date).days + 1
        days_with_data = len(daily_records)
        active_days = sum(1 for r in daily_records if r.is_active_day)
        
        # Calorie aggregations
        total_calories_burned = sum(r.calories_burned for r in daily_records)
        total_calories_consumed = sum(r.calories_consumed for r in daily_records)
        
        # Activity aggregations
        total_active_minutes = sum(r.active_minutes for r in daily_records)
        total_steps = sum(r.steps_count for r in daily_records)
        total_workouts = sum(r.workouts_completed for r in daily_records)
        
        # Averages
        avg_daily_calories_burned = total_calories_burned / days_with_data if days_with_data > 0 else 0
        avg_daily_calories_consumed = total_calories_consumed / days_with_data if days_with_data > 0 else 0
        avg_daily_deficit = avg_daily_calories_burned - avg_daily_calories_consumed
        avg_daily_steps = total_steps / days_with_data if days_with_data > 0 else 0
        
        # Weight tracking
        weight_records = [r for r in daily_records if r.weight_kg is not None]
        weight_start_kg = None
        weight_end_kg = None
        weight_change_kg = None
        
        if weight_records:
            sorted_weight = sorted(weight_records, key=lambda x: x.date)
            weight_start_kg = sorted_weight[0].weight_kg
            weight_end_kg = sorted_weight[-1].weight_kg
            weight_change_kg = weight_end_kg - weight_start_kg
        
        # Sleep average
        sleep_records = [r for r in daily_records if r.sleep_hours is not None]
        avg_sleep_hours = sum(r.sleep_hours for r in sleep_records) / len(sleep_records) if sleep_records else None
        
        # Trends (simplified)
        calories_trend = self._calculate_trend([r.calories_burned for r in daily_records[-7:]])
        activity_trend = self._calculate_trend([r.active_minutes for r in daily_records[-7:]])
        weight_trend = self._calculate_weight_trend(weight_records)
        
        # Data completeness
        avg_completeness = sum(r.data_completeness for r in daily_records) / days_with_data if days_with_data > 0 else 0
        
        return TimeRangeStats(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_calories_burned=total_calories_burned,
            total_calories_consumed=total_calories_consumed,
            avg_daily_calories_burned=avg_daily_calories_burned,
            avg_daily_calories_consumed=avg_daily_calories_consumed,
            avg_daily_deficit=avg_daily_deficit,
            total_active_minutes=total_active_minutes,
            total_steps=total_steps,
            total_workouts=total_workouts,
            active_days_count=active_days,
            activity_percentage=active_days / total_days if total_days > 0 else 0,
            avg_daily_steps=avg_daily_steps,
            weight_start_kg=weight_start_kg,
            weight_end_kg=weight_end_kg,
            weight_change_kg=weight_change_kg,
            avg_sleep_hours=avg_sleep_hours,
            calories_trend=calories_trend,
            weight_trend=weight_trend,
            activity_trend=activity_trend,
            data_completeness=avg_completeness,
            days_with_data=days_with_data
        )
    
    def _empty_stats(
        self, 
        time_range: TimeRangeType, 
        start_date: date, 
        end_date: date
    ) -> TimeRangeStats:
        """Create empty statistics for period with no data"""
        
        total_days = (end_date - start_date).days + 1
        
        return TimeRangeStats(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            calories_trend=TrendDirection.NO_DATA,
            weight_trend=TrendDirection.NO_DATA,
            activity_trend=TrendDirection.NO_DATA
        )
    
    def _calculate_trend(self, values: List[float]) -> TrendDirection:
        """Calculate simple trend from values"""
        
        if len(values) < 2:
            return TrendDirection.NO_DATA
        
        # Simple trend: compare first half with second half
        mid = len(values) // 2
        first_half = sum(values[:mid]) / mid if mid > 0 else 0
        second_half = sum(values[mid:]) / (len(values) - mid)
        
        if first_half == 0:
            return TrendDirection.NO_DATA
        
        change_percentage = (second_half - first_half) / first_half
        
        if change_percentage > 0.1:  # +10%
            return TrendDirection.UP
        elif change_percentage < -0.1:  # -10%
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE
    
    def _calculate_weight_trend(self, weight_records: List[DailyStatsRecord]) -> TrendDirection:
        """Calculate weight-specific trend"""
        
        if len(weight_records) < 2:
            return TrendDirection.NO_DATA
        
        sorted_records = sorted(weight_records, key=lambda x: x.date)
        start_weight = sorted_records[0].weight_kg
        end_weight = sorted_records[-1].weight_kg
        
        change_percentage = (end_weight - start_weight) / start_weight * 100
        
        if change_percentage > 1:  # +1%
            return TrendDirection.UP
        elif change_percentage < -1:  # -1%
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE
    
    def _calculate_current_streak(self, daily_records: List[DailyStatsRecord]) -> int:
        """Calculate current active days streak"""
        
        if not daily_records:
            return 0
        
        # Sort by date descending
        sorted_records = sorted(daily_records, key=lambda x: x.date, reverse=True)
        
        streak = 0
        current_date = date.today()
        
        for record in sorted_records:
            if record.date == current_date and record.is_active_day:
                streak += 1
                current_date -= timedelta(days=1)
            elif record.date < current_date:
                break  # Gap in data - streak ends
        
        return streak
    
    def _calculate_consistency_score(self, daily_records: List[DailyStatsRecord]) -> float:
        """Calculate consistency score (last 30 days)"""
        
        last_30_days = [
            r for r in daily_records 
            if r.date >= date.today() - timedelta(days=30)
        ]
        
        if len(last_30_days) < 10:  # Insufficient data
            return 0.0
        
        active_days = sum(1 for r in last_30_days if r.is_active_day)
        return min((active_days / 30) * 100, 100)
    
    def _calculate_improvement_score(
        self, 
        this_week: TimeRangeStats, 
        last_week: TimeRangeStats
    ) -> float:
        """Calculate improvement score comparing weeks"""
        
        if last_week.days_with_data == 0:
            return 50.0  # Neutral score without historical data
        
        # Compare key metrics
        calorie_improvement = 0
        if last_week.avg_daily_calories_burned > 0:
            calorie_improvement = (
                (this_week.avg_daily_calories_burned - last_week.avg_daily_calories_burned) /
                last_week.avg_daily_calories_burned * 100
            )
        
        activity_improvement = 0
        if last_week.activity_percentage > 0:
            activity_improvement = (
                (this_week.activity_percentage - last_week.activity_percentage) /
                last_week.activity_percentage * 100
            )
        
        # Average improvement
        improvement = (calorie_improvement + activity_improvement) / 2
        
        # Normalize to 0-100
        return max(0, min(100, 50 + improvement))
    
    def _generate_mock_daily_stats(
        self, 
        user_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[DailyStatsRecord]:
        """Generate mock data for testing - REMOVE IN PRODUCTION"""
        
        import random
        
        records = []
        current_date = start_date
        base_weight = 75.0
        
        while current_date <= end_date:
            # Simulate realistic variability
            is_active = random.random() > 0.2  # 80% active days
            
            calories_burned = random.uniform(1800, 2500) if is_active else random.uniform(1500, 1900)
            calories_consumed = random.uniform(1600, 2200)
            active_minutes = random.randint(30, 120) if is_active else random.randint(0, 30)
            steps = random.randint(6000, 12000) if is_active else random.randint(2000, 6000)
            
            # Simulate gradual weight loss
            days_elapsed = (current_date - start_date).days
            weight_trend = -0.05  # Losing 0.05kg per day
            weight_variation = random.uniform(-0.2, 0.1)
            current_weight = base_weight + (days_elapsed * weight_trend) + weight_variation
            
            record = DailyStatsRecord(
                user_id=user_id,
                date=current_date,
                calories_burned=calories_burned,
                calories_consumed=calories_consumed,
                calories_deficit=calories_burned - calories_consumed,
                active_minutes=active_minutes,
                steps_count=steps,
                workouts_completed=1 if is_active and random.random() > 0.5 else 0,
                activity_intensity=ActivityIntensity.MODERATE if is_active else ActivityIntensity.LOW,
                weight_kg=current_weight,
                sleep_hours=random.uniform(6.5, 8.5) if random.random() > 0.3 else None,
                data_completeness=random.uniform(0.7, 1.0),
                is_active_day=is_active,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            records.append(record)
            current_date += timedelta(days=1)
        
        return records
