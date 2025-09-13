# NutriFit Calorie Balance - Database Documentation

## Descrizione

Il database del **Calorie Balance Service** implementa un'**architettura event-driven** di nuova generazione per il monitoraggio calorico ad alta frequenza, progettata per applicazioni mobile con campionamento 2-minuti e analytics temporali multi-livello.

### Caratteristiche Principali
- 📱 **High-Frequency Events**: Raccolta eventi ogni 2 minuti da dispositivi mobile
- 📊 **5-Level Temporal Analytics**: Aggregazioni da orarie a mensili
- ⚡ **Performance Optimized**: Viste pre-computate per sub-second response
- 🔄 **Event Sourcing**: Timeline completa ricostruibile da eventi
- 🎯 **AI-Ready**: Schema ottimizzato per machine learning insights

## Schema ER

```mermaid
erDiagram
    USER_MANAGEMENT_USERS ||--o{ CALORIE_GOALS : "ha"
    USER_MANAGEMENT_USERS ||--o{ CALORIE_EVENTS : "genera"
    USER_MANAGEMENT_USERS ||--o{ DAILY_BALANCES : "possiede"
    USER_MANAGEMENT_USERS ||--o{ METABOLIC_PROFILES : "ha"
    
    CALORIE_EVENTS ||--o{ HOURLY_CALORIE_SUMMARY : "aggregato in"
    CALORIE_EVENTS ||--o{ DAILY_CALORIE_SUMMARY : "aggregato in"
    CALORIE_EVENTS ||--o{ WEEKLY_CALORIE_SUMMARY : "aggregato in"
    CALORIE_EVENTS ||--o{ MONTHLY_CALORIE_SUMMARY : "aggregato in"
    CALORIE_EVENTS ||--o{ DAILY_BALANCE_SUMMARY : "bilancio netto"
    
    USER_MANAGEMENT_USERS {
        UUID id PK "Cross-schema reference"
        varchar username UK "from user_management.users"
        varchar email UK "Single Source of Truth"
        varchar full_name
        int age
        varchar gender
        decimal height_cm
        decimal weight_kg
        varchar activity_level
        timestamptz created_at
        timestamptz updated_at
        boolean is_active
    }
    
    CALORIE_GOALS {
        UUID id PK
        UUID user_id FK
        varchar goal_type
        decimal target_calories
        decimal target_weight_kg
        decimal weekly_weight_change_kg
        date start_date
        date end_date
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }
    
    CALORIE_EVENTS {
        UUID id PK
        UUID user_id FK
        varchar event_type
        decimal value
        timestamptz event_timestamp
        jsonb metadata
        varchar source
    }
    
    DAILY_BALANCES {
        UUID id PK
        UUID user_id FK
        date date UK
        decimal calories_consumed
        decimal calories_burned_exercise
        decimal calories_burned_bmr
        decimal net_calories
        decimal weight_kg
        int events_count
        timestamptz last_event_timestamp
        text notes
        timestamptz created_at
        timestamptz updated_at
    }
    
    METABOLIC_PROFILES {
        UUID id PK
        UUID user_id FK
        numeric bmr_calories
        numeric tdee_calories
        numeric rmr_calories
        varchar calculation_method
        numeric accuracy_score
        numeric sedentary_multiplier
        numeric light_multiplier
        numeric moderate_multiplier
        numeric high_multiplier
        numeric extreme_multiplier
        boolean ai_adjusted
        numeric adjustment_factor
        int learning_iterations
        timestamptz calculated_at
        timestamptz expires_at
        boolean is_active
    }
```

## Core Tables

### 1. `user_management.users` - Cross-Schema Reference (Single Source of Truth)
```sql
-- NOTA: Questa tabella risiede nello schema user_management
-- Il servizio calorie_balance fa riferimento via FK cross-schema

-- Riferimento Cross-Schema (NON duplicata localmente)
-- La tabella users è gestita dal microservizio user-management
-- Vedere docs/databases/user-management-db.md per dettagli completi

FOREIGN KEY (user_id) REFERENCES user_management.users(id)
    ON UPDATE CASCADE;
    -- No DELETE RESTRICT - soft delete strategy con is_active flag
```

**Vantaggi Single Source of Truth:**
- ✅ **No Data Duplication**: Nessuna tabella users locale duplicata
- ✅ **Referential Integrity**: FK cross-schema garantisce consistenza
- ✅ **Soft Delete Safety**: `user_management.users.is_active = false` strategy
- ✅ **Performance**: Indici parziali ottimizzati per utenti attivi

### 2. `calorie_goals` - Obiettivi Calorici Dinamici
```sql
CREATE TABLE calorie_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    goal_type VARCHAR(30) NOT NULL,
    target_calories DECIMAL(6, 1) NOT NULL,
    target_weight_kg DECIMAL(5, 1),
    weekly_weight_change_kg DECIMAL(3, 1) DEFAULT 0.0 NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Cross-Schema Foreign Key (Single Source of Truth)
    FOREIGN KEY (user_id) REFERENCES user_management.users(id)
        ON UPDATE CASCADE,
    
    CONSTRAINT chk_target_calories CHECK (target_calories >= 800 AND target_calories <= 5000),
    CONSTRAINT chk_target_weight_kg CHECK (target_weight_kg >= 0 AND target_weight_kg <= 500),
    CONSTRAINT chk_weekly_weight_change_kg CHECK (weekly_weight_change_kg >= -2 AND weekly_weight_change_kg <= 2),
    UNIQUE(user_id, start_date)
);

-- Performance indexes
CREATE INDEX idx_calorie_goals_user_id ON calorie_goals(user_id);
CREATE INDEX idx_calorie_goals_start_date ON calorie_goals(start_date);
CREATE INDEX idx_calorie_goals_user_start_date ON calorie_goals(user_id, start_date);
```
**API Mapping**: `/api/v1/goals/*`

### 3. `calorie_events` - 🔥 High-Frequency Events Core
```sql
CREATE TABLE calorie_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    event_type VARCHAR(30) NOT NULL,  -- consumed, burned_exercise, burned_bmr, weight
    value DECIMAL(8, 2) NOT NULL,     -- calories or weight value
    event_timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,  -- precise timestamp for 2-minute sampling
    metadata JSONB,                   -- additional data (food_id, exercise_id, etc.)
    source VARCHAR(50) DEFAULT 'app' NOT NULL,  -- app, smartwatch, manual, etc.
    
    -- Cross-Schema Foreign Key (Single Source of Truth)
    FOREIGN KEY (user_id) REFERENCES user_management.users(id)
        ON UPDATE CASCADE,
    
    CONSTRAINT chk_event_type CHECK (event_type IN ('consumed', 'burned_exercise', 'burned_bmr', 'weight')),
    CONSTRAINT chk_event_value CHECK (value >= 0 AND value <= 10000),
    CONSTRAINT chk_source CHECK (source IN ('app', 'smartwatch', 'manual', 'api', 'sync'))
);

-- Critical performance indexes for mobile queries
CREATE INDEX idx_calorie_events_user_id ON calorie_events(user_id);
CREATE INDEX idx_calorie_events_timestamp ON calorie_events(event_timestamp);
CREATE INDEX idx_calorie_events_user_timestamp ON calorie_events(user_id, event_timestamp);
CREATE INDEX idx_calorie_events_user_type_timestamp ON calorie_events(user_id, event_type, event_timestamp);
CREATE INDEX idx_calorie_events_type ON calorie_events(event_type);
```
**API Mapping**: `/api/v1/calorie-event/*`, `/api/v1/events/*`
### 4. `daily_balances` - Enhanced Daily Aggregations
```sql
CREATE TABLE daily_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    calories_consumed DECIMAL(6, 1) DEFAULT 0.0 NOT NULL,
    calories_burned_exercise DECIMAL(6, 1) DEFAULT 0.0 NOT NULL,
    calories_burned_bmr DECIMAL(6, 1) DEFAULT 0.0 NOT NULL,
    net_calories DECIMAL(6, 1),
    weight_kg DECIMAL(5, 1),
    events_count INTEGER DEFAULT 0 NOT NULL,  -- Track number of events for this day
    last_event_timestamp TIMESTAMPTZ,  -- Last event for this day
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Cross-Schema Foreign Key (Single Source of Truth)
    FOREIGN KEY (user_id) REFERENCES user_management.users(id)
        ON UPDATE CASCADE,
    
    CONSTRAINT chk_calories_consumed CHECK (calories_consumed >= 0 AND calories_consumed <= 10000),
    CONSTRAINT chk_calories_burned_exercise CHECK (calories_burned_exercise >= 0 AND calories_burned_exercise <= 5000),
    CONSTRAINT chk_calories_burned_bmr CHECK (calories_burned_bmr >= 0 AND calories_burned_bmr <= 5000),
    CONSTRAINT chk_daily_weight CHECK (weight_kg >= 20 AND weight_kg <= 500),
    CONSTRAINT chk_events_count CHECK (events_count >= 0),
    UNIQUE(user_id, date)
);

-- Performance indexes
CREATE INDEX idx_daily_balances_user_id ON daily_balances(user_id);
CREATE INDEX idx_daily_balances_date ON daily_balances(date);
CREATE INDEX idx_daily_balances_user_date ON daily_balances(user_id, date);
CREATE INDEX idx_daily_balances_last_event ON daily_balances(user_id, last_event_timestamp);
```
**API Mapping**: `/api/v1/balance/*`

### 5. `metabolic_profiles` - Profili Metabolici Personalizzati (Schema Reale)
```sql
CREATE TABLE metabolic_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    bmr_calories NUMERIC,
    tdee_calories NUMERIC,
    rmr_calories NUMERIC,
    calculation_method CHARACTER VARYING,
    accuracy_score NUMERIC,
    sedentary_multiplier NUMERIC,
    light_multiplier NUMERIC,
    moderate_multiplier NUMERIC,
    high_multiplier NUMERIC,
    extreme_multiplier NUMERIC,
    ai_adjusted BOOLEAN,
    adjustment_factor NUMERIC,
    learning_iterations INTEGER,
    calculated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN,
    
    -- Cross-Schema Foreign Key (Single Source of Truth)
    FOREIGN KEY (user_id) REFERENCES user_management.users(id)
        ON UPDATE CASCADE,
    
    CONSTRAINT chk_bmr_calories CHECK (bmr_calories >= 800 AND bmr_calories <= 5000),
    CONSTRAINT chk_tdee_calories CHECK (tdee_calories >= 800 AND tdee_calories <= 6000),
    CONSTRAINT chk_accuracy_score CHECK (accuracy_score >= 0.0 AND accuracy_score <= 1.0),
    CONSTRAINT chk_multipliers CHECK (
        sedentary_multiplier >= 1.0 AND sedentary_multiplier <= 2.0 AND
        light_multiplier >= 1.0 AND light_multiplier <= 2.0 AND
        moderate_multiplier >= 1.0 AND moderate_multiplier <= 2.0 AND
        high_multiplier >= 1.0 AND high_multiplier <= 2.0 AND
        extreme_multiplier >= 1.0 AND extreme_multiplier <= 2.0
    )
);

-- Performance indexes
CREATE INDEX idx_metabolic_profiles_user_id ON metabolic_profiles(user_id);
CREATE INDEX idx_metabolic_profiles_expires_at ON metabolic_profiles(expires_at);
CREATE INDEX idx_metabolic_profiles_active ON metabolic_profiles(user_id, is_active) 
    WHERE is_active = true;
```
**API Mapping**: `/api/v1/users/{user_id}/profile/metabolic`

> **⚠️ NOTA CRITICA**: Lo schema reale della tabella `metabolic_profiles` è significativamente diverso da quello precedentemente documentato. Include campi avanzati per AI machine learning (`learning_iterations`, `ai_adjusted`), multipliers di attività personalizzati e metodologie di calcolo multiple.

## 📊 5-Level Temporal Analytics Views

### 1. `hourly_calorie_summary` - Real-time Intraday Trends
```sql
CREATE VIEW hourly_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('hour', event_timestamp) as hour_start,
    event_type,
    SUM(value) as total_value,
    COUNT(*) as event_count,
    AVG(value) as avg_value,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events
GROUP BY user_id, DATE_TRUNC('hour', event_timestamp), event_type;
```
**API Mapping**: `/api/v1/timeline/users/{user_id}/hourly`  
**Use Case**: Meal timing analysis, real-time dashboard updates

### 2. `daily_calorie_summary` - Day-over-day Comparisons
```sql
CREATE VIEW daily_calorie_summary AS
SELECT 
    user_id,
    DATE(event_timestamp) as date,
    event_type,
    SUM(value) as total_value,
    COUNT(*) as event_count,
    AVG(value) as avg_value,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events
GROUP BY user_id, DATE(event_timestamp), event_type;
```
**API Mapping**: `/api/v1/timeline/users/{user_id}/daily`  
**Use Case**: Daily goal tracking, progress monitoring

### 3. `weekly_calorie_summary` - Weekly Patterns & Habits
```sql
CREATE VIEW weekly_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('week', event_timestamp) as week_start,
    DATE_TRUNC('week', event_timestamp) + INTERVAL '6 days' as week_end,
    EXTRACT(year FROM event_timestamp) as year,
    EXTRACT(week FROM event_timestamp) as week_number,
    event_type,
    SUM(value) as total_value,
    COUNT(*) as event_count,
    AVG(value) as avg_value,
    COUNT(DISTINCT DATE(event_timestamp)) as active_days,
    SUM(value) / COUNT(DISTINCT DATE(event_timestamp)) as avg_daily_value,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events
GROUP BY user_id, DATE_TRUNC('week', event_timestamp), 
         EXTRACT(year FROM event_timestamp), EXTRACT(week FROM event_timestamp), event_type;
```
**API Mapping**: `/api/v1/timeline/users/{user_id}/weekly`  
**Use Case**: Habit formation tracking, weekly patterns analysis

### 4. `monthly_calorie_summary` - Long-term Trends
```sql
CREATE VIEW monthly_calorie_summary AS
SELECT 
    user_id,
    DATE_TRUNC('month', event_timestamp) as month_start,
    EXTRACT(year FROM event_timestamp) as year,
    EXTRACT(month FROM event_timestamp) as month_number,
    TO_CHAR(event_timestamp, 'YYYY-MM') as year_month,
    event_type,
    SUM(value) as total_value,
    COUNT(*) as event_count,
    AVG(value) as avg_value,
    COUNT(DISTINCT DATE(event_timestamp)) as active_days,
    SUM(value) / COUNT(DISTINCT DATE(event_timestamp)) as avg_daily_value,
    COUNT(DISTINCT DATE_TRUNC('week', event_timestamp)) as active_weeks,
    SUM(value) / COUNT(DISTINCT DATE_TRUNC('week', event_timestamp)) as avg_weekly_value,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events
GROUP BY user_id, DATE_TRUNC('month', event_timestamp), 
         EXTRACT(year FROM event_timestamp), EXTRACT(month FROM event_timestamp), 
         TO_CHAR(event_timestamp, 'YYYY-MM'), event_type;
```
**API Mapping**: `/api/v1/timeline/users/{user_id}/monthly`  
**Use Case**: Monthly progress reports, long-term trend analysis

### 5. `daily_balance_summary` - 🔥 Net Calories & Weight Correlation
```sql
CREATE VIEW daily_balance_summary AS
SELECT 
    user_id,
    DATE(event_timestamp) as date,
    SUM(CASE WHEN event_type = 'consumed' THEN value ELSE 0 END) as calories_consumed,
    SUM(CASE WHEN event_type = 'burned_exercise' THEN value ELSE 0 END) as calories_burned_exercise,
    SUM(CASE WHEN event_type = 'burned_bmr' THEN value ELSE 0 END) as calories_burned_bmr,
    SUM(CASE WHEN event_type = 'consumed' THEN value ELSE 0 END) - 
    (SUM(CASE WHEN event_type = 'burned_exercise' THEN value ELSE 0 END) + 
     SUM(CASE WHEN event_type = 'burned_bmr' THEN value ELSE 0 END)) as net_calories,
    AVG(CASE WHEN event_type = 'weight' THEN value ELSE NULL END) as avg_weight_kg,
    COUNT(*) as total_events,
    COUNT(DISTINCT event_type) as event_types_count,
    MIN(event_timestamp) as first_event,
    MAX(event_timestamp) as last_event
FROM calorie_events
WHERE event_type IN ('consumed', 'burned_exercise', 'burned_bmr', 'weight')
GROUP BY user_id, DATE(event_timestamp);
```
**API Mapping**: `/api/v1/timeline/users/{user_id}/balance`  
**Use Case**: Deficit/surplus tracking, weight correlation analysis

## 🔧 Performance & Optimization

### ⚠️ SETUP CRITICO - Esposizione Schema in Supabase

**STEP OBBLIGATORIO**: Dopo la creazione del database, esporre lo schema `calorie_balance` nella Dashboard Supabase:

1. **Dashboard**: `https://supabase.com/dashboard/project/{project-id}/settings/api`
2. **API Settings** → **Exposed schemas** → Aggiungere: `calorie_balance`  
3. **Verificare**: Lo schema deve apparire nella lista PostgREST

⚠️ **Senza questa configurazione**: Il servizio restituisce errore `PGRST106` - schema non esposto.

### Critical Indexes for Mobile Performance
```sql
-- User-based lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- High-frequency event queries
CREATE INDEX idx_calorie_events_user_timestamp ON calorie_events(user_id, event_timestamp);
CREATE INDEX idx_calorie_events_user_type_timestamp ON calorie_events(user_id, event_type, event_timestamp);

-- Timeline range queries
CREATE INDEX idx_daily_balances_user_date ON daily_balances(user_id, date);
CREATE INDEX idx_calorie_goals_user_start_date ON calorie_goals(user_id, start_date);
```

### Database Performance Features
- **Event sourcing** completo per ricostruzione timeline
- **Pre-computed aggregations** via viste per response sub-second
- **Compound indexes** ottimizzati per query mobile patterns
- **PgBouncer compatibility** con prepared statement gestione UUID
- **Supabase-optimized** per real-time subscriptions

## 🔒 Security & Data Protection

### Row Level Security (RLS)
```sql
-- Users can only access their own data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_policy ON users FOR ALL USING (auth.uid() = id);

ALTER TABLE calorie_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY calorie_events_policy ON calorie_events FOR ALL USING (auth.uid() = user_id);

ALTER TABLE daily_balances ENABLE ROW LEVEL SECURITY;
CREATE POLICY daily_balances_policy ON daily_balances FOR ALL USING (auth.uid() = user_id);

ALTER TABLE calorie_goals ENABLE ROW LEVEL SECURITY;
CREATE POLICY calorie_goals_policy ON calorie_goals FOR ALL USING (auth.uid() = user_id);

ALTER TABLE metabolic_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY metabolic_profiles_policy ON metabolic_profiles FOR ALL USING (auth.uid() = user_id);
```

### Data Validation Constraints
- **Age validation**: 10-120 years
- **Weight/Height validation**: Realistic human ranges
- **Calorie validation**: 0-10,000 calories per event
- **Username validation**: Minimum 3 characters
- **Email validation**: Unique constraint
- **Event type validation**: Enum constraint per eventi validi

## 📱 Mobile Integration Patterns

### High-Frequency Event Collection
```sql
-- Batch insert pattern for mobile sync
INSERT INTO calorie_events (user_id, event_type, value, event_timestamp, source, metadata)
VALUES 
    ($1, 'consumed', 250.5, '2024-01-15 08:30:00+00', 'app', '{"meal_id": "123"}'),
    ($1, 'consumed', 180.0, '2024-01-15 12:45:00+00', 'app', '{"meal_id": "124"}'),
    ($1, 'burned_exercise', 120.0, '2024-01-15 17:20:00+00', 'smartwatch', '{"activity": "running"}');
```

### Real-time Dashboard Queries
```sql
-- Today's balance for user
SELECT * FROM daily_balance_summary 
WHERE user_id = $1 AND date = CURRENT_DATE;

-- Recent events (last 24h)
SELECT * FROM calorie_events 
WHERE user_id = $1 AND event_timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY event_timestamp DESC;

-- Weekly progress
SELECT * FROM weekly_calorie_summary 
WHERE user_id = $1 AND week_start >= DATE_TRUNC('week', NOW() - INTERVAL '4 weeks')
ORDER BY week_start;
```

## 🔄 Migration Strategy

### Deployment Sequence
1. **Tables Creation**: Core tables con tutti i vincoli
2. **Indexes Creation**: Performance indexes per mobile patterns
3. **Views Creation**: Temporal aggregation views
4. **RLS Setup**: Security policies per data isolation
5. **Data Migration**: Migrazione da schema precedente (se necessario)

### Backup & Recovery
- **Automated daily backups** via Supabase
- **Point-in-time recovery** per rollback precisi
- **Event replay capability** per ricostruzione dati da eventi

---

## 📖 API Reference Cross-Mapping

| API Endpoint Pattern | Database Table/View | Operation Type |
|---------------------|-------------------|----------------|
| `/api/v1/users/*` | `users` | CRUD operations |
| `/api/v1/goals/*` | `calorie_goals` | Goal management |
| `/api/v1/calorie-event/*` | `calorie_events` | High-freq event logging |
| `/api/v1/balance/*` | `daily_balances` | Daily aggregations |
| `/api/v1/timeline/*/hourly` | `hourly_calorie_summary` | Real-time analytics |
| `/api/v1/timeline/*/daily` | `daily_calorie_summary` | Daily comparisons |
| `/api/v1/timeline/*/weekly` | `weekly_calorie_summary` | Weekly patterns |
| `/api/v1/timeline/*/monthly` | `monthly_calorie_summary` | Monthly trends |
| `/api/v1/timeline/*/balance` | `daily_balance_summary` | Net calorie tracking |
| `/api/v1/users/*/profile/metabolic` | `metabolic_profiles` | BMR/TDEE management |

## 🎯 Examples Queries

### Basic Operations
```sql
-- Get user with metabolic profile
SELECT u.*, mp.bmr, mp.tdee 
FROM users u 
LEFT JOIN metabolic_profiles mp ON u.id = mp.user_id 
WHERE u.id = $1;

-- Get active goal for user
SELECT * FROM calorie_goals 
WHERE user_id = $1 AND is_active = true 
ORDER BY start_date DESC LIMIT 1;

-- Log calorie consumption event
INSERT INTO calorie_events (user_id, event_type, value, event_timestamp, source, metadata)
VALUES ($1, 'consumed', $2, NOW(), 'app', $3);
```

### Analytics Queries
```sql
-- Weekly calorie trend
SELECT week_start, event_type, total_value, active_days
FROM weekly_calorie_summary 
WHERE user_id = $1 AND week_start >= $2 
ORDER BY week_start, event_type;

-- Daily balance with goals
SELECT db.*, cg.target_calories,
       (db.calories_consumed - (db.calories_burned_exercise + db.calories_burned_bmr)) as net_calories
FROM daily_balances db
JOIN calorie_goals cg ON db.user_id = cg.user_id 
WHERE db.user_id = $1 AND db.date = $2 AND cg.is_active = true;

-- Monthly progress report
SELECT 
    month_start,
    SUM(CASE WHEN event_type = 'consumed' THEN total_value END) as total_consumed,
    SUM(CASE WHEN event_type = 'burned_exercise' THEN total_value END) as total_burned,
    AVG(active_days) as avg_active_days
FROM monthly_calorie_summary 
WHERE user_id = $1 AND month_start >= $2
GROUP BY month_start 
ORDER BY month_start;
```

---

**📅 Ultimo aggiornamento:** 7 settembre 2025  
**🏗️ Schema version:** v2.0 Event-Driven Architecture  
**📱 Ottimizzato per:** Mobile high-frequency sampling + Real-time analytics  
**🔗 Riferimento implementazione:** [services/calorie-balance/create_tables_direct.py](../../services/calorie-balance/create_tables_direct.py)
