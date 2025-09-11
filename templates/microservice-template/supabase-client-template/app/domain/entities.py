"""
Domain Entities - {service-name} Service

Core business entities for the {service-name} domain.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """
    Base entity with common fields.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Example entity - replace with your actual entities
class Example{ServiceName}Entity(BaseEntity):
    """
    Example entity for {service-name} service.
    
    Replace this with your actual domain entities.
    """
    name: str = Field(..., description="Entity name")
    description: Optional[str] = Field(None, description="Entity description")
    is_active: bool = Field(True, description="Whether the entity is active")


# Add more entities as needed for your domain
# class Another{ServiceName}Entity(BaseEntity):
#     pass
