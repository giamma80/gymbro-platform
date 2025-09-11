-- =============================================================================
-- Calorie Balance Service - Reset Schema Script
-- =============================================================================
-- Project: nutrifit-platform (shared database)
-- Service: calorie-balance
-- Schema: calorie_balance (dedicated schema)
-- Purpose: Reset schema for development/testing
-- Date: 11 settembre 2025

-- WARNING: This script DESTROYS ALL DATA in the calorie_balance schema
-- Use only in development/testing environments

-- =============================================================================
-- CLEANUP SEQUENCE (Reverse order of dependencies)
-- =============================================================================

-- Set search path
SET search_path TO calorie_balance, public;

-- Drop views first (depend on tables)
DROP VIEW IF EXISTS calorie_balance.daily_balance_summary CASCADE;
DROP VIEW IF EXISTS calorie_balance.monthly_calorie_summary CASCADE;
DROP VIEW IF EXISTS calorie_balance.weekly_calorie_summary CASCADE;
DROP VIEW IF EXISTS calorie_balance.daily_calorie_summary CASCADE;
DROP VIEW IF EXISTS calorie_balance.hourly_calorie_summary CASCADE;

-- Drop tables (respect foreign key dependencies)
DROP TABLE IF EXISTS calorie_balance.metabolic_profiles CASCADE;
DROP TABLE IF EXISTS calorie_balance.daily_balances CASCADE;
DROP TABLE IF EXISTS calorie_balance.calorie_events CASCADE;
DROP TABLE IF EXISTS calorie_balance.calorie_goals CASCADE;
DROP TABLE IF EXISTS calorie_balance.users CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS calorie_balance.calculate_bmr(DECIMAL, INTEGER, gender_type, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS calorie_balance.calculate_tdee(DECIMAL, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS calorie_balance.update_daily_balance_from_events() CASCADE;

-- Drop custom types (enums)
DROP TYPE IF EXISTS calorie_balance.event_type CASCADE;
DROP TYPE IF EXISTS calorie_balance.event_source CASCADE;
DROP TYPE IF EXISTS calorie_balance.goal_type CASCADE;
DROP TYPE IF EXISTS calorie_balance.activity_level CASCADE;
DROP TYPE IF EXISTS calorie_balance.gender_type CASCADE;

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_daily_balance ON calorie_balance.calorie_events CASCADE;

-- Drop indexes (will be recreated with tables)
-- No explicit drops needed as they cascade with tables

-- =============================================================================
-- SCHEMA CLEANUP
-- =============================================================================

-- Drop the entire schema (if exists)
DROP SCHEMA IF EXISTS calorie_balance CASCADE;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify schema is gone
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'calorie_balance')
        THEN '❌ ERROR: Schema calorie_balance still exists!'
        ELSE '✅ SUCCESS: Schema calorie_balance has been removed'
    END as reset_status;

RESET search_path;
