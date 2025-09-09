"""
GraphQL Mutations for {service-name}
"""

import strawberry
from typing import Optional
from app.graphql.types import {ServiceName}Type, {ServiceName}Response, Create{ServiceName}Input, Update{ServiceName}Input
from app.core.database import SupabaseRepository


@strawberry.type
class Mutation:
    """GraphQL mutations for {service-name}."""
    
    @strawberry.mutation
    async def create_{service_name}(self, input: Create{ServiceName}Input) -> {ServiceName}Response:
        """Create a new {service-name}."""
        try:
            # Initialize repository
            repo = SupabaseRepository("{service_name}")
            
            # Prepare data
            data = {
                "name": input.name,
                "description": input.description
            }
            
            # Create in Supabase
            created_data = await repo.create(data)
            
            if not created_data:
                return {ServiceName}Response(
                    success=False,
                    message="Failed to create {service_name}",
                    data=None
                )
            
            # Convert to GraphQL type
            created_item = {ServiceName}Type(
                id=strawberry.ID(created_data["id"]),
                name=created_data["name"],
                description=created_data.get("description"),
                created_at=created_data["created_at"],
                updated_at=created_data.get("updated_at")
            )
            
            return {ServiceName}Response(
                success=True,
                message="Successfully created {service_name}",
                data=created_item
            )
            
        except Exception as e:
            return {ServiceName}Response(
                success=False,
                message=f"Error creating {service_name}: {str(e)}",
                data=None
            )
    
    @strawberry.mutation
    async def update_{service_name}(
        self, 
        id: strawberry.ID, 
        input: Update{ServiceName}Input
    ) -> {ServiceName}Response:
        """Update an existing {service-name}."""
        try:
            # Initialize repository
            repo = SupabaseRepository("{service_name}")
            
            # Check if exists
            existing = await repo.get_by_id(str(id))
            if not existing:
                return {ServiceName}Response(
                    success=False,
                    message=f"{ServiceName} with ID {id} not found",
                    data=None
                )
            
            # Prepare update data
            update_data = {}
            if input.name is not None:
                update_data["name"] = input.name
            if input.description is not None:
                update_data["description"] = input.description
            
            if not update_data:
                return {ServiceName}Response(
                    success=False,
                    message="No fields to update",
                    data=None
                )
            
            # Update in Supabase
            updated_data = await repo.update(str(id), update_data)
            
            if not updated_data:
                return {ServiceName}Response(
                    success=False,
                    message="Failed to update {service_name}",
                    data=None
                )
            
            # Convert to GraphQL type
            updated_item = {ServiceName}Type(
                id=strawberry.ID(updated_data["id"]),
                name=updated_data["name"],
                description=updated_data.get("description"),
                created_at=updated_data["created_at"],
                updated_at=updated_data.get("updated_at")
            )
            
            return {ServiceName}Response(
                success=True,
                message="Successfully updated {service_name}",
                data=updated_item
            )
            
        except Exception as e:
            return {ServiceName}Response(
                success=False,
                message=f"Error updating {service_name}: {str(e)}",
                data=None
            )
    
    @strawberry.mutation
    async def delete_{service_name}(self, id: strawberry.ID) -> {ServiceName}Response:
        """Delete a {service-name}."""
        try:
            # Initialize repository
            repo = SupabaseRepository("{service_name}")
            
            # Check if exists
            existing = await repo.get_by_id(str(id))
            if not existing:
                return {ServiceName}Response(
                    success=False,
                    message=f"{ServiceName} with ID {id} not found",
                    data=None
                )
            
            # Delete from Supabase
            await repo.delete(str(id))
            
            return {ServiceName}Response(
                success=True,
                message="Successfully deleted {service_name}",
                data=None
            )
            
        except Exception as e:
            return {ServiceName}Response(
                success=False,
                message=f"Error deleting {service_name}: {str(e)}",
                data=None
            )
