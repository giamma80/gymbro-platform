from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from ..domain import (
    User, CalorieGoal, DailyBalance, MetabolicProfile,
    CalorieCalculationService, MetabolicCalculationService, WeightPredictionService,
    ActivityLevel, GoalType
)


class DefaultCalorieCalculationService(CalorieCalculationService):
    """Default implementation of calorie calculation service"""
    
    def calculate_calorie_goal(
        self, 
        user: User, 
        goal_type: str, 
        weekly_weight_change: Decimal,
        target_weight: Optional[Decimal] = None
    ) -> Decimal:
        """Calculate daily calorie goal based on user profile and goals"""
        # Calculate TDEE
        tdee = user.calculate_tdee()
        if not tdee:
            raise ValueError("Cannot calculate TDEE - missing user profile data")
        
        # Convert goal type
        goal_enum = GoalType(goal_type)
        
        # Calculate calorie adjustment for weight change
        # 1 kg fat ≈ 7700 calories
        calories_per_kg = Decimal('7700')
        weekly_calorie_change = weekly_weight_change * calories_per_kg
        daily_calorie_adjustment = weekly_calorie_change / 7
        
        # Calculate target calories
        target_calories = tdee + daily_calorie_adjustment
        
        # Safety bounds
        min_calories = user.calculate_bmr() * Decimal('1.2') if user.calculate_bmr() else Decimal('1200')
        max_calories = tdee * Decimal('1.5')
        
        target_calories = max(min_calories, min(target_calories, max_calories))
        
        return target_calories.quantize(Decimal('0.1'))
    
    def calculate_progress_metrics(
        self, 
        daily_balances: List[DailyBalance],
        calorie_goal: CalorieGoal
    ) -> Dict[str, Any]:
        """Calculate progress metrics from daily balances"""
        if not daily_balances:
            return {
                "avg_daily_calories": Decimal('0'),
                "goal_adherence_rate": 0.0,
                "calorie_variance": Decimal('0'),
                "days_tracked": 0,
                "weight_change": None
            }
        
        # Calculate averages
        total_consumed = sum(b.calories_consumed for b in daily_balances)
        avg_daily_calories = total_consumed / len(daily_balances)
        
        # Goal adherence (within 100 calories tolerance)
        tolerance = Decimal('100')
        adherent_days = sum(
            1 for b in daily_balances 
            if abs(b.calories_consumed - calorie_goal.target_calories) <= tolerance
        )
        adherence_rate = (adherent_days / len(daily_balances)) * 100
        
        # Calorie variance
        variances = [
            (b.calories_consumed - calorie_goal.target_calories) ** 2 
            for b in daily_balances
        ]
        variance = (sum(variances) / len(variances)) ** Decimal('0.5')
        
        # Weight change
        weight_entries = [b for b in daily_balances if b.weight_kg]
        weight_change = None
        if len(weight_entries) >= 2:
            # Sort by date
            weight_entries.sort(key=lambda x: x.date)
            first_weight = weight_entries[0].weight_kg
            last_weight = weight_entries[-1].weight_kg
            weight_change = last_weight - first_weight
        
        return {
            "avg_daily_calories": avg_daily_calories.quantize(Decimal('0.1')),
            "goal_adherence_rate": round(adherence_rate, 1),
            "calorie_variance": variance.quantize(Decimal('0.1')),
            "days_tracked": len(daily_balances),
            "weight_change": weight_change.quantize(Decimal('0.1')) if weight_change else None,
            "calorie_surplus_deficit": (avg_daily_calories - calorie_goal.target_calories).quantize(Decimal('0.1'))
        }


class DefaultMetabolicCalculationService(MetabolicCalculationService):
    """Default implementation of metabolic calculation service"""
    
    def calculate_bmr(self, user: User) -> Optional[Decimal]:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
        return user.calculate_bmr()
    
    def calculate_tdee(self, user: User) -> Optional[Decimal]:
        """Calculate Total Daily Energy Expenditure"""
        return user.calculate_tdee()
    
    def should_recalculate_profile(self, profile: MetabolicProfile, user: User) -> bool:
        """Determine if metabolic profile needs recalculation"""
        # Recalculate if user's key metrics have changed significantly
        current_bmr = self.calculate_bmr(user)
        current_tdee = self.calculate_tdee(user)
        
        if not current_bmr or not current_tdee:
            return False
        
        # Check for significant changes (>5%)
        bmr_change = abs(current_bmr - profile.bmr) / profile.bmr
        tdee_change = abs(current_tdee - profile.tdee) / profile.tdee
        
        return bmr_change > Decimal('0.05') or tdee_change > Decimal('0.05')


class DefaultWeightPredictionService(WeightPredictionService):
    """Default implementation of weight prediction service"""
    
    def predict_weight_change(
        self, 
        current_weight: Decimal,
        daily_balances: List[DailyBalance],
        goal: CalorieGoal
    ) -> Dict[str, Any]:
        """Predict weight change based on calorie balance"""
        if not daily_balances:
            return {
                "predicted_weekly_change": Decimal('0'),
                "predicted_monthly_change": Decimal('0'),
                "goal_timeline_weeks": None,
                "confidence": "low"
            }
        
        # Calculate average daily calorie surplus/deficit
        avg_surplus = sum(
            b.net_calories - goal.target_calories 
            for b in daily_balances
        ) / len(daily_balances)
        
        # Convert to weight change
        # 7700 calories ≈ 1 kg
        calories_per_kg = Decimal('7700')
        predicted_daily_weight_change = avg_surplus / calories_per_kg
        
        # Project to different timeframes
        predicted_weekly = predicted_daily_weight_change * 7
        predicted_monthly = predicted_daily_weight_change * 30
        
        # Calculate confidence based on data consistency
        calorie_variance = self._calculate_variance([b.net_calories for b in daily_balances])
        confidence = "high" if calorie_variance < 500 else "medium" if calorie_variance < 1000 else "low"
        
        # Timeline to goal
        goal_timeline_weeks = None
        if goal.target_weight_kg and predicted_weekly != 0:
            weight_to_lose = current_weight - goal.target_weight_kg
            goal_timeline_weeks = weight_to_lose / predicted_weekly
        
        return {
            "predicted_weekly_change": predicted_weekly.quantize(Decimal('0.1')),
            "predicted_monthly_change": predicted_monthly.quantize(Decimal('0.1')),
            "goal_timeline_weeks": goal_timeline_weeks.quantize(Decimal('0.1')) if goal_timeline_weeks else None,
            "confidence": confidence,
            "avg_daily_surplus": avg_surplus.quantize(Decimal('0.1'))
        }
    
    def calculate_goal_timeline(
        self, 
        current_weight: Decimal,
        target_weight: Decimal,
        weekly_change: Decimal
    ) -> Dict[str, Any]:
        """Calculate timeline to reach weight goal"""
        if weekly_change == 0:
            return {
                "weeks_to_goal": None,
                "months_to_goal": None,
                "target_date": None,
                "feasible": False
            }
        
        weight_difference = target_weight - current_weight
        weeks_to_goal = weight_difference / weekly_change
        
        # Validate if goal is feasible (reasonable timeline)
        feasible = 1 <= abs(weeks_to_goal) <= 104  # 1 week to 2 years
        
        months_to_goal = weeks_to_goal / Decimal('4.33')  # Average weeks per month
        
        # Calculate target date
        target_date = None
        if feasible:
            from datetime import datetime, timedelta
            target_date = datetime.now().date() + timedelta(weeks=float(weeks_to_goal))
        
        return {
            "weeks_to_goal": weeks_to_goal.quantize(Decimal('0.1')) if feasible else None,
            "months_to_goal": months_to_goal.quantize(Decimal('0.1')) if feasible else None,
            "target_date": target_date,
            "feasible": feasible,
            "weekly_rate": weekly_change
        }
    
    def _calculate_variance(self, values: List[Decimal]) -> Decimal:
        """Calculate variance of values"""
        if not values:
            return Decimal('0')
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance.quantize(Decimal('0.1'))
