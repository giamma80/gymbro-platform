# 📦 PostgreSQL Direct Template - pyproject.toml

```toml
[tool.poetry]
name = "nutrifit-{service-name}"
version = "1.0.0"
description = "NutriFit {Service Name} Microservice with PostgreSQL Direct"
authors = ["NutriFit Team <dev@nutrifit.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"

# 🔥 Core Framework
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# 🗄️ PostgreSQL Direct Connection
asyncpg = "^0.29.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.0"}
alembic = "^1.12.0"

# 🤖 AI/ML Extensions (Optional for ai-coach service)
pgvector = {version = "^0.2.0", optional = true}
numpy = {version = "^1.24.0", optional = true}

# 🔐 Authentication & Security
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"

# 📊 Data Validation & Serialization
email-validator = "^2.1.0"
python-dateutil = "^2.8.2"

# 🔄 HTTP & External APIs
httpx = "^0.25.0"
aiofiles = "^23.2.1"

# 📈 Performance & Caching
redis = "^5.0.0"
aioredis = "^2.0.0"

# 📝 Logging & Monitoring
structlog = "^23.2.0"
rich = "^13.7.0"

# 🧪 Testing (Optional)
pytest = {version = "^7.4.0", optional = true}
pytest-asyncio = {version = "^0.21.0", optional = true}
httpx = {version = "^0.25.0", optional = true}
pytest-postgresql = {version = "^5.0.0", optional = true}

[tool.poetry.extras]
test = ["pytest", "pytest-asyncio", "httpx", "pytest-postgresql"]
ai = ["pgvector", "numpy"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.alembic]
script_location = "alembic"
prepend_sys_path = ["."]
version_path_separator = "os"

sqlalchemy.url = "postgresql+asyncpg://postgres:password@localhost:5432/test_db"
```

# 🔧 Configuration Template - config.py

```python
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuration settings for PostgreSQL Direct microservice"""
    
    # 🗄️ Database Configuration
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    database_pool_pre_ping: bool = True
    
    # 🚀 FastAPI Configuration
    app_name: str = "NutriFit {Service Name} Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 🔐 Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 🌐 CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",  # Flutter dev
        "https://*.netlify.app",  # Frontend deployment
        "https://*.render.com"    # Backend services
    ]
    
    # 📊 Redis Cache Configuration
    redis_url: Optional[str] = None
    cache_ttl: int = 300  # 5 minutes default
    
    # 📝 Logging
    log_level: str = "INFO"
    
    # 🤖 AI Configuration (for ai-coach service)
    openai_api_key: Optional[str] = None
    vector_dimension: int = 1536  # OpenAI embeddings
    
    @property
    def async_database_url(self) -> str:
        """Convert database URL to async format"""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
```

# 🗄️ Database Client Template - database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func, text
from config import settings
from typing import Optional, Dict, Any, List, AsyncGenerator
import structlog
import uuid
from datetime import datetime

logger = structlog.get_logger(__name__)

# Database Base
class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Database Engine
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=settings.database_pool_pre_ping
)

# Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class DatabaseService:
    """High-performance database service with connection pooling"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with proper cleanup"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health"""
        try:
            async with self.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
                
                # Check connection pool status
                pool = self.engine.pool
                return {
                    "status": "healthy",
                    "database_connected": True,
                    "pool_size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                }
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "database_connected": False,
                "error": str(e)
            }
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query with parameters"""
        try:
            async with self.session_factory() as session:
                result = await session.execute(text(query), params or {})
                
                # Convert result to list of dicts
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error("Query execution failed", query=query, error=str(e))
            raise
    
    async def execute_analytics_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute complex analytics query with optimization"""
        try:
            async with self.session_factory() as session:
                # Set session-level optimizations for analytics
                await session.execute(text("SET work_mem = '256MB'"))
                await session.execute(text("SET enable_hashjoin = ON"))
                await session.execute(text("SET enable_mergejoin = ON"))
                
                result = await session.execute(text(query), params or {})
                columns = result.keys()
                rows = result.fetchall()
                
                logger.info("Analytics query executed", 
                          query_hash=hash(query), 
                          rows_returned=len(rows))
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error("Analytics query failed", query=query, error=str(e))
            raise
    
    async def bulk_insert(self, table_name: str, records: List[Dict[str, Any]]) -> int:
        """High-performance bulk insert"""
        if not records:
            return 0
            
        try:
            async with self.session_factory() as session:
                # Use COPY for maximum performance with large datasets
                columns = list(records[0].keys())
                placeholders = ", ".join([f":{col}" for col in columns])
                
                query = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({placeholders})
                """
                
                await session.execute(text(query), records)
                await session.commit()
                
                logger.info("Bulk insert completed", 
                          table=table_name, 
                          records_count=len(records))
                
                return len(records)
                
        except Exception as e:
            logger.error("Bulk insert failed", 
                        table=table_name, 
                        records_count=len(records), 
                        error=str(e))
            raise

# Vector Operations (for AI services)
class VectorService:
    """Vector operations using pgvector extension"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def create_embedding(self, content: str, embedding: List[float], metadata: Dict[str, Any] = None) -> str:
        """Store content with vector embedding"""
        record_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO knowledge_base (id, content, embedding, metadata, created_at)
            VALUES (:id, :content, :embedding, :metadata, :created_at)
        """
        
        params = {
            "id": record_id,
            "content": content,
            "embedding": f"[{','.join(map(str, embedding))}]",  # pgvector format
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        }
        
        await self.db.execute_query(query, params)
        return record_id
    
    async def similarity_search(self, query_embedding: List[float], limit: int = 10, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        query = """
            SELECT 
                id, content, metadata,
                1 - (embedding <=> :query_embedding) as similarity
            FROM knowledge_base
            WHERE 1 - (embedding <=> :query_embedding) > :threshold
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """
        
        params = {
            "query_embedding": f"[{','.join(map(str, query_embedding))}]",
            "threshold": threshold,
            "limit": limit
        }
        
        return await self.db.execute_query(query, params)

# Global service instances
db_service = DatabaseService()
vector_service = VectorService(db_service)

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database dependency for FastAPI endpoints"""
    async for session in db_service.get_session():
        yield session
```

# 🔧 Models Template - models.py

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Float, JSON, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from database import Base
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Example models for different service types

# For calorie-balance service
class CalorieEvent(BaseModel):
    __tablename__ = "calorie_events"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    calories_consumed: Mapped[int] = mapped_column(Integer, nullable=False)
    calories_burned_activity: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned_bmr: Mapped[int] = mapped_column(Integer, nullable=False)
    net_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Performance optimization
    date_partition: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    hour_partition: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 0-23
    
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

# For ai-coach service with vector support
class KnowledgeBase(BaseModel):
    __tablename__ = "knowledge_base"
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=False)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Vector search optimization
    # Note: In real implementation, use pgvector extension
    # embedding: Mapped[Vector] = mapped_column(Vector(1536))  # for pgvector

class ConversationSession(BaseModel):
    __tablename__ = "conversation_sessions"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    session_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
```

# 🚀 Main App Template - main.py

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from database import db_service, get_db
from typing import List, Dict, Any, Optional
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="High-performance PostgreSQL microservice for NutriFit Platform",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": settings.app_name}

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe with database check"""
    health = await db_service.health_check()
    return health

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "service": settings.app_name}

# Analytics endpoints (example for calorie-balance service)
@app.get("/api/v1/analytics/user-trends")
async def get_user_calorie_trends(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get user calorie trends with optimized analytics query"""
    query = """
        SELECT 
            DATE_TRUNC('day', created_at) as date,
            AVG(calories_consumed) as avg_calories_consumed,
            AVG(calories_burned_activity) as avg_calories_burned,
            AVG(net_calories) as avg_net_calories,
            COUNT(*) as events_count
        FROM calorie_events 
        WHERE user_id = :user_id 
          AND created_at >= NOW() - INTERVAL '%s days'
        GROUP BY DATE_TRUNC('day', created_at)
        ORDER BY date DESC
    """ % days
    
    result = await db_service.execute_analytics_query(query, {"user_id": user_id})
    return {"user_id": user_id, "trends": result}

@app.post("/api/v1/bulk-events")
async def bulk_create_events(
    events: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db)
):
    """High-performance bulk event creation"""
    if len(events) > 1000:
        raise HTTPException(status_code=400, detail="Too many events (max 1000)")
    
    # Add date partitioning for performance
    for event in events:
        if 'created_at' in event:
            dt = event['created_at']
            event['date_partition'] = dt.strftime('%Y-%m-%d')
            event['hour_partition'] = dt.hour
    
    count = await db_service.bulk_insert("calorie_events", events)
    return {"success": True, "inserted_count": count}

# Vector search endpoint (example for ai-coach service)
@app.post("/api/v1/knowledge/search")
async def search_knowledge(
    query: str,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Vector similarity search in knowledge base"""
    # In real implementation, you would:
    # 1. Generate embedding for query using OpenAI/other service
    # 2. Perform vector search using pgvector
    
    # Placeholder implementation
    search_query = """
        SELECT id, content, metadata, 
               similarity(content, :query) as relevance
        FROM knowledge_base
        WHERE content ILIKE '%' || :query || '%'
        ORDER BY relevance DESC
        LIMIT :limit
    """
    
    result = await db_service.execute_query(search_query, {
        "query": query,
        "limit": limit
    })
    
    return {"query": query, "results": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
```

# 📦 Environment Template - .env.example

```bash
# 🗄️ PostgreSQL Direct Configuration
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
DATABASE_POOL_PRE_PING=true

# 🔐 Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 🚀 FastAPI Configuration
APP_NAME=NutriFit Service Name Service
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# 📊 Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# 🤖 AI Configuration (for ai-coach service)
OPENAI_API_KEY=your-openai-api-key
VECTOR_DIMENSION=1536

# 🌐 CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://app.nutrifit.com
```

# 🛠️ Alembic Migration Template - alembic/versions/001_initial_schema.sql

```sql
-- Initial schema for PostgreSQL Direct service
-- Revision ID: 001
-- Create Date: 2025-09-07

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For similarity search
-- CREATE EXTENSION IF NOT EXISTS "vector";  -- For AI services with pgvector

-- Create main tables with partitioning for performance
CREATE TABLE calorie_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    calories_consumed INTEGER NOT NULL,
    calories_burned_activity INTEGER DEFAULT 0,
    calories_burned_bmr INTEGER NOT NULL,
    net_calories INTEGER NOT NULL,
    date_partition VARCHAR(10) NOT NULL,  -- YYYY-MM-DD for partitioning
    hour_partition INTEGER NOT NULL CHECK (hour_partition >= 0 AND hour_partition <= 23),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create partitions for current and next months
CREATE TABLE calorie_events_current PARTITION OF calorie_events
    FOR VALUES FROM (DATE_TRUNC('month', CURRENT_DATE)) 
    TO (DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month'));

CREATE TABLE calorie_events_next PARTITION OF calorie_events
    FOR VALUES FROM (DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')) 
    TO (DATE_TRUNC('month', CURRENT_DATE + INTERVAL '2 months'));

-- Indexes for performance
CREATE INDEX idx_calorie_events_user_id ON calorie_events(user_id);
CREATE INDEX idx_calorie_events_date_partition ON calorie_events(date_partition);
CREATE INDEX idx_calorie_events_user_date ON calorie_events(user_id, date_partition);
CREATE INDEX idx_calorie_events_created_at ON calorie_events(created_at);

-- For AI services: Knowledge base with vector search
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding FLOAT[] NOT NULL,  -- Will be VECTOR(1536) with pgvector
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vector similarity index (requires pgvector)
-- CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Full-text search index
CREATE INDEX idx_knowledge_base_content_gin ON knowledge_base USING gin(to_tsvector('english', content));

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_calorie_events_updated_at 
    BEFORE UPDATE ON calorie_events 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at 
    BEFORE UPDATE ON knowledge_base 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```
