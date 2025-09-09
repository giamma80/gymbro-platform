"""
API Router - Supabase Client Template
Service: {service-name}
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, items

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
