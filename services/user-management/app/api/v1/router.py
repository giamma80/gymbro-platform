"""
API Router - User Management Service
Service: user-management
Schema: user_management
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.api.v1 import users

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="", tags=["users"])
