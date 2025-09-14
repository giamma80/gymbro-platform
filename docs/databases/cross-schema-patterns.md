# Cross-Schema Database Patterns - NutriFit Platform

## 🎯 Overview

Documentazione dei pattern architetturali per la gestione cross-schema nella piattaforma NutriFit, implementando il principio **Single Source of Truth** per i dati utente attraverso microservizi con database condiviso schema-based.

## 🏗️ Single Source of Truth Architecture

### Principi Fondamentali

1. **user_management.users è l'unica fonte authoritative** per dati utente
2. **Nessun microservizio replica tabelle users** localmente
3. **Foreign Keys Cross-Schema** garantiscono integrità referenziale
4. **Soft Delete Strategy** con `is_active` flag previene data loss
5. **Indici Parziali** ottimizzano performance per utenti attivi

## 📋 Standard Implementation Pattern

### 1. Schema Master: user_management

```sql
-- Schema autoritative per dati utente
CREATE SCHEMA IF NOT EXISTS user_management;

CREATE TABLE user_management.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    age INTEGER CHECK (age >= 10 AND age <= 120),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    height_cm DECIMAL(5,1) CHECK (height_cm >= 50 AND height_cm <= 300),
    weight_kg DECIMAL(5,1) CHECK (weight_kg >= 20 AND weight_kg <= 500),
    activity_level VARCHAR(20) CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3)
);
```

#### Performance Optimization - Partial Indexes

```sql
-- Indice parziale per utenti attivi (performance ottimale)
CREATE INDEX idx_users_active ON user_management.users (id) 
WHERE is_active = true;

-- Constraint unique solo per utenti attivi
CREATE UNIQUE INDEX idx_users_email_active ON user_management.users (email) 
WHERE is_active = true;

CREATE UNIQUE INDEX idx_users_username_active ON user_management.users (username) 
WHERE is_active = true;
```

### 2. Schema Consumer: Altri Microservizi

```sql
-- Schema microservizio consumer (esempio: calorie_balance)
CREATE SCHEMA IF NOT EXISTS calorie_balance;

-- ❌ NON CREARE tabella users duplicata
-- DROP TABLE IF EXISTS calorie_balance.users;  

-- ✅ Tabelle che referenziano user_management
CREATE TABLE calorie_balance.calorie_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    calories DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Foreign Key Cross-Schema (Single Source of Truth)
    FOREIGN KEY (user_id) REFERENCES user_management.users(id)
        ON UPDATE CASCADE
        -- Niente DELETE RESTRICT - soft delete strategy
);
```

## 🔧 Migration Strategy

### Step 1: Backup delle tabelle users esistenti

```sql
-- Backup dati esistenti prima della migrazione
CREATE TABLE backup_users_<service_name>_<timestamp> AS 
SELECT * FROM <service_schema>.users;
```

### Step 2: Verifica data consistency

```sql
-- Verifica che tutti gli user_id nelle tabelle figlio esistano in user_management
SELECT 
    t1.user_id,
    COUNT(*) as references_count
FROM <service_schema>.<child_table> t1
LEFT JOIN user_management.users u ON t1.user_id = u.id
WHERE u.id IS NULL
GROUP BY t1.user_id;
```

### Step 3: Update Foreign Keys

```sql
-- Rimuovi vecchie FK
ALTER TABLE <service_schema>.<table_name> 
DROP CONSTRAINT IF EXISTS fk_<table_name>_user_id;

-- Aggiungi nuove FK cross-schema
ALTER TABLE <service_schema>.<table_name>
ADD CONSTRAINT fk_<table_name>_user_cross_schema
FOREIGN KEY (user_id) REFERENCES user_management.users(id)
ON UPDATE CASCADE;
```

### Step 4: Drop duplicate users tables

```sql
-- Rimuovi tabella users duplicata (DOPO aver verificato FK)
DROP TABLE IF EXISTS <service_schema>.users CASCADE;
```

## 📊 Performance Considerations

### Query Patterns Ottimizzati

```sql
-- ✅ Query efficiente con JOIN cross-schema
SELECT 
    e.id,
    e.calories,
    u.username,
    u.email
FROM calorie_balance.calorie_events e
JOIN user_management.users u ON e.user_id = u.id
WHERE u.is_active = true  -- Usa indice parziale
  AND e.created_at >= CURRENT_DATE - INTERVAL '7 days';

-- ✅ Aggregazioni con filtro utenti attivi
SELECT 
    u.username,
    SUM(e.calories) as total_calories
FROM user_management.users u
JOIN calorie_balance.calorie_events e ON u.id = e.user_id
WHERE u.is_active = true  -- Performance ottimale
GROUP BY u.id, u.username;
```

### Index Strategy

```sql
-- Indici ottimizzati per query cross-schema frequenti
CREATE INDEX idx_<table_name>_user_id ON <schema>.<table_name>(user_id)
WHERE user_id IN (
    SELECT id FROM user_management.users WHERE is_active = true
);

-- Indice composito per query temporali
CREATE INDEX idx_<table_name>_user_date ON <schema>.<table_name>(user_id, created_at);
```

## 🏛️ Repository Pattern & Schema Manager

### ⚠️ CRITICAL: Common Schema Manager Mistakes

**❌ WRONG - Common Error Pattern:**
```python
class WrongRepository:
    def __init__(self):
        self.client = get_supabase_client()
        # ❌ ERROR: Using string table name without schema
        self.table = "calorie_events"  # This hits public schema!
        
    async def get_data(self):
        # ❌ ERROR: Double table() call 
        return self.client.table(self.table).select("*").execute()
```

**✅ CORRECT - Schema Manager Pattern:**
```python
class CorrectRepository:
    def __init__(self):
        self.client = get_supabase_client()
        self.schema_manager = get_schema_manager()
        # ✅ CORRECT: Schema manager returns configured table object
        self.table = self.schema_manager.calorie_events
        
    async def get_data(self):
        # ✅ CORRECT: Direct table object usage
        return self.table.select("*").execute()
```

### Schema Manager Implementation

```python
# app/core/schema_tables.py
class SchemaManager:
    def __init__(self, client: Client = None):
        self._client = client or get_supabase_client()
        self._settings = get_settings()
        self._schema_name = self._settings.database_schema  # e.g., "calorie_balance"
    
    def table(self, table_name: str) -> Any:
        """Get table with correct schema configuration."""
        return self._client.schema(self._schema_name).table(table_name)
    
    @property
    def calorie_events(self) -> Any:
        """Pre-configured calorie_events table with schema."""
        return self.table('calorie_events')
```

### Repository Best Practices

#### 1. Initialization Pattern
```python
def __init__(self):
    """ALWAYS follow this exact pattern."""
    self.client = get_supabase_client()           # For direct client access if needed
    self.schema_manager = get_schema_manager()    # Schema configuration
    self.table = self.schema_manager.table_name   # Pre-configured table object
```

#### 2. Query Execution Pattern
```python
async def query_method(self):
    """Use self.table directly - NOT self.client.table()"""
    # ✅ CORRECT: Direct table usage
    response = self.table.select("*").eq("user_id", user_id).execute()
    
    # ❌ WRONG: Don't do this!
    # response = self.client.table(self.table).select("*")...
```

#### 3. Error-Prone Scenarios to Avoid

**Scenario A: Mixed Schema Access**
```python
# ❌ WRONG: This breaks schema isolation
self.events_table = "calorie_events"  # Hits public.calorie_events
self.goals_table = self.schema_manager.calorie_goals  # Hits calorie_balance.calorie_goals
```

**Scenario B: String Concatenation**
```python
# ❌ WRONG: Manual schema handling
self.table = f"{schema_name}.table_name"  # Fragile and error-prone
```

**Scenario C: Incomplete Initialization**
```python
# ❌ WRONG: Missing schema manager
def __init__(self):
    self.client = get_supabase_client()
    # Missing: self.schema_manager = get_schema_manager()
    self.table = "table_name"  # Will hit public schema!
```

### Debugging Schema Issues

#### Common Error Messages:
1. **`Could not find table 'public.table_name'`** 
   - **Cause**: Using string table name instead of schema manager
   - **Fix**: Use `self.table = self.schema_manager.table_name`

2. **`<postgrest._sync.request_builder.SyncRequestBuilder object>`**
   - **Cause**: Calling `self.client.table(self.table)` when `self.table` is already a table object
   - **Fix**: Use `self.table.select()` directly

3. **`'Repository' object has no attribute 'client'`**
   - **Cause**: Missing `self.client = get_supabase_client()` in `__init__`
   - **Fix**: Always initialize client first

#### Quick Debugging Commands:
```python
# Check what type self.table is
print(f"Table type: {type(self.table)}")
print(f"Table repr: {repr(self.table)}")

# Check schema configuration
print(f"Schema: {self.schema_manager.schema_name}")
```

### Migration Checklist for Existing Repositories

- [ ] ✅ `self.client = get_supabase_client()` in `__init__`
- [ ] ✅ `self.schema_manager = get_schema_manager()` in `__init__`  
- [ ] ✅ `self.table = self.schema_manager.table_name` (not string)
- [ ] ✅ Direct table usage: `self.table.select()` (not `self.client.table()`)
- [ ] ✅ Test with `curl` to verify correct schema access
- [ ] ✅ Check logs for schema error messages

## 🛡️ Data Safety & Soft Delete

### Soft Delete Strategy

```sql
-- ❌ Mai delete fisico di utenti
-- DELETE FROM user_management.users WHERE id = ?;

-- ✅ Sempre soft delete
UPDATE user_management.users 
SET is_active = false, updated_at = NOW()
WHERE id = ?;
```

### Data Consistency Checks

```sql
-- Monitoring query per verificare referential integrity
SELECT 
    '<service_schema>' as service,
    '<table_name>' as table_name,
    COUNT(*) as orphaned_records
FROM <service_schema>.<table_name> t
LEFT JOIN user_management.users u ON t.user_id = u.id
WHERE u.id IS NULL;
```

## 📈 Benefits Summary

| Aspetto | Prima (Duplicate Tables) | Dopo (Cross-Schema FK) |
|---------|-------------------------|------------------------|
| **Data Consistency** | ❌ Possibili inconsistenze | ✅ Single source of truth garantito |
| **Storage** | ❌ Duplicazione dati | ✅ Storage ottimizzato |
| **Performance** | ❌ Sync overhead | ✅ Native PostgreSQL performance |
| **Maintenance** | ❌ Update multipli | ✅ Update centralizzato |
| **Scalability** | ❌ N*users growth | ✅ Linear growth |
| **Data Safety** | ❌ Risk di dati orfani | ✅ Referential integrity |

## 🚀 Implementation Checklist

### Pre-Migration
- [ ] Backup di tutte le tabelle users esistenti
- [ ] Verifica referential integrity esistente
- [ ] Test performance su dataset realistico
- [ ] Documenta mapping user_id esistenti

### Migration
- [ ] Update Foreign Keys per puntare a user_management.users
- [ ] Drop tabelle users duplicate dopo verifica FK
- [ ] Crea indici parziali in user_management
- [ ] Update query application layer

### Post-Migration
- [ ] Monitoring referential integrity
- [ ] Performance testing query cross-schema
- [ ] Update documentazione API
- [ ] Training team su nuovi pattern

---

## 📞 References

- **Database Architecture**: [docs/architettura.md](../architettura.md)
- **User Management DB**: [docs/databases/user-management-db.md](./user-management-db.md)
- **Calorie Balance DB**: [docs/databases/calorie-balance-db.md](./calorie-balance-db.md)

**Implementato per**: NutriFit Platform v2.0 - Cross-Schema Architecture Pattern