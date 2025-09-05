from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from .core.config import settings
from .core.database import init_db, close_db
from .core.logging import configure_logging
from .api.routers import health, users, goals, balance, calorie_event


# Configure logging
configure_logging(debug=settings.debug)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("Starting Calorie Balance Service", version="1.3.0")
    
    # Skip database initialization for now since tables exist
    # await init_db()
    
    yield
    
    logger.info("Shutting down Calorie Balance Service")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Microservizio per il calcolo e tracking dell'equilibrio calorico giornaliero",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://app.gymbro.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Calorie Goals"])
app.include_router(balance.router, prefix="/api/v1/balance", tags=["Daily Balance"])
app.include_router(calorie_event.router, prefix="/api/v1/calorie-event", tags=["Eventi Calorici"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
