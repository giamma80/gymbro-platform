from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from ..domain import (
    User, MetabolicProfile,
    UserRepository, MetabolicProfileRepository,
    MetabolicCalculationService
)
from ..core.interfaces import UnitOfWork


class MetabolicProfileService:
    """Application service for metabolic profile management"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        profile_repo: MetabolicProfileRepository,
        metabolic_service: MetabolicCalculationService,
        uow: UnitOfWork
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.metabolic_service = metabolic_service
        self.uow = uow
    
    async def ensure_current_profile(self, user_id: UUID) -> Optional[MetabolicProfile]:
        """Ensure user has a current valid metabolic profile"""
        async with self.uow:
            # Get current profile
            current_profile = await self.profile_repo.get_current_by_user(user_id)
            
            # Get user data
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Check if we need to create/update profile
            needs_calculation = (
                not current_profile or
                not current_profile.is_valid() or
                self.metabolic_service.should_recalculate_profile(current_profile, user)
            )
            
            if needs_calculation:
                # Create new profile
                new_profile = MetabolicProfile.create_from_user(user)
                if new_profile:
                    created_profile = await self.profile_repo.create(new_profile)
                    await self.uow.commit()
                    return created_profile
            
            return current_profile
    
    async def recalculate_all_profiles(self) -> Dict[str, int]:
        """Recalculate all user profiles (maintenance task)"""
        # This would typically be called by a background job
        async with self.uow:
            # Get all users (implement pagination for large datasets)
            users = await self.user_repo.get_all(limit=1000)
            
            updated_count = 0
            error_count = 0
            
            for user in users:
                try:
                    await self.ensure_current_profile(user.id)
                    updated_count += 1
                except Exception:
                    error_count += 1
            
            # Clean up expired profiles
            deleted_count = await self.profile_repo.delete_expired_profiles()
            
            await self.uow.commit()
            
            return {
                "updated": updated_count,
                "errors": error_count,
                "deleted": deleted_count
            }


class AnalyticsService:
    """Application service for analytics and insights"""
    
    def __init__(
        self,
        balance_repo,
        goal_repo,
        user_repo
    ):
        self.balance_repo = balance_repo
        self.goal_repo = goal_repo
        self.user_repo = user_repo
    
    async def get_user_dashboard(self, user_id: UUID) -> Dict[str, Any]:
        """Get dashboard data for user"""
        # Get current goal
        current_goal = await self.goal_repo.get_active_goal_by_user(user_id)
        
        # Get recent balances (last 30 days)
        recent_balances = await self.balance_repo.get_latest_by_user(user_id, limit=30)
        
        # Calculate summary metrics
        if recent_balances:
            avg_calories_consumed = sum(b.calories_consumed for b in recent_balances) / len(recent_balances)
            avg_net_calories = sum(b.net_calories for b in recent_balances) / len(recent_balances)
            
            # Weight trend
            weight_entries = [b for b in recent_balances if b.weight_kg]
            weight_trend = None
            if len(weight_entries) >= 2:
                # Simple linear trend
                first_weight = weight_entries[-1].weight_kg  # Oldest
                last_weight = weight_entries[0].weight_kg   # Most recent
                days_between = (weight_entries[0].date - weight_entries[-1].date).days
                if days_between > 0:
                    weight_trend = (last_weight - first_weight) / days_between * 7  # Weekly trend
        else:
            avg_calories_consumed = Decimal('0')
            avg_net_calories = Decimal('0')
            weight_trend = None
        
        return {
            "current_goal": current_goal,
            "recent_balances": recent_balances[:7],  # Last week
            "summary": {
                "avg_calories_consumed": avg_calories_consumed,
                "avg_net_calories": avg_net_calories,
                "weight_trend_weekly": weight_trend,
                "days_tracked": len(recent_balances)
            }
        }
    
    async def get_weekly_summary(self, user_id: UUID, weeks_back: int = 4) -> List[Dict[str, Any]]:
        """Get weekly summaries for the last N weeks"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        balances = await self.balance_repo.get_range_by_user(user_id, start_date, end_date)
        
        # Group by week
        weekly_data = []
        current_week_start = start_date
        
        while current_week_start <= end_date:
            week_end = current_week_start + timedelta(days=6)
            week_balances = [
                b for b in balances 
                if current_week_start <= b.date <= week_end
            ]
            
            if week_balances:
                total_consumed = sum(b.calories_consumed for b in week_balances)
                total_net = sum(b.net_calories for b in week_balances)
                avg_consumed = total_consumed / len(week_balances)
                avg_net = total_net / len(week_balances)
                
                # Weight change during week
                weight_entries = [b for b in week_balances if b.weight_kg]
                weight_change = None
                if len(weight_entries) >= 2:
                    weight_change = weight_entries[-1].weight_kg - weight_entries[0].weight_kg
                
                weekly_data.append({
                    "week_start": current_week_start,
                    "week_end": week_end,
                    "days_tracked": len(week_balances),
                    "total_calories_consumed": total_consumed,
                    "avg_calories_consumed": avg_consumed,
                    "avg_net_calories": avg_net,
                    "weight_change": weight_change
                })
            
            current_week_start = week_end + timedelta(days=1)
        
        return weekly_data


class RecommendationService:
    """Application service for providing recommendations"""
    
    def __init__(
        self,
        goal_repo,
        balance_repo,
        metabolic_service
    ):
        self.goal_repo = goal_repo
        self.balance_repo = balance_repo
        self.metabolic_service = metabolic_service
    
    async def get_daily_recommendations(self, user_id: UUID) -> Dict[str, Any]:
        """Get daily recommendations for user"""
        # Get current goal
        goal = await self.goal_repo.get_active_goal_by_user(user_id)
        if not goal:
            return {"error": "No active goal found"}
        
        # Get today's balance
        today = datetime.now().date()
        today_balance = await self.balance_repo.get_by_user_and_date(user_id, today)
        
        recommendations = []
        
        if today_balance:
            remaining_calories = goal.target_calories - today_balance.calories_consumed
            
            if remaining_calories > 200:
                recommendations.append({
                    "type": "calorie_intake",
                    "message": f"You have {remaining_calories:.0f} calories remaining for today",
                    "priority": "medium"
                })
            elif remaining_calories < -200:
                recommendations.append({
                    "type": "calorie_intake",
                    "message": f"You're {abs(remaining_calories):.0f} calories over your goal",
                    "priority": "high"
                })
            
            # Exercise recommendation
            if today_balance.calories_burned_exercise < 100:
                recommendations.append({
                    "type": "exercise",
                    "message": "Consider adding some physical activity today",
                    "priority": "low"
                })
        else:
            recommendations.append({
                "type": "tracking",
                "message": "Don't forget to log your meals today",
                "priority": "medium"
            })
        
        return {
            "date": today,
            "goal": goal,
            "current_balance": today_balance,
            "recommendations": recommendations
        }
