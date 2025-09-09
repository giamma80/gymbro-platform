"""
GraphQL Types for user-management
"""

import strawberry
from typing import List, Optional
from datetime import datetime


@strawberry.federation.type(keys=["id"])
class UserType:
    """GraphQL type for user entity with federation support."""
    
    id: strawberry.ID
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve user reference for Apollo Federation."""
        # This will be implemented with actual user fetching
        from app.core.database import SupabaseRepository
        repo = SupabaseRepository("users")
        # TODO: Implement async reference resolution
        pass


@strawberry.input
class CreateUserInput:
    """Input type for creating user."""
    
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: str


@strawberry.input
class UpdateUserInput:
    """Input type for updating user."""
    
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.type
class UserResponse:
    """Response type for user operations."""
    
    success: bool
    message: str
    data: Optional[UserType] = None


@strawberry.type
class UserListResponse:
    """Response type for user list operations."""
    
    success: bool
    message: str
    data: List[UserType]
    total: int


@strawberry.type
class AuthResponse:
    """Response type for authentication operations."""
    
    success: bool
    message: str
    access_token: Optional[str] = None
    user: Optional[UserType] = None
