#!/usr/bin/env python3
"""
Database setup script for Calorie Balance Service
Creates tables specific to calorie balance domain
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables for proper import
os.environ.setdefault('PYTHONPATH', str(current_dir))

try:
    from app.core.database import engine
    from app.core.config import settings
    from app.infrastructure.database.models import Base
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)hon3
"""
Database setup script for Calorie Balance Service
Creates all tables in Supabase database
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.database import init_db, engine
from app.core.config import settings
from app.infrastructure.database.models import Base
import structlog

logger = structlog.get_logger(__name__)


async def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...", database_url=settings.database_url[:50] + "...")
        
        # Initialize database - this will create all tables
        await init_db()
        
        logger.info("✅ Database tables created successfully!")
        
        # Print created tables info
        async with engine.begin() as conn:
            result = await conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in result.fetchall()]
            logger.info("📊 Created tables:", tables=tables)
            
        return True
        
    except Exception as e:
        logger.error("❌ Failed to create database tables", error=str(e))
        return False


async def test_connection():
    """Test database connection"""
    try:
        logger.info("Testing database connection...")
        
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version();")
            version = result.fetchone()[0]
            logger.info("✅ Database connection successful!", postgresql_version=version)
            
        return True
        
    except Exception as e:
        logger.error("❌ Database connection failed", error=str(e))
        logger.error("🔧 Check your DATABASE_URL in .env file")
        return False


async def main():
    """Main setup function"""
    print("🚀 NutriFit Calorie Balance Database Setup")
    print("=" * 50)
    
    # Test connection first
    if not await test_connection():
        return False
    
    print()
    
    # Create tables
    if not await create_tables():
        return False
    
    print()
    print("🎉 Database setup completed successfully!")
    print("📝 You can now start the service with: ./start-dev.sh")
    
    return True


if __name__ == "__main__":
    # Configure basic logging for setup
    import structlog
    structlog.configure(
        processors=[
            structlog.dev.ConsoleRenderer(colors=True)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
