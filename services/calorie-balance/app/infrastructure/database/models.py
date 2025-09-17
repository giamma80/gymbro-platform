from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


class UserModel(Base):
    """SQLAlchemy model for User entity"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    height_cm = Column(Numeric(5, 1), nullable=True)
    weight_kg = Column(Numeric(5, 1), nullable=True)
    activity_level = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    calorie_goals = relationship("CalorieGoalModel", back_populates="user", cascade="all, delete-orphan")
    daily_balances = relationship("DailyBalanceModel", back_populates="user", cascade="all, delete-orphan")
    metabolic_profiles = relationship("MetabolicProfileModel", back_populates="user", cascade="all, delete-orphan")


class CalorieGoalModel(Base):
    """SQLAlchemy model for CalorieGoal entity"""
    __tablename__ = "calorie_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_type = Column(String(30), nullable=False)
    target_calories = Column(Numeric(6, 1), nullable=False)
    target_weight_kg = Column(Numeric(5, 1), nullable=True)
    weekly_weight_change_kg = Column(Numeric(3, 1), default=0.0, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="calorie_goals")


class DailyBalanceModel(Base):
    """SQLAlchemy model for DailyBalance entity"""
    __tablename__ = "daily_balances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    calories_consumed = Column(Numeric(6, 1), default=0.0, nullable=False)
    calories_burned_exercise = Column(Numeric(6, 1), default=0.0, nullable=False)
    calories_burned_bmr = Column(Numeric(6, 1), nullable=True)
    net_calories = Column(Numeric(6, 1), default=0.0, nullable=False)
    weight_kg = Column(Numeric(5, 1), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="daily_balances")
    
    # Composite unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )


class MetabolicProfileModel(Base):
    """SQLAlchemy model for MetabolicProfile entity"""
    __tablename__ = "metabolic_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)  # VARCHAR(255) as per schema
    
    # Calculated metabolic values
    bmr_calories = Column(Numeric(6, 1), nullable=False)
    tdee_calories = Column(Numeric(6, 1), nullable=False) 
    rmr_calories = Column(Numeric(6, 1), nullable=True)
    
    # Calculation method and accuracy
    calculation_method = Column(String(50), default='mifflin_st_jeor')
    accuracy_score = Column(Numeric(3, 2), default=0.8)
    
    # Activity multipliers
    sedentary_multiplier = Column(Numeric(3, 2), default=1.2)
    light_multiplier = Column(Numeric(3, 2), default=1.375)
    moderate_multiplier = Column(Numeric(3, 2), default=1.55)
    high_multiplier = Column(Numeric(3, 2), default=1.725)
    extreme_multiplier = Column(Numeric(3, 2), default=1.9)
    
    # Activity level (added in 006_fix_schema_task_1_1.sql)
    activity_level = Column(String(20), default='moderate')
    
    # AI learning data
    ai_adjusted = Column(Boolean, default=False)
    adjustment_factor = Column(Numeric(4, 3), default=1.000)
    learning_iterations = Column(Integer, default=0)
    
    # Validity period
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), server_default=text("NOW() + INTERVAL '30 days'"))
    is_active = Column(Boolean, default=True)
    
    # Note: No relationship to UserModel since it's in user_management schema
