"""
GraphQL Mutations for user-management
"""

from typing import Optional

import strawberry

from app.core.database import SupabaseRepository
from app.graphql.types import (
    AuthResponse,
    CreateUserInput,
    UpdateUserInput,
    UserResponse,
    UserType,
)


@strawberry.type
class Mutation:
    """GraphQL mutations for user-management."""

    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> UserResponse:
        """Create a new user."""
        try:
            repo = SupabaseRepository("users")

            # Check if email already exists
            existing_users = await repo.query(email=input.email)
            if existing_users:
                return UserResponse(
                    success=False,
                    message="User with this email already exists",
                    data=None,
                )

            # Prepare user data (password should be hashed in real implementation)
            user_data = {
                "email": input.email,
                "username": input.username,
                "full_name": input.full_name,
                "is_active": True,
                # Note: In real implementation, hash the password properly
                "password_hash": f"hashed_{input.password}",  # Placeholder
            }

            # Create user in Supabase
            created_data = await repo.create(user_data)

            if not created_data:
                return UserResponse(
                    success=False, message="Failed to create user", data=None
                )

            # Convert to GraphQL type (exclude password)
            user = UserType(
                id=strawberry.ID(created_data["id"]),
                email=created_data["email"],
                username=created_data.get("username"),
                full_name=created_data.get("full_name"),
                is_active=created_data.get("is_active", True),
                created_at=created_data["created_at"],
                updated_at=created_data.get("updated_at"),
            )

            return UserResponse(
                success=True, message="User created successfully", data=user
            )

        except Exception as e:
            return UserResponse(
                success=False, message=f"Error creating user: {str(e)}", data=None
            )

    @strawberry.mutation
    async def update_user(
        self, id: strawberry.ID, input: UpdateUserInput
    ) -> UserResponse:
        """Update an existing user."""
        try:
            repo = SupabaseRepository("users")

            # Check if user exists
            existing = await repo.get_by_id(str(id))
            if not existing:
                return UserResponse(
                    success=False, message=f"User with ID {id} not found", data=None
                )

            # Prepare update data
            update_data = {}
            if input.email is not None:
                # Check if new email already exists
                existing_users = await repo.query(email=input.email)
                if existing_users and existing_users[0]["id"] != str(id):
                    return UserResponse(
                        success=False,
                        message="Email already in use by another user",
                        data=None,
                    )
                update_data["email"] = input.email

            if input.username is not None:
                update_data["username"] = input.username
            if input.full_name is not None:
                update_data["full_name"] = input.full_name
            if input.is_active is not None:
                update_data["is_active"] = input.is_active

            if not update_data:
                return UserResponse(
                    success=False, message="No fields to update", data=None
                )

            # Update user in Supabase
            updated_data = await repo.update(str(id), update_data)

            if not updated_data:
                return UserResponse(
                    success=False, message="Failed to update user", data=None
                )

            # Convert to GraphQL type
            user = UserType(
                id=strawberry.ID(updated_data["id"]),
                email=updated_data["email"],
                username=updated_data.get("username"),
                full_name=updated_data.get("full_name"),
                is_active=updated_data.get("is_active", True),
                created_at=updated_data["created_at"],
                updated_at=updated_data.get("updated_at"),
            )

            return UserResponse(
                success=True, message="User updated successfully", data=user
            )

        except Exception as e:
            return UserResponse(
                success=False, message=f"Error updating user: {str(e)}", data=None
            )

    @strawberry.mutation
    async def delete_user(self, id: strawberry.ID) -> UserResponse:
        """Delete a user (soft delete by setting is_active to False)."""
        try:
            repo = SupabaseRepository("users")

            # Check if user exists
            existing = await repo.get_by_id(str(id))
            if not existing:
                return UserResponse(
                    success=False, message=f"User with ID {id} not found", data=None
                )

            # Soft delete by setting is_active to False
            updated_data = await repo.update(str(id), {"is_active": False})

            return UserResponse(
                success=True, message="User deactivated successfully", data=None
            )

        except Exception as e:
            return UserResponse(
                success=False, message=f"Error deleting user: {str(e)}", data=None
            )
