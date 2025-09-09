"""
GraphQL Types for {service-name}
"""

import strawberry
from typing import List, Optional
from datetime import datetime


@strawberry.federation.type(keys=["id"])
class {ServiceName}Type:
    """GraphQL type for {service-name} entity with federation support."""
    
    id: strawberry.ID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve entity reference for Apollo Federation."""
        # This will be implemented with actual data fetching
        # from your repository/service layer
        pass


@strawberry.input
class Create{ServiceName}Input:
    """Input type for creating {service-name}."""
    
    name: str
    description: Optional[str] = None


@strawberry.input
class Update{ServiceName}Input:
    """Input type for updating {service-name}."""
    
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.type
class {ServiceName}Response:
    """Response type for {service-name} operations."""
    
    success: bool
    message: str
    data: Optional[{ServiceName}Type] = None


@strawberry.type
class {ServiceName}ListResponse:
    """Response type for {service-name} list operations."""
    
    success: bool
    message: str
    data: List[{ServiceName}Type]
    total: int
