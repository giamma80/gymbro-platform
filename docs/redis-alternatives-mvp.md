# 🚀 Redis Alternatives for MVP - Costi Zero su Render

## 🎯 Obiettivo: Eliminare Redis dal MVP per usare solo il Free Tier di Render

### 📊 Situazione Attuale
- ✅ Redis **NON implementato** nel codice (solo configurato)
- ✅ Usi previsti: Sessions, Cache, Rate Limiting, Celery
- ✅ Opportunità: Switch prima dell'implementazione

## 💡 Alternative Gratuite

### 🥇 **OPZIONE 1: PostgreSQL + In-Memory (RACCOMANDATO)**

```python
# Sessions → PostgreSQL Table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token_hash VARCHAR,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    last_accessed TIMESTAMP
);

# Cache → Python dict + TTL
import time
from typing import Dict, Any, Optional

class InMemoryCache:
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key: (value, expiry)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            del self._cache[key]
        return None
```

**✅ Vantaggi:**
- Zero costi aggiuntivi 
- PostgreSQL già incluso in Render free
- Performance accettabile per MVP
- Scaling path chiaro (→ Redis quando necessario)

**❌ Svantaggi:**
- Cache perso al restart app
- Meno performance di Redis
- Sessions in DB più lente

### 🥈 **OPZIONE 2: Upstash Redis (Free Tier)**

```yaml
# Alternative Redis Managed Free:
Upstash Redis:
  Free: 10k requests/day
  Perfect per MVP
  Integration: Semplice (Redis URL)
  
Railway Redis:
  Free: $5 credit/mese
  Full Redis compatibility
```

### 🥉 **OPZIONE 3: SQLite per Cache Locale**

```python
# Cache con SQLite in memoria
import sqlite3
import pickle
import time

class SQLiteCache:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._setup_tables()
    
    def _setup_tables(self):
        self.conn.execute("""
            CREATE TABLE cache (
                key TEXT PRIMARY KEY,
                value BLOB,
                expiry REAL
            )
        """)
```

## 🎯 **RACCOMANDAZIONE: PostgreSQL + In-Memory**

### 📋 **Piano di Implementazione**

#### 1. **Rimuovere Redis Dependencies**
```bash
# pyproject.toml
- redis = "^6.4.0"

# config.py  
- REDIS_URL
- CELERY_BROKER_URL (Redis)
- CELERY_RESULT_BACKEND (Redis)
```

#### 2. **Implementare PostgreSQL Sessions**
```sql
-- migrations/add_sessions_table.sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token_hash ON user_sessions(token_hash);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
```

#### 3. **In-Memory Cache Service**
```python
# services/cache_service.py
from typing import Dict, Any, Optional
import time
import threading
from datetime import datetime, timedelta

class CacheService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = {}
                    cls._instance._access_counts = {}
        return cls._instance
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        expiry = time.time() + ttl
        self._cache[key] = {
            'value': value,
            'expiry': expiry,
            'created': time.time()
        }
    
    def get(self, key: str) -> Optional[Any]:
        self._cleanup_expired()
        
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item['expiry']:
                self._access_counts[key] = self._access_counts.get(key, 0) + 1
                return item['value']
            else:
                del self._cache[key]
                if key in self._access_counts:
                    del self._access_counts[key]
        return None
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            if key in self._access_counts:
                del self._access_counts[key]
            return True
        return False
    
    def _cleanup_expired(self) -> None:
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time >= item['expiry']
        ]
        for key in expired_keys:
            del self._cache[key]
            if key in self._access_counts:
                del self._access_counts[key]
    
    def stats(self) -> Dict[str, Any]:
        self._cleanup_expired()
        return {
            'total_keys': len(self._cache),
            'total_access_count': sum(self._access_counts.values()),
            'most_accessed': max(self._access_counts.items(), key=lambda x: x[1]) if self._access_counts else None
        }

# Singleton instance
cache = CacheService()
```

#### 4. **Rate Limiting con PostgreSQL**
```python
# models/rate_limit.py
from sqlalchemy import Column, String, DateTime, Integer
from database import Base
from datetime import datetime

class RateLimit(Base):
    __tablename__ = "rate_limits"
    
    key = Column(String, primary_key=True)  # ip:endpoint
    count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    async def check_rate_limit(cls, db, key: str, limit: int, window: int) -> bool:
        # Implementation for rate limiting using DB
        pass
```

## 🚀 **Migration Strategy**

### **Fase 1: Remove Redis (Immediate)**
1. Update `pyproject.toml` - remove redis dependency
2. Update `config.py` - remove Redis settings  
3. Update `docker-compose.yml` - comment Redis service
4. Update tests - remove Redis fixtures

### **Fase 2: Implement Alternatives (Week 1)**
1. PostgreSQL sessions table + model
2. In-memory cache service
3. Database-based rate limiting
4. Update auth.py to use new session storage

### **Fase 3: Future Scaling (v0.5.0+)**
1. Monitor performance metrics
2. When needed: Add Redis back
3. Smooth migration path exists

## 📊 **Performance Comparison**

| Feature | Redis | PostgreSQL + Memory | Performance Impact |
|---------|-------|-------------------|-------------------|
| **Sessions** | ⚡ <1ms | 🔧 5-10ms | Acceptable for MVP |
| **Cache** | ⚡ <1ms | 🔧 <1ms (memory) | Identical |
| **Rate Limiting** | ⚡ <1ms | 🔧 10-20ms | Acceptable for MVP |
| **Persistence** | ✅ Yes | ❌ Cache lost on restart | MVP acceptable |
| **Scaling** | ✅ Excellent | 🔧 Limited | Migration path exists |

## 💰 **Cost Comparison (MVP Phase)**

```bash
# With Redis (Render):
- App Service: $0 (free tier)
- PostgreSQL: $0 (free tier)  
- Redis: $7/month (first tier)
- Total: $7/month

# Without Redis (Pure Free):
- App Service: $0 (free tier)
- PostgreSQL: $0 (free tier)
- In-memory cache: $0 (included)
- Total: $0/month
```

## 🎯 **DECISIONE FINALE**

**✅ RECOMMEND**: PostgreSQL + In-Memory per MVP

**Rationale**:
1. **💰 Zero costs** per validazione MVP
2. **🚀 Performance accettabile** per early users  
3. **📈 Clear upgrade path** a Redis quando necessario
4. **🔧 Minimal complexity** vs alternatives
5. **⚡ Immediate implementation** possibile

### 🔄 **Future Migration Path**
```bash
# Quando migrare a Redis:
- Utenti attivi > 1000/giorno
- Session management diventa bottleneck
- Cache miss rate > 30%
- Budget disponibile > $20/mese

# Migration sarà automatica:
1. Add Redis to config
2. Switch cache service to Redis
3. Migrate existing sessions
4. Zero downtime deployment
```

## 🛠️ **Implementation Tasks**

- [ ] Remove Redis from dependencies
- [ ] Create PostgreSQL sessions table
- [ ] Implement InMemoryCache service  
- [ ] Update auth service for DB sessions
- [ ] Database-based rate limiting
- [ ] Update tests to remove Redis
- [ ] Update documentation
- [ ] Deploy and validate performance

**Estimated Time**: 1-2 giorni sviluppo
**Risk Level**: Low (fallback to Redis sempre disponibile)
**Impact**: Zero costi MVP, performance accettabile

---

*Next: Implementare il removal di Redis e PostgreSQL sessions*
