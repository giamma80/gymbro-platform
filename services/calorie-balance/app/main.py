"""
FastAPI Application Template - Supabase Client
Service: calorie-balance
Connection Type: Supabase Client (Real-time, CRUD operations)
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import check_supabase_connection, create_supabase_client
from app.core.exceptions import setup_exception_handlers
from app.core.logging import configure_logging

# from app.api.v1.auth import router as auth_router  # Uncomment if auth is needed
from app.graphql import graphql_router

# Lazy settings access: avoid early environment validation at import time
def _settings():  # internal helper
    return get_settings()


logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging with correlation ID."""

    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )

        # Bind to logger context
        s = _settings()
        logger = structlog.get_logger().bind(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
            service=s.service_name,
        )

        start_time = time.time()
        logger.info("Request started")

        # Process request
        response = await call_next(request)

        # Log completion
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Correlation-ID"] = correlation_id

        logger.info(
            "Request completed",
            status_code=response.status_code,
            process_time=process_time,
        )

        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    logger.info("Starting calorie-balance service")

    # Initialize Supabase client
    supabase_client = create_supabase_client()
    app.state.supabase = supabase_client

    # Test connection
    is_connected = await check_supabase_connection()
    if not is_connected:
        logger.error("Failed to connect to Supabase")
        raise HTTPException(
            status_code=503, detail="Database connection failed"
        )

    logger.info("Service startup complete")

    yield

    # Cleanup
    logger.info("Shutting down calorie-balance service")


def create_application() -> FastAPI:
    """Create FastAPI application with middleware and routing."""

    # Configure logging first
    configure_logging()

    s = _settings()
    app = FastAPI(
        title="NutriFit calorie-balance",
        description=(
            "NutriFit calorie-balance microservice with Supabase integration"
        ),
        version="1.0.0",
        openapi_url="/api/v1/openapi.json"
        if s.environment != "production"
        else None,
        docs_url="/docs" if s.environment != "production" else None,
        redoc_url="/redoc" if s.environment != "production" else None,
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handling
    setup_exception_handlers(app)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    # GraphQL endpoint
    app.include_router(graphql_router, prefix="", tags=["GraphQL"])

    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Basic health check."""
        s = _settings()
        return {
            "status": "healthy",
            "service": s.service_name,
            "timestamp": time.time(),
        }

    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check with Supabase connectivity."""
        try:
            is_ready = await check_supabase_connection()

            if is_ready:
                s = _settings()
                return {
                    "status": "ready",
                    "service": s.service_name,
                    "checks": {"supabase": "connected"},
                }
            else:
                return Response(
                    content=(
                        '{"status": "not_ready", "error": "Supabase connection failed"}'
                    ),
                    status_code=503,
                    media_type="application/json",
                )

        except Exception as e:
            logger.error("Readiness check failed", error=str(e))
            return Response(
                content=f'{{"status": "not_ready", "error": "{str(e)}"}}',
                status_code=503,
                media_type="application/json",
            )

    @app.get("/health/live")
    async def liveness_check():
        """Liveness check for Kubernetes."""
        s = _settings()
        return {"status": "alive", "service": s.service_name}

    return app


# Create app instance
app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=_settings().environment == "development",
        access_log=False,  # We handle logging in middleware
    )
