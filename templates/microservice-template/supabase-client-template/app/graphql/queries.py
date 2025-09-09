"""
GraphQL Queries for {service-name}
"""

import strawberry
from typing import List, Optional
from app.graphql.types import {ServiceName}Type, {ServiceName}ListResponse
from app.core.database import SupabaseRepository


@strawberry.type
class Query:
    """GraphQL queries for {service-name}."""
    
    @strawberry.field
    async def get_{service_name}(self, id: strawberry.ID) -> Optional[{ServiceName}Type]:
        """Get a single {service-name} by ID."""
        # Initialize repository
        repo = SupabaseRepository("{service_name}")
        
        # Fetch data from Supabase
        data = await repo.get_by_id(str(id))
        
        if not data:
            return None
            
        return {ServiceName}Type(
            id=strawberry.ID(data["id"]),
            name=data["name"],
            description=data.get("description"),
            created_at=data["created_at"],
            updated_at=data.get("updated_at")
        )
    
    @strawberry.field
    async def list_{service_name}s(
        self, 
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> {ServiceName}ListResponse:
        """List {service-name}s with pagination."""
        try:
            # Initialize repository
            repo = SupabaseRepository("{service_name}")
            
            # Fetch data from Supabase
            data = await repo.get_all(limit=limit, offset=offset)
            
            # Convert to GraphQL types
            items = [
                {ServiceName}Type(
                    id=strawberry.ID(item["id"]),
                    name=item["name"],
                    description=item.get("description"),
                    created_at=item["created_at"],
                    updated_at=item.get("updated_at")
                )
                for item in data
            ]
            
            return {ServiceName}ListResponse(
                success=True,
                message="Successfully retrieved {service_name}s",
                data=items,
                total=len(items)
            )
            
        except Exception as e:
            return {ServiceName}ListResponse(
                success=False,
                message=f"Error retrieving {service_name}s: {str(e)}",
                data=[],
                total=0
            )
