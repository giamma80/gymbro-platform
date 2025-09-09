# Supabase Cloud Configuration Template

## Database Strategy per NutriFit Microservizi

### Project Organization
Ogni microservizio ha un proprio progetto Supabase per garantire isolamento e autonomia.

### Required Supabase Projects

| Microservizio | Project Name | Database Schema | Connection Type |
|---------------|--------------|-----------------|-----------------|
| user-management | `nutrifit-user-mgmt` | Users, profiles, auth | Supabase Client |
| calorie-balance | `nutrifit-calorie-balance` | Daily entries, goals | PostgreSQL Direct |
| meal-tracking | `nutrifit-meal-tracking` | Foods, meals, nutrition | Supabase Client |
| health-monitor | `nutrifit-health-monitor` | HealthKit data, metrics | Supabase Client |
| notifications | `nutrifit-notifications` | Push tokens, templates | Supabase Client |
| ai-coach | `nutrifit-ai-coach` | Conversations, vectors | PostgreSQL Direct |

## Environment Variables Template

```bash
# User Management Service - Supabase Client
SUPABASE_USER_MANAGEMENT_URL=https://[project-id].supabase.co
SUPABASE_USER_MANAGEMENT_ANON_KEY=eyJ...
SUPABASE_USER_MANAGEMENT_SERVICE_KEY=eyJ...

# Calorie Balance Service - PostgreSQL Direct  
SUPABASE_CALORIE_BALANCE_URL=https://[project-id].supabase.co
SUPABASE_CALORIE_BALANCE_DB_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
SUPABASE_CALORIE_BALANCE_SERVICE_KEY=eyJ...

# Meal Tracking Service - Supabase Client
SUPABASE_MEAL_TRACKING_URL=https://[project-id].supabase.co
SUPABASE_MEAL_TRACKING_ANON_KEY=eyJ...
SUPABASE_MEAL_TRACKING_SERVICE_KEY=eyJ...

# Health Monitor Service - Supabase Client
SUPABASE_HEALTH_MONITOR_URL=https://[project-id].supabase.co
SUPABASE_HEALTH_MONITOR_ANON_KEY=eyJ...
SUPABASE_HEALTH_MONITOR_SERVICE_KEY=eyJ...

# Notifications Service - Supabase Client
SUPABASE_NOTIFICATIONS_URL=https://[project-id].supabase.co
SUPABASE_NOTIFICATIONS_ANON_KEY=eyJ...
SUPABASE_NOTIFICATIONS_SERVICE_KEY=eyJ...

# AI Coach Service - PostgreSQL Direct
SUPABASE_AI_COACH_URL=https://[project-id].supabase.co
SUPABASE_AI_COACH_DB_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
SUPABASE_AI_COACH_SERVICE_KEY=eyJ...

# Cross-service security
INTER_SERVICE_SECRET_KEY=your-inter-service-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

## Setup Instructions

### 1. Install Supabase CLI
```bash
npm install -g supabase
```

### 2. Create Supabase Projects
```bash
# Login to Supabase
supabase login

# Create projects (manual via Supabase Dashboard)
# https://supabase.com/dashboard/projects
```

### 3. Configure Environment
```bash
# Copy template
cp config/environments/supabase.env.template .env

# Fill in actual values from Supabase dashboard
# Project Settings -> API -> URL and Keys
```

### 4. Validate Configuration
```bash
# Test connection to each project
python scripts/validate-supabase-setup.py
```
