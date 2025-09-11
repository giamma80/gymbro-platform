"""
Health Endpoints - Supabase Client Template
Service: calorie-balance
"""

from fastapi import APIRouter, Depends
from app.core.database import check_supabase_connection
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/")
async def health_status():
    """Basic health status."""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health():
    """Detailed health check with dependencies."""
    supabase_connected = await check_supabase_connection()
    
    return {
        "status": "healthy" if supabase_connected else "degraded",
        "service": settings.service_name,
        "version": "1.0.0",
        "checks": {
            "supabase": "connected" if supabase_connected else "disconnected"
        },
        "environment": settings.environment,
        "debug": settings.debug
    }
