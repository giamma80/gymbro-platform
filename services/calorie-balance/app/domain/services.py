from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date as date_type
from decimal import Decimal

from .entities import User, CalorieGoal, DailyBalance, MetabolicProfile


class CalorieCalculationService(ABC):
    """Domain service for calorie calculations"""
    
    @abstractmethod
    def calculate_calorie_goal(
        self, 
        user: User, 
        goal_type: str, 
        weekly_weight_change: Decimal,
        target_weight: Optional[Decimal] = None
    ) -> Decimal:
        """Calculate daily calorie goal based on user profile and goals"""
        pass
    
    @abstractmethod
    def calculate_progress_metrics(
        self, 
        daily_balances: List[DailyBalance],
        calorie_goal: CalorieGoal
    ) -> dict:
        """Calculate progress metrics from daily balances"""
        pass


class MetabolicCalculationService(ABC):
    """Domain service for metabolic calculations"""
    
    @abstractmethod
    def calculate_bmr(self, user: User) -> Optional[Decimal]:
        """Calculate Basal Metabolic Rate"""
        pass
    
    @abstractmethod
    def calculate_tdee(self, user: User) -> Optional[Decimal]:
        """Calculate Total Daily Energy Expenditure"""
        pass
    
    @abstractmethod
    def should_recalculate_profile(self, profile: MetabolicProfile, user: User) -> bool:
        """Determine if metabolic profile needs recalculation"""
        pass


class WeightPredictionService(ABC):
    """Domain service for weight prediction"""
    
    @abstractmethod
    def predict_weight_change(
        self, 
        current_weight: Decimal,
        daily_balances: List[DailyBalance],
        goal: CalorieGoal
    ) -> dict:
        """Predict weight change based on calorie balance"""
        pass
    
    @abstractmethod
    def calculate_goal_timeline(
        self, 
        current_weight: Decimal,
        target_weight: Decimal,
        weekly_change: Decimal
    ) -> dict:
        """Calculate timeline to reach weight goal"""
        pass
