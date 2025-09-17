from datetime import date as date_type
from decimal import Decimal
from typing import Optional

from ..domain import (
    CalorieCalculationService,
    CalorieGoal,
    CalorieGoalRepository,
    DailyBalance,
    DailyBalanceRepository,
    MetabolicCalculationService,
)


class CreateCalorieGoalCommand:
    """Command to create a new calorie goal"""

    def __init__(
        self,
        user_id: str,
        goal_type: str,
        target_weight_kg: Optional[Decimal] = None,
        weekly_weight_change_kg: Decimal = Decimal("0.0"),
        start_date: Optional[date_type] = None,
    ):
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_weight_kg = target_weight_kg
        self.weekly_weight_change_kg = weekly_weight_change_kg
        self.start_date = start_date or date_type.today()


class UpdateDailyBalanceCommand:
    """Command to update daily calorie balance"""

    def __init__(
        self,
        user_id: str,
        date: date_type,
        calories_consumed: Optional[Decimal] = None,
        calories_burned_exercise: Optional[Decimal] = None,
        weight_kg: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ):
        self.user_id = user_id
        self.date = date
        self.calories_consumed = calories_consumed
        self.calories_burned_exercise = calories_burned_exercise
        self.weight_kg = weight_kg
        self.notes = notes


class CalorieGoalCommandHandler:
    """Command handler for calorie goal operations"""

    def __init__(
        self,
        goal_repo: CalorieGoalRepository,
        calorie_service: CalorieCalculationService,
    ):
        self.goal_repo = goal_repo
        self.calorie_service = calorie_service

    async def handle_create_goal(
        self, command: CreateCalorieGoalCommand
    ) -> CalorieGoal:
        """Handle create calorie goal command"""
        async with self.uow:
            # Verify user exists
            user = await self.user_repo.get_by_id(command.user_id)
            if not user:
                raise ValueError(f"User {command.user_id} not found")

            # Deactivate existing goals
            await self.goal_repo.deactivate_user_goals(command.user_id)

            # Calculate target calories
            target_calories = self.calorie_service.calculate_calorie_goal(
                user=user,
                goal_type=command.goal_type,
                weekly_weight_change=command.weekly_weight_change_kg,
                target_weight=command.target_weight_kg,
            )

            # Create new goal
            goal = CalorieGoal(
                user_id=command.user_id,
                goal_type=command.goal_type,
                target_calories=target_calories,
                target_weight_kg=command.target_weight_kg,
                weekly_weight_change_kg=command.weekly_weight_change_kg,
                start_date=command.start_date,
            )

            created_goal = await self.goal_repo.create(goal)
            await self.uow.commit()

            return created_goal


class DailyBalanceCommandHandler:
    """Command handler for daily balance operations"""

    def __init__(
        self,
        balance_repo: DailyBalanceRepository,
    ):
        self.balance_repo = balance_repo

    async def handle_update_balance(
        self, command: UpdateDailyBalanceCommand
    ) -> DailyBalance:
        """Handle update daily balance command"""
        async with self.uow:
            # Verify user exists
            user = await self.user_repo.get_by_id(command.user_id)
            if not user:
                raise ValueError(f"User {command.user_id} not found")

            # Get or create daily balance
            balance = await self.balance_repo.get_by_user_and_date(
                command.user_id, command.date
            )

            if not balance:
                balance = DailyBalance(
                    id=None,  # Let database generate ID
                    user_id=str(command.user_id),
                    date=command.date,
                )

            # Update fields if provided
            if command.calories_consumed is not None:
                balance.calories_consumed = command.calories_consumed
            if command.calories_burned_exercise is not None:
                balance.calories_burned_exercise = command.calories_burned_exercise
            if command.weight_kg is not None:
                balance.weight_kg = command.weight_kg
            if command.notes is not None:
                balance.notes = command.notes

            # Get BMR from metabolic profile
            profile = await self.metabolic_profile_repo.get_current_by_user(
                command.user_id
            )
            if profile:
                balance.calories_burned_bmr = profile.bmr

            # Calculate net calories
            balance.calculate_net_calories()

            # Update timestamp
            from datetime import datetime

            balance.updated_at = datetime.utcnow()

            if balance.id:  # Existing record
                updated_balance = await self.balance_repo.update(balance)
            else:  # New record
                updated_balance = await self.balance_repo.create(balance)

            await self.uow.commit()
            return updated_balance
