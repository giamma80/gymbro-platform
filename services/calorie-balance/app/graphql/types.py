"""
GraphQL Types for calorie-balance
"""

import strawberry
from typing import List, Optional
from datetime import datetime


@strawberry.federation.type(keys=["id"])
class UcalorieUbalanceType:
    """GraphQL type for calorie-balance entity with federation support."""
    
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
class CreateUcalorieUbalanceInput:
    """Input type for creating calorie-balance."""
    
    name: str
    description: Optional[str] = None


@strawberry.input
class UpdateUcalorieUbalanceInput:
    """Input type for updating calorie-balance."""
    
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.type
class UcalorieUbalanceResponse:
    """Response type for calorie-balance operations."""
    
    success: bool
    message: str
    data: Optional[UcalorieUbalanceType] = None


@strawberry.type
class UcalorieUbalanceListResponse:
    """Response type for calorie-balance list operations."""
    
    success: bool
    message: str
    data: List[UcalorieUbalanceType]
    total: int
