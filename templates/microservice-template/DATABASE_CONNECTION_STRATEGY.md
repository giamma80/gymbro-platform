# 🏗️ Database Connection Strategy - NutriFit Platform

**Last Updated:** 7 settembre 2025  
**Strategy:** Hybrid Supabase Client + PostgreSQL Direct

## 📊 Database Connection Matrix

| **Microservizio** | **Connection Type** | **Primary Library** | **Use Case** |
|-------------------|-------------------|------------------|-------------|
| **user-management** | **Supabase Client** | `supabase-py` | Real-time auth, sessions, social login |
| **calorie-balance** | **PostgreSQL Direct** | `asyncpg` + `SQLAlchemy` | Complex analytics, high-performance queries |
| **meal-tracking** | **Supabase Client** | `supabase-py` | Real-time food logging, mobile sync |
| **health-monitor** | **Supabase Client** | `supabase-py` | Real-time HealthKit streaming |
| **notifications** | **Supabase Client** | `supabase-py` | Real-time push notifications |
| **ai-coach** | **PostgreSQL Direct** | `asyncpg` + `pgvector` | Vector search, ML queries |

---

## 🔧 Connection Templates

### **Template A: Supabase Client Connection**

**Use for:** Real-time features, authentication, mobile sync

```python
# pyproject.toml dependencies
supabase = "^2.0.0"
python-dotenv = "^1.0.0"

# config.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseConfig:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
    def get_client(self) -> Client:
        return create_client(self.url, self.key)
        
    def get_service_client(self) -> Client:
        return create_client(self.url, self.service_key)

# database.py
from config import SupabaseConfig

config = SupabaseConfig()
supabase = config.get_client()
supabase_admin = config.get_service_client()

# Usage examples
async def create_user(user_data: dict):
    result = supabase.table('users').insert(user_data).execute()
    return result.data

async def get_user_realtime(user_id: str):
    # Real-time subscription
    supabase.table('users').on('UPDATE', handle_user_update).filter('id', 'eq', user_id).subscribe()

async def authenticate_user(email: str, password: str):
    auth_response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    return auth_response
```

### **Template B: PostgreSQL Direct Connection**

**Use for:** Complex analytics, high-performance queries, vector operations

```python
# pyproject.toml dependencies
asyncpg = "^0.29.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
pgvector = "^0.2.0"  # for AI services

# config.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class PostgreSQLConfig:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        # Supabase PostgreSQL connection
        # Format: postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
        
    def get_async_engine(self):
        return create_async_engine(
            self.database_url,
            echo=False,
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )

# database.py
from config import PostgreSQLConfig
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

config = PostgreSQLConfig()
engine = config.get_async_engine()
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage examples
from sqlalchemy import text

async def complex_analytics_query():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT 
                user_id,
                AVG(calories_consumed) as avg_calories,
                COUNT(*) as total_entries,
                DATE_TRUNC('week', created_at) as week
            FROM calorie_events 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            GROUP BY user_id, week
            HAVING COUNT(*) > 5
            ORDER BY avg_calories DESC
        """))
        return result.fetchall()

# For AI services - vector operations
async def vector_similarity_search(query_vector: list):
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT 
                id, content, metadata,
                embedding <-> %s as distance
            FROM knowledge_base
            ORDER BY embedding <-> %s
            LIMIT 10
        """), (query_vector, query_vector))
        return result.fetchall()
```

---

## 🔄 Migration Guide

### **From Current PostgreSQL Direct → Hybrid Strategy**

1. **Keep existing calorie-balance** as PostgreSQL direct (performance critical)
2. **Migrate user-management** to Supabase Client (auth features)
3. **New microservices** follow connection matrix above

### **Environment Variables Setup**

```bash
# For Supabase Client services
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# For PostgreSQL Direct services  
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
```

---

## 🎯 Decision Framework

### **Choose Supabase Client when:**
- ✅ Need real-time subscriptions
- ✅ Mobile app synchronization required
- ✅ Authentication/authorization features
- ✅ Rapid development/prototyping
- ✅ Simple CRUD operations
- ✅ Row Level Security needs

### **Choose PostgreSQL Direct when:**
- ✅ Complex analytical queries
- ✅ Performance-critical operations
- ✅ Vector/ML operations
- ✅ Custom optimizations needed
- ✅ Large-scale data processing
- ✅ Advanced PostgreSQL features

---

## � Known Issues & Solutions

### **HTTPX Version Conflict (RESOLVED)**

**Issue:** `httpx` dependency declared twice in `pyproject.toml`:
- Main dependencies: `httpx = "^0.25.0"`
- Dev dependencies: `httpx = "^0.25.0"` (duplicate)
- Incompatible with `postgrest ^0.10.8` which requires `httpx <0.25.0`

**Solution Applied (9 Sep 2025):**
- ✅ **Fixed in supabase-client-template**: `httpx = "^0.24.0"` (single declaration)
- ✅ **Fixed in user-management service**: Removed duplicate, aligned version
- ✅ **Compatibility verified**: Works with `postgrest ^0.10.8`

**Command to verify:**
```bash
cd templates/microservice-template/supabase-client-template
poetry check
poetry install  # Should work without conflicts
```

---

## �📚 Template Files Updated

- `templates/microservice-template/supabase-client-template/` - For real-time services
- `templates/microservice-template/postgresql-direct-template/` - For analytics services
- `docs/microservizi_python.md` - Updated with hybrid strategy
- Individual service documentation updated per connection type

**Next Steps:**
1. Update existing documentation per service type
2. Create separate template directories
3. Update deployment configurations
4. Update CI/CD for different connection types
