"""
GraphQL Queries for calorie-balance
"""

import strawberry
from typing import List, Optional
from app.graphql.types import UcalorieUbalanceType, UcalorieUbalanceListResponse
from app.core.database import SupabaseRepository


@strawberry.type
class Query:
    """GraphQL queries for calorie-balance."""
    
    @strawberry.field
    async def get_calorie_balance(self, id: strawberry.ID) -> Optional[UcalorieUbalanceType]:
        """Get a single calorie-balance by ID."""
        # Initialize repository
        repo = SupabaseRepository("calorie_balance")
        
        # Fetch data from Supabase
        data = await repo.get_by_id(str(id))
        
        if not data:
            return None
            
        return UcalorieUbalanceType(
            id=strawberry.ID(data["id"]),
            name=data["name"],
            description=data.get("description"),
            created_at=data["created_at"],
            updated_at=data.get("updated_at")
        )
    
    @strawberry.field
    async def list_calorie_balances(
        self, 
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> UcalorieUbalanceListResponse:
        """List calorie-balances with pagination."""
        try:
            # Initialize repository
            repo = SupabaseRepository("calorie_balance")
            
            # Fetch data from Supabase
            data = await repo.get_all(limit=limit, offset=offset)
            
            # Convert to GraphQL types
            items = [
                UcalorieUbalanceType(
                    id=strawberry.ID(item["id"]),
                    name=item["name"],
                    description=item.get("description"),
                    created_at=item["created_at"],
                    updated_at=item.get("updated_at")
                )
                for item in data
            ]
            
            return UcalorieUbalanceListResponse(
                success=True,
                message="Successfully retrieved calorie_balances",
                data=items,
                total=len(items)
            )
            
        except Exception as e:
            return UcalorieUbalanceListResponse(
                success=False,
                message=f"Error retrieving calorie_balances: {str(e)}",
                data=[],
                total=0
            )
