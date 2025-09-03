"""
Analytics Service - Main Application
DUAL API ARCHITECTURE: FastAPI (REST) + Strawberry GraphQL
Following GymBro microservice template v1.0
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.config import settings
from app.graphql_schema import schema


# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with startup and shutdown handlers"""
    logger.info(f"🏗️ Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    logger.info(f"📊 Analytics Service with time-series data")
    logger.info(f"🌐 DUAL API: REST + GraphQL Federation")
    
    # Database initialization would go here
    # await init_database()
    
    # Redis cache initialization would go here
    # await init_redis()
    
    logger.info("✅ Analytics Service started successfully")
    
    yield
    
    logger.info("🛑 Analytics Service shutting down...")


def create_app() -> FastAPI:
    """Factory function to create FastAPI application"""
    
    # Create FastAPI app following template
    app = FastAPI(
        title="GymBro Analytics Service",
        description="Time-series fitness analytics with DUAL API architecture",
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS middleware - standard configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Health check endpoints - MANDATORY
    @app.get("/health")
    async def health():
        """Basic health check endpoint"""
        from app.models import HealthCheck
        return HealthCheck()
    
    @app.get("/ping")
    async def ping():
        """Minimal ping endpoint"""
        return {"ping": "pong", "service": settings.SERVICE_NAME}
    
    @app.get("/")
    async def root():
        """Root endpoint with service information"""
        return {
            "service": settings.SERVICE_NAME,
            "version": settings.VERSION,
            "description": "Time-series fitness analytics",
            "apis": {
                "rest": "/api/v1",
                "graphql": "/graphql",
                "docs": "/docs",
                "health": "/health"
            }
        }
    
    # GraphQL endpoint - APOLLO FEDERATION READY
    graphql_app = GraphQLRouter(
        schema,
        graphiql=True,
        path="/graphql"
    )
    app.include_router(graphql_app, prefix="/graphql")
    
    # REST API endpoints
    from app.api.v1.endpoints import router as api_router
    app.include_router(api_router, prefix="/api/v1")
    
    # Apollo Federation service endpoint
    @app.get("/_service")
    async def federation_service():
        """Apollo Federation service definition"""
        from strawberry.printer import print_schema
        
        sdl = print_schema(schema)
        
        # Add Federation directives
        federation_sdl = f"""
        scalar DateTime
        
        # Analytics Service Schema
        {sdl}
        
        # Federation extensions
        extend type User @key(fields: "id") {{
            id: ID! @external
            analytics: UserAnalytics
        }}
        
        type UserAnalytics {{
            dashboard: UserDashboard
            dailyStats(timeRange: TimeRangeType): [DailyStatsRecord!]!
            trends(metric: String!, days: Int = 30): [DailyStatsRecord!]!
        }}
        """
        
        return {"sdl": federation_sdl}
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=["app"] if settings.DEBUG else None,
        log_level=settings.LOG_LEVEL.lower()
    )
