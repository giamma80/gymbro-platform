"""
API schemas for calorie-balance service.

This module defines Pydantic models for request/response validation
and serialization for the calorie-balance service API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Import domain enums
from app.domain.entities import ActivityLevel, GenderType


class UserMetricsSchema(BaseModel):
    """Schema for user metrics using Parameter Passing pattern."""

    weight_kg: Decimal = Field(
        ..., description="Current weight in kilograms", ge=20, le=500
    )
    height_cm: Decimal = Field(..., description="Height in centimeters", ge=50, le=300)
    age: int = Field(..., description="Age in years", ge=13, le=120)
    gender: GenderType = Field(..., description="Gender (MALE/FEMALE)")
    activity_level: ActivityLevel = Field(..., description="Physical activity level")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "weight_kg": 75.5,
                "height_cm": 175.0,
                "age": 30,
                "gender": "MALE",
                "activity_level": "MODERATE",
            }
        },
    )


class MetabolicCalculationRequest(UserMetricsSchema):
    """Schema for metabolic profile calculation request."""

    pass


class MetabolicProfileResponse(BaseModel):
    """Schema for metabolic profile response - aligned with database schema."""

    # Core entity fields from database schema
    id: UUID
    user_id: UUID
    bmr_calories: Decimal
    tdee_calories: Decimal
    rmr_calories: Decimal
    calculation_method: str
    accuracy_score: Decimal

    # Activity multipliers
    activity_level: Optional[str] = None
    sedentary_multiplier: Decimal
    light_multiplier: Decimal
    moderate_multiplier: Decimal
    high_multiplier: Decimal
    extreme_multiplier: Decimal

    # AI fields
    ai_adjusted: bool = False
    adjustment_factor: Decimal
    learning_iterations: int = 0

    # Timestamps and status
    calculated_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class WeightLossGoalRequest(UserMetricsSchema):
    """Schema for creating weight loss goal with user metrics."""

    target_weight_kg: Decimal = Field(
        ..., description="Target weight in kilograms", ge=20, le=500
    )
    weekly_loss_kg: Decimal = Field(
        ..., description="Desired weekly weight loss in kg", ge=0.1, le=2.0
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "weight_kg": 80.0,
                "height_cm": 175.0,
                "age": 30,
                "gender": "MALE",
                "activity_level": "MODERATE",
                "target_weight_kg": 75.0,
                "weekly_loss_kg": 0.5,
            }
        },
    )


class UcalorieUbalanceBase(BaseModel):
    """Base schema for calorie-balance with common fields."""

    model_config = ConfigDict(
        from_attributes=True, validate_assignment=True, arbitrary_types_allowed=True
    )


class UcalorieUbalanceCreate(UcalorieUbalanceBase):
    """Schema for creating a new calorie-balance record."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Name of the calorie-balance"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Description of the calorie-balance"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Example calorie-balance",
                "description": "This is an example calorie-balance record",
                "metadata": {"category": "example", "priority": "high"},
            }
        },
    )


class UcalorieUbalanceUpdate(BaseModel):
    """Schema for updating a calorie-balance record."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Name of the calorie-balance"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Description of the calorie-balance"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "name": "Updated calorie-balance",
                "description": "This is an updated calorie-balance record",
            }
        },
    )


class UcalorieUbalanceResponse(UcalorieUbalanceBase):
    """Schema for calorie-balance responses."""

    id: UUID = Field(..., description="Unique identifier for the calorie-balance")
    user_id: UUID = Field(
        ..., description="ID of the user who owns this calorie-balance"
    )
    name: str = Field(..., description="Name of the calorie-balance")
    description: Optional[str] = Field(
        None, description="Description of the calorie-balance"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated"
    )

    @classmethod
    def from_entity(cls, entity) -> "UcalorieUbalanceResponse":
        """Create response schema from domain entity."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            description=entity.description,
            metadata=entity.metadata or {},
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51d2-43a1-b789-123456789abc",
                "name": "Example calorie-balance",
                "description": "This is an example calorie-balance record",
                "metadata": {"category": "example", "priority": "high"},
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            }
        },
    )


class UcalorieUbalanceListResponse(BaseModel):
    """Schema for paginated calorie-balance list responses."""

    records: List[UcalorieUbalanceResponse] = Field(
        ..., description="List of calorie-balance records"
    )
    total: int = Field(..., description="Total number of records returned")
    limit: int = Field(..., description="Maximum number of records requested")
    offset: int = Field(..., description="Number of records skipped")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "records": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "987fcdeb-51d2-43a1-b789-123456789abc",
                        "name": "Example calorie-balance",
                        "description": "This is an example calorie-balance record",
                        "metadata": {},
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                    }
                ],
                "total": 1,
                "limit": 10,
                "offset": 0,
            }
        },
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "detail": "Resource not found",
                "error_code": "RESOURCE_NOT_FOUND",
                "timestamp": "2024-01-01T12:00:00Z",
            }
        },
    )


class HealthResponse(BaseModel):
    """Schema for health check responses."""

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Health check timestamp")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional health details"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "calorie-balance",
                "timestamp": "2024-01-01T12:00:00Z",
                "details": {"database": "connected", "version": "1.0.0"},
            }
        },
    )
