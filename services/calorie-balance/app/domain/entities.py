from datetime import datetime
from datetime import date as date_type
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator


class ActivityLevel(str, Enum):
    """User activity level enumeration"""
    SEDENTARY = "sedentary"          # Little or no exercise
    LIGHTLY_ACTIVE = "lightly_active"  # Light exercise 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # Moderate exercise 3-5 days/week
    VERY_ACTIVE = "very_active"      # Hard exercise 6-7 days/week
    EXTRA_ACTIVE = "extra_active"    # Very hard exercise, physical job


class Gender(str, Enum):
    """User gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class GoalType(str, Enum):
    """Calorie goal type enumeration"""
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTENANCE = "maintenance"


class User(BaseModel):
    """User domain entity"""
    id: str = Field(..., description="User unique identifier")
    username: str = Field(..., min_length=3, max_length=100, description="Username (unique, min 3 chars)")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[Gender] = None
    height_cm: Optional[Decimal] = Field(None, ge=50, le=300, decimal_places=1)
    weight_kg: Optional[Decimal] = Field(None, ge=20, le=500, decimal_places=1)
    activity_level: Optional[ActivityLevel] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    @validator('weight_kg', 'height_cm')
    def validate_positive_numbers(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Value must be positive')
        return v

    def calculate_bmr(self) -> Optional[Decimal]:
        """Calcola il Basal Metabolic Rate usando la formula Mifflin-St Jeor"""
        if not all([self.weight_kg, self.height_cm, self.age, self.gender]):
            return None
        weight = float(self.weight_kg)
        height = float(self.height_cm)
        age = float(self.age)
        bmr = 10 * weight + 6.25 * height - 5 * age
        if self.gender == Gender.MALE:
            bmr += 5
        elif self.gender == Gender.FEMALE:
            bmr -= 161
        return Decimal(str(bmr)).quantize(Decimal('0.1'))

    def calculate_tdee(self) -> Optional[Decimal]:
        """Calcola il Total Daily Energy Expenditure (TDEE) usando il BMR e il livello di attività"""
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTRA_ACTIVE: 1.9,
        }
        bmr = self.calculate_bmr()
        if bmr is None or self.activity_level is None:
            return None
        multiplier = activity_multipliers[self.activity_level]
        return (bmr * Decimal(str(multiplier))).quantize(Decimal('0.1'))


class CalorieGoal(BaseModel):
    """Calorie goal domain entity"""
    id: UUID = Field(default_factory=uuid4)
    user_id: str = Field(..., description="Reference to user")
    goal_type: GoalType = Field(..., description="Type of calorie goal")
    target_calories: Decimal = Field(..., ge=800, le=5000, decimal_places=1)
    target_weight_kg: Optional[Decimal] = Field(None, ge=20, le=500, decimal_places=1)
    weekly_weight_change_kg: Decimal = Field(Decimal('0.0'), ge=-2, le=2, decimal_places=1)
    start_date: date_type = Field(default_factory=date_type.today)
    end_date: Optional[date_type] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('weekly_weight_change_kg')
    def validate_weight_change(cls, v, values):
        if 'goal_type' in values:
            goal_type = values['goal_type']
            if goal_type == GoalType.WEIGHT_LOSS and v > 0:
                raise ValueError('Weight loss goal must have negative or zero weight change')
            elif goal_type == GoalType.WEIGHT_GAIN and v < 0:
                raise ValueError('Weight gain goal must have positive weight change')
        return v


class DailyBalance(BaseModel):
    """Daily calorie balance domain entity"""
    id: Optional[UUID] = Field(default=None)  # Let database generate ID
    user_id: str = Field(..., description="Reference to user")
    date: date_type = Field(..., description="Date for this balance record")
    calories_consumed: Decimal = Field(Decimal('0.0'), ge=0, le=10000, decimal_places=1)
    calories_burned_exercise: Decimal = Field(Decimal('0.0'), ge=0, le=5000, decimal_places=1)
    calories_burned_bmr: Decimal = Field(Decimal('0.0'), ge=0, le=5000, decimal_places=1)
    net_calories: Decimal = Field(Decimal('0.0'), decimal_places=1)
    weight_kg: Optional[Decimal] = Field(None, ge=20, le=500, decimal_places=1)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def calculate_net_calories(self) -> Decimal:
        """Calculate net calories (consumed - burned)"""
        total_burned = self.calories_burned_exercise
        if self.calories_burned_bmr:
            total_burned += self.calories_burned_bmr
        
        self.net_calories = (self.calories_consumed - total_burned).quantize(Decimal('0.1'))
        return self.net_calories

    def is_within_goal(self, target_calories: Decimal, tolerance: Decimal = Decimal('100')) -> bool:
        """Check if daily balance is within calorie goal tolerance"""
        return abs(self.net_calories - target_calories) <= tolerance


class MetabolicProfile(BaseModel):
    """Metabolic profile calculation entity"""
    id: UUID = Field(default_factory=uuid4)
    user_id: str = Field(..., description="Reference to user")
    bmr: Decimal = Field(..., ge=800, le=5000, decimal_places=1)
    tdee: Decimal = Field(..., ge=800, le=6000, decimal_places=1)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime = Field(..., description="When this profile expires")
    
    @classmethod
    def create_from_user(cls, user: User) -> Optional['MetabolicProfile']:
        """Create metabolic profile from user data"""
        bmr = user.calculate_bmr()
        tdee = user.calculate_tdee()
        
        if not bmr or not tdee:
            return None
        
        # Profile valid for 30 days
        from datetime import timedelta
        valid_until = datetime.utcnow() + timedelta(days=30)
        
        return cls(
            user_id=user.id,
            bmr=bmr,
            tdee=tdee,
            valid_until=valid_until
        )

    def is_valid(self) -> bool:
        """Check if profile is still valid"""
        return datetime.utcnow() < self.valid_until
