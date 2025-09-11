"""
API schemas for {service-name} service.

This module defines Pydantic models for request/response validation
and serialization for the {service-name} service API.
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.types import UUID4


class {ServiceName}Base(BaseModel):
    """Base schema for {service-name} with common fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )


class {ServiceName}Create({ServiceName}Base):
    """Schema for creating a new {service-name} record."""
    
    # Add your specific fields here based on your service requirements
    name: str = Field(..., min_length=1, max_length=255, description="Name of the {service-name}")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the {service-name}")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Example {service-name}",
                "description": "This is an example {service-name} record",
                "metadata": {
                    "category": "example",
                    "priority": "high"
                }
            }
        }


class {ServiceName}Update(BaseModel):
    """Schema for updating a {service-name} record."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    # All fields are optional for updates
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the {service-name}")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the {service-name}")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated {service-name}",
                "description": "This is an updated {service-name} record"
            }
        }


class {ServiceName}Response({ServiceName}Base):
    """Schema for {service-name} responses."""
    
    id: UUID4 = Field(..., description="Unique identifier for the {service-name}")
    user_id: UUID4 = Field(..., description="ID of the user who owns this {service-name}")
    name: str = Field(..., description="Name of the {service-name}")
    description: Optional[str] = Field(None, description="Description of the {service-name}")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated")
    
    @classmethod
    def from_entity(cls, entity) -> "{ServiceName}Response":
        """
        Create response schema from domain entity.
        
        Args:
            entity: Domain entity instance
            
        Returns:
            {ServiceName}Response instance
        """
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            description=entity.description,
            metadata=entity.metadata or {},
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51d2-43a1-b789-123456789abc",
                "name": "Example {service-name}",
                "description": "This is an example {service-name} record",
                "metadata": {
                    "category": "example",
                    "priority": "high"
                },
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class {ServiceName}ListResponse(BaseModel):
    """Schema for paginated {service-name} list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    records: List[{ServiceName}Response] = Field(..., description="List of {service-name} records")
    total: int = Field(..., description="Total number of records returned")
    limit: int = Field(..., description="Maximum number of records requested")
    offset: int = Field(..., description="Number of records skipped")
    
    class Config:
        json_schema_extra = {
            "example": {
                "records": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "987fcdeb-51d2-43a1-b789-123456789abc",
                        "name": "Example {service-name}",
                        "description": "This is an example {service-name} record",
                        "metadata": {},
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total": 1,
                "limit": 100,
                "offset": 0
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Resource not found",
                "error_code": "RESOURCE_NOT_FOUND",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Schema for health check responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Health check timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "{service-name}",
                "timestamp": "2024-01-01T12:00:00Z",
                "details": {
                    "database": "connected",
                    "version": "1.0.0"
                }
            }
        }
