"""
GraphQL Queries for user-management
"""

import strawberry
from typing import List, Optional
from uuid import UUID
from app.graphql.types import UserType, UserListResponse
from app.infrastructure.repositories import UserRepository, UserServiceContextRepository


@strawberry.type
class Query:
    """GraphQL queries for user-management."""
    
    @strawberry.field
    async def get_user(self, id: strawberry.ID) -> Optional[UserType]:
        """Get a single user by ID."""
        try:
            user_repo = UserRepository()
            user = await user_repo.get_by_id(UUID(str(id)))
            
            if not user:
                return None
                
            return UserType(
                id=strawberry.ID(str(user.id)),
                email=user.email,
                username=user.username,
                full_name=f"{user.email}",  # Using email as fallback
                is_active=user.status.value == 'active',
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        except Exception:
            return None
    
    @strawberry.field
    async def get_user_by_email(self, email: str) -> Optional[UserType]:
        """Get a user by email address."""
        try:
            user_repo = UserRepository()
            user = await user_repo.get_by_email(email)
            
            if not user:
                return None
                
            return UserType(
                id=strawberry.ID(str(user.id)),
                email=user.email,
                username=user.username,
                full_name=f"{user.email}",  # Using email as fallback
                is_active=user.status.value == 'active',
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except Exception:
            return None
    
    @strawberry.field
    async def list_users(
        self, 
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """List users with pagination and filtering."""
        try:
            user_repo = UserRepository()
            
            # For now, get all users (pagination can be added later)
            users_data = await user_repo.get_all()
            
            # Filter by active status if specified
            if is_active is not None:
                users_data = [
                    user for user in users_data 
                    if (user.status.value == 'active') == is_active
                ]
            
            # Apply pagination
            start = offset or 0
            end = start + (limit or 10)
            paginated_users = users_data[start:end]
            
            # Convert to GraphQL types
            users = [
                UserType(
                    id=strawberry.ID(str(user.id)),
                    email=user.email,
                    username=user.username,
                    full_name=f"{user.email}",  # Using email as fallback
                    is_active=user.status.value == 'active',
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                for user in paginated_users
            ]
            
            return UserListResponse(
                success=True,
                message="Successfully retrieved users",
                data=users,
                total=len(users_data)  # Total count before pagination
            )
            
        except Exception as e:
            return UserListResponse(
                success=False,
                message=f"Error retrieving users: {str(e)}",
                data=[],
                total=0
            )

    @strawberry.field
    async def user_service_context(self, user_id: strawberry.ID) -> Optional[UserType]:
        """Get user service context for GraphQL Federation."""
        try:
            context_repo = UserServiceContextRepository()
            context = await context_repo.get_by_user_id(UUID(str(user_id)))
            
            if not context:
                return None
                
            return UserType(
                id=strawberry.ID(str(context.user_id)),
                email=context.email,
                username=context.username,
                full_name=context.full_name or context.email,
                is_active=context.user_status == 'active',
                created_at=context.created_at,
                updated_at=context.updated_at
            )
            
        except Exception:
            return None
