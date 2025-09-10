"""
API Router - Supabase Client Template
Service: {service-name}
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, items
from app.api.v1 import entities

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])

# Optional auth router (uncomment if auth is needed)
# from app.api.v1 import auth
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
