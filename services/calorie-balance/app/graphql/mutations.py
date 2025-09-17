"""
GraphQL Mutations for calorie-balance
"""

from typing import Optional

import strawberry

from app.core.database import SupabaseRepository
from app.graphql.types import (
    CreateUcalorieUbalanceInput,
    UcalorieUbalanceResponse,
    UcalorieUbalanceType,
    UpdateUcalorieUbalanceInput,
)


@strawberry.type
class Mutation:
    """GraphQL mutations for calorie-balance."""

    @strawberry.mutation
    async def create_calorie_balance(
        self, input: CreateUcalorieUbalanceInput
    ) -> UcalorieUbalanceResponse:
        """Create a new calorie-balance."""
        try:
            # Initialize repository
            repo = SupabaseRepository("calorie_balance")

            # Prepare data
            data = {"name": input.name, "description": input.description}

            # Create in Supabase
            created_data = await repo.create(data)

            if not created_data:
                return UcalorieUbalanceResponse(
                    success=False, message="Failed to create calorie_balance", data=None
                )

            # Convert to GraphQL type
            created_item = UcalorieUbalanceType(
                id=strawberry.ID(created_data["id"]),
                name=created_data["name"],
                description=created_data.get("description"),
                created_at=created_data["created_at"],
                updated_at=created_data.get("updated_at"),
            )

            return UcalorieUbalanceResponse(
                success=True,
                message="Successfully created calorie_balance",
                data=created_item,
            )

        except Exception as e:
            return UcalorieUbalanceResponse(
                success=False,
                message=f"Error creating calorie_balance: {str(e)}",
                data=None,
            )

    @strawberry.mutation
    async def update_calorie_balance(
        self, id: strawberry.ID, input: UpdateUcalorieUbalanceInput
    ) -> UcalorieUbalanceResponse:
        """Update an existing calorie-balance."""
        try:
            # Initialize repository
            repo = SupabaseRepository("calorie_balance")

            # Check if exists
            existing = await repo.get_by_id(str(id))
            if not existing:
                return UcalorieUbalanceResponse(
                    success=False,
                    message=f"UcalorieUbalance with ID {id} not found",
                    data=None,
                )

            # Prepare update data
            update_data = {}
            if input.name is not None:
                update_data["name"] = input.name
            if input.description is not None:
                update_data["description"] = input.description

            if not update_data:
                return UcalorieUbalanceResponse(
                    success=False, message="No fields to update", data=None
                )

            # Update in Supabase
            updated_data = await repo.update(str(id), update_data)

            if not updated_data:
                return UcalorieUbalanceResponse(
                    success=False, message="Failed to update calorie_balance", data=None
                )

            # Convert to GraphQL type
            updated_item = UcalorieUbalanceType(
                id=strawberry.ID(updated_data["id"]),
                name=updated_data["name"],
                description=updated_data.get("description"),
                created_at=updated_data["created_at"],
                updated_at=updated_data.get("updated_at"),
            )

            return UcalorieUbalanceResponse(
                success=True,
                message="Successfully updated calorie_balance",
                data=updated_item,
            )

        except Exception as e:
            return UcalorieUbalanceResponse(
                success=False,
                message=f"Error updating calorie_balance: {str(e)}",
                data=None,
            )

    @strawberry.mutation
    async def delete_calorie_balance(
        self, id: strawberry.ID
    ) -> UcalorieUbalanceResponse:
        """Delete a calorie-balance."""
        try:
            # Initialize repository
            repo = SupabaseRepository("calorie_balance")

            # Check if exists
            existing = await repo.get_by_id(str(id))
            if not existing:
                return UcalorieUbalanceResponse(
                    success=False,
                    message=f"UcalorieUbalance with ID {id} not found",
                    data=None,
                )

            # Delete from Supabase
            await repo.delete(str(id))

            return UcalorieUbalanceResponse(
                success=True, message="Successfully deleted calorie_balance", data=None
            )

        except Exception as e:
            return UcalorieUbalanceResponse(
                success=False,
                message=f"Error deleting calorie_balance: {str(e)}",
                data=None,
            )
