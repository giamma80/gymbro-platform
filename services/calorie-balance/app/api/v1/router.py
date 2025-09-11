"""
API Router - Calorie Balance Service
Event-driven calorie tracking with high-frequency mobile endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, items
from app.api.v1 import entities

# Import the new calorie events router (Priority 1)
from app.api.routers import events, balance, goals

api_router = APIRouter()

# Include Priority 1 endpoints - Event-driven core
api_router.include_router(events.router, tags=["events"])

# Include router for balance and goals
api_router.include_router(balance.router, prefix="/balance", tags=["balance"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])

# Template routers (can be removed in production)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])

# Optional auth router (uncomment if auth is needed)
# from app.api.v1 import auth
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
