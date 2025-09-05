from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from uuid import uuid4
import structlog
from .config import settings

logger = structlog.get_logger(__name__)

# SQLAlchemy async engine with Supabase-compatible settings
# Using UUID-based prepared statement names for PgBouncer transaction mode compatibility
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,  # Required for transaction mode compatibility
    # PgBouncer transaction mode compatibility with UUID prepared statements
    connect_args={
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4().hex}__",
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "server_settings": {
            "application_name": "calorie_balance_service",
            "jit": "off",
            "statement_timeout": "60000",
            "idle_in_transaction_session_timeout": "60000",
        }
    },
    pool_pre_ping=False,  # Disable to avoid prepared statement conflicts
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create tables if needed"""
    try:
        # Since we already have tables, we can skip the table creation
        # and just test the connection
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            await session.commit()
            
        logger.info("Database connection verified successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
        raise


async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
