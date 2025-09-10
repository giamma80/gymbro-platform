# Supabase Cloud Setup Guide - CLOUD-001

**Issue:** CLOUD-001  
**Priority:** 🚨 P10 (CRITICAL - INFRASTRUCTURE)  
**Status:** 🚧 In Implementation  
**Date:** 7 settembre 2025  

## 🎯 Objective

Configurare Supabase Cloud per sostituire il PostgreSQL locale attualmente in uso nel calorie-balance service e preparare l'infrastruttura per tutti i 6 microservizi della piattaforma NutriFit.

## 📋 Current State Analysis

### ❌ Current Issues
- **calorie-balance service** usa PostgreSQL locale con connessione diretta
- **Nessun progetto Supabase Cloud** configurato
- **Database segregation** solo documentata, non implementata nel cloud
- **User Management Service** progettato per Supabase ma non connesso
- **Real-time features** documentate ma impossibili senza Supabase
- **Mobile app authentication** bloccata senza Supabase Auth

### ✅ What We Have
- Complete database schemas progettati per tutti i 6 microservizi
- User Management Service con database design completo
- API roadmaps che assumono Supabase Cloud connectivity
- Docker configurations pronte per environment variables

## 🏗️ Implementation Plan

### Phase 1: Supabase Projects Creation (Week 1)

#### Step 1.1: Create Supabase Projects
Creare 6 progetti Supabase separati per database segregation:

```bash
# Login to Supabase Dashboard
# Create 6 new projects:

1. nutrifit-user-management      # Core authentication
2. nutrifit-calorie-balance      # Energy metabolism
3. nutrifit-meal-tracking        # Food & nutrition
4. nutrifit-health-monitor       # Health data sync
5. nutrifit-notifications        # Messaging system
6. nutrifit-ai-coach            # AI coaching
```

#### Step 1.2: Configure Database Schemas
Per ogni progetto, setup dello schema via SQL Editor:

**1. User Management Database:**
```sql
-- Run user-management schema from docs/databases/user-management-db.md
-- Tables: users, user_profiles, auth_credentials, social_auth_profiles, auth_sessions, privacy_settings
-- Enable Auth in Supabase dashboard
-- Configure RLS policies
```

**2. Calorie Balance Database:**
```sql
-- Migrate existing schema from create_tables_direct.py
-- Tables: users, user_profiles, calorie_goals, metabolic_profiles, calorie_events
-- Temporal views: hourly_calorie_summary, daily_calorie_summary, etc.
-- Add indexes and constraints
```

**3. Meal Tracking Database:**
```sql
-- New schema based on docs/databases/meal-tracking-db.md
-- Tables: meals, food_items, nutrition_data, meal_photos, ai_recognition_logs
-- AI integration tables for GPT-4V results
```

**4. Health Monitor Database:**
```sql
-- New schema based on docs/databases/health-monitor-db.md  
-- Tables: health_metrics, device_syncs, workout_sessions, vital_signs
-- HealthKit/Health Connect integration tables
```

**5. Notifications Database:**
```sql
-- New schema based on docs/databases/notifications-db.md
-- Tables: notification_templates, push_tokens, delivery_logs, user_preferences
-- FCM integration setup
```

**6. AI Coach Database:**
```sql
-- New schema based on docs/databases/ai-coach-db.md
-- Tables: coaching_sessions, conversation_history, rag_documents, user_insights
-- Vector storage for RAG system
```

### Phase 2: Authentication Integration (Week 1-2)

#### Step 2.1: Supabase Auth Configuration
```bash
# In User Management Supabase project:
# 1. Enable Authentication
# 2. Configure Social Providers:
#    - Google OAuth
#    - Apple Sign-In  
#    - Facebook Login
# 3. Configure JWT settings
# 4. Setup email templates
# 5. Configure redirects and domains
```

#### Step 2.2: Update User Management Service
```python
# Update user-management service configuration
DATABASE_URL = "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"
SUPABASE_URL = "https://[project].supabase.co"
SUPABASE_KEY = "[anon_key]"

# Install supabase-py
poetry add supabase

# Create Supabase client for auth operations
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

### Phase 3: Service Migration (Week 2)

#### Step 3.1: Migrate Calorie Balance Service
```python
# Update services/calorie-balance/.env
DATABASE_URL = "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"

# Update database connection in core/database.py
# Test existing endpoints with new connection
# Verify all tables and data migrated correctly
```

#### Step 3.2: Update All Service Configurations
```yaml
# For each microservice, update environment variables:
# services/*/docker/.env

# Calorie Balance
CALORIE_BALANCE_DB_URL = "postgresql://postgres:[password]@db.calorie-balance.supabase.co:5432/postgres"

# Meal Tracking  
MEAL_TRACKING_DB_URL = "postgresql://postgres:[password]@db.meal-tracking.supabase.co:5432/postgres"

# Health Monitor
HEALTH_MONITOR_DB_URL = "postgresql://postgres:[password]@db.health-monitor.supabase.co:5432/postgres"

# Notifications
NOTIFICATIONS_DB_URL = "postgresql://postgres:[password]@db.notifications.supabase.co:5432/postgres"

# AI Coach
AI_COACH_DB_URL = "postgresql://postgres:[password]@db.ai-coach.supabase.co:5432/postgres"

# User Management (includes Supabase Auth)
USER_MANAGEMENT_DB_URL = "postgresql://postgres:[password]@db.user-management.supabase.co:5432/postgres"
SUPABASE_URL = "https://user-management.supabase.co"
SUPABASE_ANON_KEY = "[anon_key]"
SUPABASE_SERVICE_KEY = "[service_key]"
```

### Phase 4: Real-time Features Setup (Week 2-3)

#### Step 4.1: Enable Real-time Subscriptions
```sql
-- In each Supabase project, enable real-time for key tables:

-- User Management: sessions, user_profiles
-- Calorie Balance: calorie_events, daily_calorie_summary  
-- Meal Tracking: meals, nutrition_data
-- Health Monitor: health_metrics, vital_signs
-- Notifications: delivery_logs
-- AI Coach: coaching_sessions, conversation_history
```

#### Step 4.2: Real-time Client Integration
```python
# Add real-time subscriptions to services
# Example for calorie-balance service:

def setup_realtime_subscriptions():
    supabase.table('calorie_events').on('INSERT', handle_new_calorie_event).subscribe()
    supabase.table('daily_calorie_summary').on('UPDATE', handle_summary_update).subscribe()
```

### Phase 5: Security & Performance (Week 3)

#### Step 5.1: Row Level Security (RLS)
```sql
-- Enable RLS on all user-specific tables
-- Example policies:

-- Users can only see their own data
CREATE POLICY "Users can view own data" ON calorie_events
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own data" ON calorie_events  
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

#### Step 5.2: Database Optimization
```sql
-- Add performance indexes for common queries
-- Configure connection pooling
-- Setup automatic backups
-- Monitor query performance
```

### Phase 6: Integration Testing (Week 3-4)

#### Step 6.1: Service Integration Tests
```python
# Test cross-service communication
# Verify user context API works across services  
# Test authentication flow end-to-end
# Verify real-time subscriptions work
```

#### Step 6.2: Load Testing
```python
# Test database performance under load
# Verify connection pooling works
# Test real-time subscription limits
# Monitor resource usage
```

## 📊 Expected Outcomes

### ✅ Infrastructure Ready
- 6 Supabase projects configured with proper schemas
- Database segregation implemented in cloud
- Authentication system centralized and working
- Real-time features enabled for mobile app

### ✅ Service Integration
- All microservices connected to Supabase Cloud
- User Management Service as authentication hub
- Cross-service user context API working
- Local development still possible with cloud DBs

### ✅ Production Readiness
- Managed database infrastructure 
- Automatic scaling and backups
- Global edge network for performance
- Security policies implemented

## 🔧 Environment Configuration

### Development Environment
```bash
# .env.development
NODE_ENV=development
DATABASE_URL=postgresql://postgres:[dev_password]@db.[dev_project].supabase.co:5432/postgres
SUPABASE_URL=https://[dev_project].supabase.co
SUPABASE_ANON_KEY=[dev_anon_key]
```

### Production Environment  
```bash
# .env.production  
NODE_ENV=production
DATABASE_URL=postgresql://postgres:[prod_password]@db.[prod_project].supabase.co:5432/postgres
SUPABASE_URL=https://[prod_project].supabase.co
SUPABASE_ANON_KEY=[prod_anon_key]
```

## 🚨 Migration Risks & Mitigation

### Risk 1: Data Loss During Migration
**Mitigation:**
- Full backup of current PostgreSQL data
- Test migration on development environment first
- Gradual rollout service by service
- Rollback plan prepared

### Risk 2: Authentication Breaking
**Mitigation:**
- Implement User Management Service first
- Test authentication thoroughly in dev
- Maintain backward compatibility during transition
- Monitor auth metrics closely

### Risk 3: Performance Degradation
**Mitigation:**
- Load test before production migration
- Configure connection pooling properly  
- Monitor query performance metrics
- Setup alerts for response time thresholds

## 📈 Success Metrics

### Technical Metrics
- **Database Response Time**: < 100ms for 95% of queries
- **Authentication Success Rate**: > 99.5%
- **Real-time Message Delivery**: < 500ms latency
- **Service Uptime**: > 99.9% availability

### Business Metrics  
- **Mobile App Unblocked**: Authentication and real-time sync working
- **Developer Experience**: Local development seamless with cloud DBs
- **Deployment Ready**: All services can be deployed to production
- **Scalability**: Infrastructure can handle 10x current load

## 🎯 Next Steps After Completion

1. **DEPLOY-001**: Setup Render.com deployment with Supabase integration
2. **MOBILE-001**: Create Flutter app with Supabase authentication  
3. **CLOUD-002**: Enable advanced real-time features
4. **AI-001**: Implement MCP Server with Supabase data integration

---

**Status**: 🚧 Ready for Implementation  
**Estimated Completion**: 3-4 weeks  
**Blockers**: None - highest priority  
**Dependencies**: Supabase account access, service environment variables  
**Risk Level**: Medium (careful migration required)

## 📝 Environment Variables Template

Per configurare rapidamente tutti i microservizi con Supabase:

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
```
