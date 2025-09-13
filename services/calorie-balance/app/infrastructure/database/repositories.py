from typing import List, Optional
from uuid import UUID
from datetime import date as date_type, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from ...domain import (
    CalorieGoal, DailyBalance, MetabolicProfile,
    CalorieGoalRepository, DailyBalanceRepository, MetabolicProfileRepository,
    ActivityLevel, GoalType
)
from .models import CalorieGoalModel, DailyBalanceModel, MetabolicProfileModel

def goal_model_to_entity(model: CalorieGoalModel) -> CalorieGoal:
    """Convert CalorieGoalModel to CalorieGoal entity"""
    return CalorieGoal(
        id=str(model.id) if model.id is not None else None,
        user_id=str(model.user_id) if model.user_id is not None else None,
        goal_type=GoalType(model.goal_type),
        target_calories=model.target_calories,
        target_weight_kg=model.target_weight_kg,
        weekly_weight_change_kg=model.weekly_weight_change_kg,
        start_date=model.start_date,
        end_date=model.end_date,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at
    )

def goal_entity_to_model(entity: CalorieGoal) -> CalorieGoalModel:
    """Convert CalorieGoal entity to CalorieGoalModel"""
    from uuid import UUID
    return CalorieGoalModel(
        id=UUID(str(entity.id)) if entity.id is not None else None,
        user_id=UUID(str(entity.user_id)) if entity.user_id is not None else None,
        goal_type=entity.goal_type.value,
        target_calories=entity.target_calories,
        target_weight_kg=entity.target_weight_kg,
        weekly_weight_change_kg=entity.weekly_weight_change_kg,
        start_date=entity.start_date,
        end_date=entity.end_date,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )

def balance_model_to_entity(model: DailyBalanceModel) -> DailyBalance:
    """Convert DailyBalanceModel to DailyBalance entity"""
    return DailyBalance(
        id=str(model.id) if model.id is not None else None,
        user_id=str(model.user_id) if model.user_id is not None else None,
        date=model.date,
        calories_consumed=model.calories_consumed,
        calories_burned_exercise=model.calories_burned_exercise,
        calories_burned_bmr=model.calories_burned_bmr,
        net_calories=model.net_calories,
        weight_kg=model.weight_kg,
        notes=model.notes,
        created_at=model.created_at,
        updated_at=model.updated_at
    )

def balance_entity_to_model(entity: DailyBalance) -> DailyBalanceModel:
    """Convert DailyBalance entity to DailyBalanceModel"""
    return DailyBalanceModel(
        id=entity.id,
        user_id=entity.user_id,
        date=entity.date,
        calories_consumed=entity.calories_consumed,
        calories_burned_exercise=entity.calories_burned_exercise,
        calories_burned_bmr=entity.calories_burned_bmr,
        net_calories=entity.net_calories,
        weight_kg=entity.weight_kg,
        notes=entity.notes,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )

def profile_model_to_entity(model: MetabolicProfileModel) -> MetabolicProfile:
    """Convert MetabolicProfileModel to MetabolicProfile entity"""
    return MetabolicProfile(
        id=str(model.id) if model.id is not None else None,
        user_id=str(model.user_id) if model.user_id is not None else None,
        bmr=model.bmr,
        tdee=model.tdee,
        calculated_at=model.calculated_at,
        valid_until=model.valid_until
    )

def profile_entity_to_model(entity: MetabolicProfile) -> MetabolicProfileModel:
    """Convert MetabolicProfile entity to MetabolicProfileModel"""
    return MetabolicProfileModel(
        id=entity.id,
        user_id=entity.user_id,
        bmr=entity.bmr,
        tdee=entity.tdee,
        calculated_at=entity.calculated_at,
        valid_until=entity.valid_until
    )

    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[CalorieGoal]:
        """Get goal by ID"""
        stmt = select(CalorieGoalModel).where(CalorieGoalModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return goal_model_to_entity(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CalorieGoal]:
        """Get all goals with pagination"""
        stmt = select(CalorieGoalModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [goal_model_to_entity(model) for model in models]
    
    async def create(self, entity: CalorieGoal) -> CalorieGoal:
        """Create new goal"""
        model = goal_entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return goal_model_to_entity(model)
    
    async def update(self, entity: CalorieGoal) -> CalorieGoal:
        """Update existing goal"""
        stmt = select(CalorieGoalModel).where(CalorieGoalModel.id == entity.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Goal {entity.id} not found")
        
        # Update fields
        model.goal_type = entity.goal_type.value
        model.target_calories = entity.target_calories
        model.target_weight_kg = entity.target_weight_kg
        model.weekly_weight_change_kg = entity.weekly_weight_change_kg
        model.start_date = entity.start_date
        model.end_date = entity.end_date
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        
        await self.session.flush()
        return goal_model_to_entity(model)
    
    async def delete(self, id: UUID) -> bool:
        """Delete goal by ID"""
        stmt = select(CalorieGoalModel).where(CalorieGoalModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False
    
    async def get_active_goal_by_user(self, user_id: UUID) -> Optional[CalorieGoal]:
        """Get active calorie goal for user"""
        stmt = select(CalorieGoalModel).where(
            and_(
                CalorieGoalModel.user_id == user_id,
                CalorieGoalModel.is_active == True
            )
        ).order_by(desc(CalorieGoalModel.created_at))
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return goal_model_to_entity(model) if model else None
    
    async def get_goals_by_user(self, user_id: UUID, include_inactive: bool = False) -> List[CalorieGoal]:
        """Get all goals for user"""
        conditions = [CalorieGoalModel.user_id == user_id]
        if not include_inactive:
            conditions.append(CalorieGoalModel.is_active == True)
        
        stmt = select(CalorieGoalModel).where(
            and_(*conditions)
        ).order_by(desc(CalorieGoalModel.created_at))
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [goal_model_to_entity(model) for model in models]
    
    async def deactivate_user_goals(self, user_id: UUID) -> None:
        """Deactivate all goals for user"""
        stmt = select(CalorieGoalModel).where(
            and_(
                CalorieGoalModel.user_id == user_id,
                CalorieGoalModel.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        for model in models:
            model.is_active = False
            model.updated_at = datetime.utcnow()
        
        await self.session.flush()

class SqlDailyBalanceRepository(DailyBalanceRepository):
    """SQLAlchemy implementation of DailyBalanceRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[DailyBalance]:
        """Get balance by ID"""
        stmt = select(DailyBalanceModel).where(DailyBalanceModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return balance_model_to_entity(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[DailyBalance]:
        """Get all balances with pagination"""
        stmt = select(DailyBalanceModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [balance_model_to_entity(model) for model in models]
    
    async def create(self, entity: DailyBalance) -> DailyBalance:
        """Create new balance"""
        model = balance_entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return balance_model_to_entity(model)
    
    async def update(self, entity: DailyBalance) -> DailyBalance:
        """Update existing balance"""
        stmt = select(DailyBalanceModel).where(DailyBalanceModel.id == entity.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Balance {entity.id} not found")
        
        # Update fields
        model.date = entity.date
        model.calories_consumed = entity.calories_consumed
        model.calories_burned_exercise = entity.calories_burned_exercise
        model.calories_burned_bmr = entity.calories_burned_bmr
        model.net_calories = entity.net_calories
        model.weight_kg = entity.weight_kg
        model.notes = entity.notes
        model.updated_at = entity.updated_at
        
        await self.session.flush()
        return balance_model_to_entity(model)
    
    async def delete(self, id: UUID) -> bool:
        """Delete balance by ID"""
        stmt = select(DailyBalanceModel).where(DailyBalanceModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False
    
    async def get_by_user_and_date(self, user_id: UUID, date: date_type) -> Optional[DailyBalance]:
        """Get daily balance for specific user and date"""
        stmt = select(DailyBalanceModel).where(
            and_(
                DailyBalanceModel.user_id == user_id,
                DailyBalanceModel.date == date
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return balance_model_to_entity(model) if model else None
    
    async def get_range_by_user(
        self, 
        user_id: UUID, 
        start_date: date_type, 
        end_date: date_type
    ) -> List[DailyBalance]:
        """Get daily balances for user within date range"""
        stmt = select(DailyBalanceModel).where(
            and_(
                DailyBalanceModel.user_id == user_id,
                DailyBalanceModel.date >= start_date,
                DailyBalanceModel.date <= end_date
            )
        ).order_by(desc(DailyBalanceModel.date))
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [balance_model_to_entity(model) for model in models]
    
    async def get_latest_by_user(self, user_id: UUID, limit: int = 30) -> List[DailyBalance]:
        """Get latest daily balances for user"""
        stmt = select(DailyBalanceModel).where(
            DailyBalanceModel.user_id == user_id
        ).order_by(desc(DailyBalanceModel.date)).limit(limit)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [balance_model_to_entity(model) for model in models]

class SqlMetabolicProfileRepository(MetabolicProfileRepository):
    """SQLAlchemy implementation of MetabolicProfileRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[MetabolicProfile]:
        """Get profile by ID"""
        stmt = select(MetabolicProfileModel).where(MetabolicProfileModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return profile_model_to_entity(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MetabolicProfile]:
        """Get all profiles with pagination"""
        stmt = select(MetabolicProfileModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [profile_model_to_entity(model) for model in models]
    
    async def create(self, entity: MetabolicProfile) -> MetabolicProfile:
        """Create new profile"""
        model = profile_entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return profile_model_to_entity(model)
    
    async def update(self, entity: MetabolicProfile) -> MetabolicProfile:
        """Update existing profile"""
        stmt = select(MetabolicProfileModel).where(MetabolicProfileModel.id == entity.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Profile {entity.id} not found")
        
        # Update fields
        model.bmr = entity.bmr
        model.tdee = entity.tdee
        model.calculated_at = entity.calculated_at
        model.valid_until = entity.valid_until
        
        await self.session.flush()
        return profile_model_to_entity(model)
    
    async def delete(self, id: UUID) -> bool:
        """Delete profile by ID"""
        stmt = select(MetabolicProfileModel).where(MetabolicProfileModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False
    
    async def get_current_by_user(self, user_id: UUID) -> Optional[MetabolicProfile]:
        """Get current valid metabolic profile for user"""
        now = datetime.utcnow()
        stmt = select(MetabolicProfileModel).where(
            and_(
                MetabolicProfileModel.user_id == user_id,
                MetabolicProfileModel.valid_until > now
            )
        ).order_by(desc(MetabolicProfileModel.calculated_at))
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return profile_model_to_entity(model) if model else None
    
    async def get_latest_by_user(self, user_id: UUID) -> Optional[MetabolicProfile]:
        """Get latest metabolic profile for user (even if expired)"""
        stmt = select(MetabolicProfileModel).where(
            MetabolicProfileModel.user_id == user_id
        ).order_by(desc(MetabolicProfileModel.calculated_at))
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return profile_model_to_entity(model) if model else None
    
    async def delete_expired_profiles(self) -> int:
        """Delete expired metabolic profiles"""
        now = datetime.utcnow()
        stmt = select(MetabolicProfileModel).where(
            MetabolicProfileModel.valid_until <= now
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        count = len(models)
        for model in models:
            await self.session.delete(model)
        
        await self.session.flush()
        return count
