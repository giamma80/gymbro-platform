# Supabase Calorie Balance Database Migration

**Service:** calorie-balance  
**Project:** nutrifit-calorie-balance  
**Priority:** 🔥 HIGH - Existing Service Migration  
**Date:** 7 settembre 2025  

## 🎯 Migration Overview

Migrate the existing calorie-balance service from local PostgreSQL to Supabase Cloud, preserving all existing functionality while enabling cloud-native features.

## 📋 Pre-Migration Checklist

### ✅ Current State Verification
- [ ] Local PostgreSQL service running and accessible
- [ ] All tables exist: `users`, `user_profiles`, `calorie_goals`, `metabolic_profiles`, `calorie_events`
- [ ] Event-driven views working: `hourly_calorie_summary`, `daily_calorie_summary`, etc.
- [ ] API endpoints responding correctly
- [ ] Test suite passing (100% success rate)

### 📊 Data Backup
```bash
# Create full backup before migration
cd services/calorie-balance
pg_dump -h localhost -U postgres -d nutrifit_calorie_balance > backup_$(date +%Y%m%d).sql

# Verify backup integrity
psql -h localhost -U postgres -c "\l nutrifit_calorie_balance"
```

## 🚀 Migration Steps

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project: `nutrifit-calorie-balance`
3. Select same region as user-management project
4. Generate strong database password
5. Save connection details

### Step 2: Setup Database Schema
Copy existing schema from `create_tables_direct.py` to Supabase SQL Editor:

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Custom enums (from existing schema)
CREATE TYPE gender AS ENUM ('male', 'female', 'other');
CREATE TYPE activity_level AS ENUM ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active');
CREATE TYPE goal_type AS ENUM ('weight_loss', 'weight_gain', 'maintenance');

-- 1. Users table (will be deprecated after User Management Service migration)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User profiles table (calorie-specific profiles)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    age INTEGER,
    gender gender,
    activity_level activity_level,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_profile UNIQUE(user_id),
    CONSTRAINT height_check CHECK (height_cm > 0 AND height_cm < 300),
    CONSTRAINT weight_check CHECK (weight_kg > 0 AND weight_kg < 1000),
    CONSTRAINT age_check CHECK (age > 0 AND age < 150)
);

-- 3. Calorie goals table
CREATE TABLE calorie_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    daily_calorie_target INTEGER NOT NULL,
    goal_type goal_type NOT NULL,
    target_weight_kg DECIMAL(5,2),
    target_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_calories CHECK (daily_calorie_target > 0),
    CONSTRAINT positive_target_weight CHECK (target_weight_kg IS NULL OR target_weight_kg > 0)
);

-- 4. Metabolic profiles table
CREATE TABLE metabolic_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bmr DECIMAL(7,2) NOT NULL,
    tdee DECIMAL(7,2) NOT NULL,
    calories_burned_bmr DECIMAL(7,2) NOT NULL,
    calories_burned_activities DECIMAL(7,2) DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_bmr CHECK (bmr > 0),
    CONSTRAINT positive_tdee CHECK (tdee > 0),
    CONSTRAINT positive_calories_burned CHECK (calories_burned_bmr >= 0)
);

-- 5. Calorie events table (high-frequency events)
CREATE TABLE calorie_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    calories_amount DECIMAL(8,2) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_calories CHECK (calories_amount >= 0)
);

-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_calorie_goals_user_id ON calorie_goals(user_id);
CREATE INDEX idx_calorie_goals_active ON calorie_goals(user_id, is_active);
CREATE INDEX idx_metabolic_profiles_user_id ON metabolic_profiles(user_id);
CREATE INDEX idx_metabolic_profiles_active ON metabolic_profiles(user_id, is_active);
CREATE INDEX idx_calorie_events_user_id ON calorie_events(user_id);
CREATE INDEX idx_calorie_events_timestamp ON calorie_events(event_timestamp);
CREATE INDEX idx_calorie_events_user_timestamp ON calorie_events(user_id, event_timestamp);
CREATE INDEX idx_calorie_events_type ON calorie_events(event_type);

-- Temporal analytics views (5-level hierarchy)
-- 1. Hourly aggregation
CREATE VIEW hourly_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('hour', event_timestamp) as hour_bucket,
    SUM(calories_amount) as total_calories,
    COUNT(*) as event_count,
    AVG(calories_amount) as avg_calories_per_event,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events 
GROUP BY user_id, DATE_TRUNC('hour', event_timestamp)
ORDER BY user_id, hour_bucket;

-- 2. Daily aggregation  
CREATE VIEW daily_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('day', event_timestamp) as day_bucket,
    SUM(calories_amount) as total_calories,
    COUNT(*) as event_count,
    AVG(calories_amount) as avg_calories_per_event,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events 
GROUP BY user_id, DATE_TRUNC('day', event_timestamp)
ORDER BY user_id, day_bucket;

-- 3. Weekly aggregation
CREATE VIEW weekly_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('week', event_timestamp) as week_bucket,
    SUM(calories_amount) as total_calories,
    COUNT(*) as event_count,
    AVG(calories_amount) as avg_calories_per_event,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events 
GROUP BY user_id, DATE_TRUNC('week', event_timestamp)
ORDER BY user_id, week_bucket;

-- 4. Monthly aggregation
CREATE VIEW monthly_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('month', event_timestamp) as month_bucket,
    SUM(calories_amount) as total_calories,
    COUNT(*) as event_count,
    AVG(calories_amount) as avg_calories_per_event,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events 
GROUP BY user_id, DATE_TRUNC('month', event_timestamp)
ORDER BY user_id, month_bucket;

-- 5. Balance calculation view
CREATE VIEW calorie_balance_summary AS
SELECT 
    ce.user_id,
    DATE_TRUNC('day', ce.event_timestamp) as day_bucket,
    SUM(ce.calories_amount) as calories_consumed,
    COALESCE(mp.calories_burned_bmr, 0) + COALESCE(mp.calories_burned_activities, 0) as calories_burned,
    SUM(ce.calories_amount) - (COALESCE(mp.calories_burned_bmr, 0) + COALESCE(mp.calories_burned_activities, 0)) as net_balance,
    cg.daily_calorie_target,
    SUM(ce.calories_amount) - cg.daily_calorie_target as target_variance
FROM calorie_events ce
LEFT JOIN metabolic_profiles mp ON ce.user_id = mp.user_id AND mp.is_active = true
LEFT JOIN calorie_goals cg ON ce.user_id = cg.user_id AND cg.is_active = true
GROUP BY ce.user_id, DATE_TRUNC('day', ce.event_timestamp), mp.calories_burned_bmr, mp.calories_burned_activities, cg.daily_calorie_target
ORDER BY ce.user_id, day_bucket;
```

### Step 3: Data Migration
```bash
# Export data from local PostgreSQL
cd services/calorie-balance

# Export each table separately for better control
pg_dump -h localhost -U postgres -d nutrifit_calorie_balance -t users --data-only > users_data.sql
pg_dump -h localhost -U postgres -d nutrifit_calorie_balance -t user_profiles --data-only > user_profiles_data.sql
pg_dump -h localhost -U postgres -d nutrifit_calorie_balance -t calorie_goals --data-only > calorie_goals_data.sql
pg_dump -h localhost -U postgres -d nutrifit_calorie_balance -t metabolic_profiles --data-only > metabolic_profiles_data.sql
pg_dump -h localhost -U postgres -d nutrifit_calorie_balance -t calorie_events --data-only > calorie_events_data.sql

# Import to Supabase (via SQL Editor or psql)
# Note: Replace connection details with your Supabase credentials
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" < users_data.sql
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" < user_profiles_data.sql
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" < calorie_goals_data.sql
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" < metabolic_profiles_data.sql
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres" < calorie_events_data.sql
```

### Step 4: Update Service Configuration
```python
# Update services/calorie-balance/.env
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres"

# Update core/database.py if needed
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure SSL is configured for Supabase
if "supabase" in SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL += "?sslmode=require"
```

### Step 5: Verification Testing
```bash
# Test database connectivity
cd services/calorie-balance
poetry run python -c "
from core.database import get_database_connection
try:
    conn = get_database_connection()
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# Run existing test suite
poetry run python -m pytest tests/ -v

# Test all API endpoints
python test_all_formats.py
python test_official_formats.py
```

### Step 6: Enable Real-time Features
```sql
-- Enable real-time for key tables in Supabase dashboard
-- Go to Database > Replication
-- Enable real-time for:
-- - calorie_events (for live tracking)
-- - daily_calorie_summary (for dashboard updates)
-- - calorie_goals (for goal changes)
-- - metabolic_profiles (for profile updates)
```

### Step 7: Performance Optimization
```sql
-- Additional performance indexes for Supabase
CREATE INDEX CONCURRENTLY idx_calorie_events_user_recent 
ON calorie_events(user_id, event_timestamp DESC) 
WHERE event_timestamp > NOW() - INTERVAL '30 days';

CREATE INDEX CONCURRENTLY idx_hourly_summary_recent
ON hourly_calorie_summary(user_id, hour_bucket DESC);

CREATE INDEX CONCURRENTLY idx_daily_summary_recent  
ON daily_calorie_summary(user_id, day_bucket DESC);

-- Configure connection pooling in Supabase dashboard
-- Settings > Database > Connection pooling
-- Transaction mode: Recommended for most applications
-- Default pool size: 20
-- Max client connections: 100
```

## 🔐 Security Configuration

### Row Level Security (RLS)
```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE calorie_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE metabolic_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE calorie_events ENABLE ROW LEVEL SECURITY;

-- RLS policies (basic user isolation)
CREATE POLICY "Users can access own data" ON users
    FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can access own profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own goals" ON calorie_goals
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own metabolic data" ON metabolic_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own events" ON calorie_events
    FOR ALL USING (auth.uid() = user_id);
```

## 📊 Migration Validation

### Data Integrity Checks
```sql
-- Verify record counts match
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'user_profiles', COUNT(*) FROM user_profiles  
UNION ALL
SELECT 'calorie_goals', COUNT(*) FROM calorie_goals
UNION ALL
SELECT 'metabolic_profiles', COUNT(*) FROM metabolic_profiles
UNION ALL  
SELECT 'calorie_events', COUNT(*) FROM calorie_events;

-- Verify views work correctly
SELECT user_id, COUNT(*) as event_count 
FROM calorie_events 
GROUP BY user_id 
ORDER BY event_count DESC 
LIMIT 5;

-- Test temporal aggregations
SELECT * FROM daily_calorie_summary 
ORDER BY day_bucket DESC 
LIMIT 10;
```

### API Endpoint Testing
```bash
# Test all existing endpoints work with Supabase
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/v1/users"
curl -X GET "http://localhost:8000/api/v1/calorie-goals" 
curl -X GET "http://localhost:8000/api/v1/metabolic-profiles"
curl -X GET "http://localhost:8000/api/v1/calorie-events"

# Test analytics endpoints
curl -X GET "http://localhost:8000/api/v1/analytics/daily-summary"
curl -X GET "http://localhost:8000/api/v1/analytics/calorie-balance"
```

## 🚨 Rollback Plan

If migration fails:

1. **Immediate Rollback:**
```bash
# Restore local environment
cd services/calorie-balance
cp .env.backup .env  # Restore local DATABASE_URL

# Restart local services
docker-compose up -d postgres
poetry run uvicorn main:app --reload
```

2. **Data Recovery:**
```bash
# Restore from backup if needed
psql -h localhost -U postgres -d nutrifit_calorie_balance < backup_$(date +%Y%m%d).sql
```

## ✅ Success Criteria

- [ ] All tables migrated with correct schema
- [ ] All data transferred without loss
- [ ] All API endpoints responding correctly
- [ ] Test suite passes (100% success rate)
- [ ] Real-time features enabled
- [ ] Performance matches or exceeds local setup
- [ ] RLS policies configured and working
- [ ] Connection pooling optimized
- [ ] Backup strategy confirmed

## 🔄 Next Steps After Migration

1. **User Management Integration**: Connect to centralized auth service
2. **Remove Users Table**: Migrate to User Management Service 
3. **Real-time Sync**: Enable live updates for mobile app
4. **Advanced Analytics**: Setup more sophisticated views
5. **Performance Monitoring**: Configure alerts and dashboards

---

**Status:** 🚧 Ready for Migration  
**Estimated Time:** 6-8 hours  
**Risk Level:** Medium (careful data migration required)  
**Dependencies:** Supabase account, backup verification
