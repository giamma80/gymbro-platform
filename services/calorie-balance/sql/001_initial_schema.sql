-- =============================================================================
-- Calorie Balance Service - Initial Database Schema
-- =============================================================================
-- Project: nutrifit-platform (shared database)
-- Service: calorie-balance  
-- Schema: calorie_balance (dedicated schema to save costs)
-- Phase: 1.0 - Event-Driven Architecture Foundation
-- Date: 11 settembre 2025

-- =============================================================================
-- SCHEMA SETUP - Event-Driven Architecture for High-Frequency Data
-- =============================================================================

-- Create dedicated schema for calorie-balance service
CREATE SCHEMA IF NOT EXISTS calorie_balance;

-- Set search path to use our schema
SET search_path TO calorie_balance, public;

-- Enable required extensions (global)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- CUSTOM ENUMS - calorie_balance schema (with safe creation)
-- =============================================================================

-- Gender enumeration (shared with user-management pattern)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'calorie_balance')) THEN
        CREATE TYPE calorie_balance.gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');
    END IF;
END $$;

-- Event type enumeration for calorie_events
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'calorie_balance')) THEN
        CREATE TYPE calorie_balance.event_type AS ENUM ('consumed', 'burned_exercise', 'burned_bmr', 'weight');
    END IF;
END $$;

-- Event source enumeration for tracking data origin
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_source' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'calorie_balance')) THEN
        CREATE TYPE calorie_balance.event_source AS ENUM ('healthkit', 'google_fit', 'manual', 'app_tracking', 'ai_estimation');
    END IF;
END $$;

-- Goal type enumeration
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'goal_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'calorie_balance')) THEN
        CREATE TYPE calorie_balance.goal_type AS ENUM ('weight_loss', 'weight_gain', 'maintain_weight', 'muscle_gain', 'performance');
    END IF;
END $$;

-- Activity level enumeration for metabolic calculations
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'activity_level' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'calorie_balance')) THEN
        CREATE TYPE calorie_balance.activity_level AS ENUM ('sedentary', 'light', 'moderate', 'high', 'extreme');
    END IF;
END $$;

-- =============================================================================
-- CORE TABLES - Event-Driven Architecture
-- =============================================================================

-- Users table (subset of user-management data relevant to calorie balance)
CREATE TABLE IF NOT EXISTS calorie_balance.users (
    id VARCHAR(255) PRIMARY KEY,  -- UUID from user-management service
    email VARCHAR(255) UNIQUE NOT NULL,
    
    -- Metabolic parameters for calculations
    age INTEGER,
    gender calorie_balance.gender_type,
    height_cm DECIMAL(4,1), -- e.g., 175.5 cm
    current_weight_kg DECIMAL(5,2), -- e.g., 75.50 kg
    target_weight_kg DECIMAL(5,2), -- e.g., 70.00 kg
    activity_level calorie_balance.activity_level DEFAULT 'moderate',
    
    -- Calculated metabolic values (cached for performance)
    bmr_calories DECIMAL(6,1), -- Basal Metabolic Rate
    tdee_calories DECIMAL(6,1), -- Total Daily Energy Expenditure
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT users_age_check CHECK (age BETWEEN 10 AND 120),
    CONSTRAINT users_height_check CHECK (height_cm BETWEEN 50 AND 300),
    CONSTRAINT users_weight_check CHECK (current_weight_kg BETWEEN 20 AND 500),
    CONSTRAINT users_target_weight_check CHECK (target_weight_kg BETWEEN 20 AND 500),
    CONSTRAINT users_bmr_check CHECK (bmr_calories > 0),
    CONSTRAINT users_tdee_check CHECK (tdee_calories > 0)
);

-- Calorie goals table (dynamic goals over time)
CREATE TABLE IF NOT EXISTS calorie_balance.calorie_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES calorie_balance.users(id) ON DELETE CASCADE,
    
    -- Goal configuration
    goal_type calorie_balance.goal_type NOT NULL,
    daily_calorie_target DECIMAL(6,1) NOT NULL, -- e.g., 2000.0 calories
    daily_deficit_target DECIMAL(6,1), -- e.g., -500.0 for weight loss
    weekly_weight_change_kg DECIMAL(4,2), -- e.g., -0.50 kg/week
    
    -- Timeline
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE, -- NULL for ongoing goals
    is_active BOOLEAN DEFAULT TRUE,
    
    -- AI optimization data
    ai_optimized BOOLEAN DEFAULT FALSE,
    optimization_metadata JSONB, -- AI coach adjustments
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT goals_calorie_target_check CHECK (daily_calorie_target BETWEEN 800 AND 5000),
    CONSTRAINT goals_deficit_check CHECK (daily_deficit_target BETWEEN -1500 AND 1500),
    CONSTRAINT goals_weight_change_check CHECK (weekly_weight_change_kg BETWEEN -2.0 AND 2.0),
    CONSTRAINT goals_date_check CHECK (end_date IS NULL OR end_date > start_date)
);

-- 🔥 HIGH-FREQUENCY CALORIE EVENTS TABLE (Event-Driven Core)
CREATE TABLE IF NOT EXISTS calorie_balance.calorie_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES calorie_balance.users(id) ON DELETE CASCADE,
    
    -- Event data
    event_type calorie_balance.event_type NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL, -- Precision to second for mobile sampling
    value DECIMAL(6,1) NOT NULL, -- Calories or weight value
    
    -- Data quality and provenance
    source calorie_balance.event_source NOT NULL DEFAULT 'manual',
    confidence_score DECIMAL(3,2) DEFAULT 1.0, -- 0.0-1.0 quality score
    
    -- Additional context
    metadata JSONB, -- Device info, meal context, exercise type, etc.
    
    -- Performance tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT events_value_check CHECK (value >= 0),
    CONSTRAINT events_confidence_check CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    CONSTRAINT events_weight_range_check CHECK (
        event_type != 'weight' OR (value BETWEEN 20 AND 500)
    ),
    CONSTRAINT events_calorie_range_check CHECK (
        event_type = 'weight' OR (value BETWEEN 0 AND 10000)
    )
);

-- Daily balance table (enhanced for event aggregations)
CREATE TABLE IF NOT EXISTS calorie_balance.daily_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES calorie_balance.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Calorie balance data
    calories_consumed DECIMAL(6,1) DEFAULT 0,
    calories_burned_exercise DECIMAL(6,1) DEFAULT 0,
    calories_burned_bmr DECIMAL(6,1) DEFAULT 0,
    net_calories DECIMAL(7,1) GENERATED ALWAYS AS (calories_consumed - (calories_burned_exercise + calories_burned_bmr)) STORED,
    
    -- Weight tracking
    morning_weight_kg DECIMAL(5,2),
    evening_weight_kg DECIMAL(5,2),
    
    -- Event-driven enhancements
    events_count INTEGER DEFAULT 0, -- Number of events aggregated
    last_event_timestamp TIMESTAMPTZ, -- Most recent event for this day
    data_completeness_score DECIMAL(3,2) DEFAULT 1.0, -- How complete is the day's data
    
    -- Goal progress
    daily_calorie_target DECIMAL(6,1), -- Target for this day (from active goal)
    target_deviation DECIMAL(7,1) GENERATED ALWAYS AS ((calories_consumed - (calories_burned_exercise + calories_burned_bmr)) - COALESCE(daily_calorie_target, 0)) STORED,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, date), -- One balance per user per day
    CONSTRAINT balance_calories_check CHECK (calories_consumed >= 0 AND calories_burned_exercise >= 0 AND calories_burned_bmr >= 0),
    CONSTRAINT balance_weight_check CHECK (morning_weight_kg BETWEEN 20 AND 500 AND evening_weight_kg BETWEEN 20 AND 500),
    CONSTRAINT balance_completeness_check CHECK (data_completeness_score BETWEEN 0.0 AND 1.0),
    CONSTRAINT balance_events_check CHECK (events_count >= 0)
);

-- Metabolic profiles table (AI-optimized metabolic calculations)
CREATE TABLE IF NOT EXISTS calorie_balance.metabolic_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES calorie_balance.users(id) ON DELETE CASCADE,
    
    -- Calculated metabolic values
    bmr_calories DECIMAL(6,1) NOT NULL, -- Basal Metabolic Rate
    tdee_calories DECIMAL(6,1) NOT NULL, -- Total Daily Energy Expenditure
    rmr_calories DECIMAL(6,1), -- Resting Metabolic Rate (if measured)
    
    -- Calculation method and accuracy
    calculation_method VARCHAR(50) DEFAULT 'mifflin_st_jeor', -- harris_benedict, katch_mcardle, etc.
    accuracy_score DECIMAL(3,2) DEFAULT 0.8, -- Estimated accuracy
    
    -- Activity multipliers
    sedentary_multiplier DECIMAL(3,2) DEFAULT 1.2,
    light_multiplier DECIMAL(3,2) DEFAULT 1.375,
    moderate_multiplier DECIMAL(3,2) DEFAULT 1.55,
    high_multiplier DECIMAL(3,2) DEFAULT 1.725,
    extreme_multiplier DECIMAL(3,2) DEFAULT 1.9,
    
    -- AI learning data
    ai_adjusted BOOLEAN DEFAULT FALSE,
    adjustment_factor DECIMAL(4,3) DEFAULT 1.000, -- AI correction factor
    learning_iterations INTEGER DEFAULT 0,
    
    -- Validity period
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT metabolic_bmr_check CHECK (bmr_calories BETWEEN 800 AND 3500),
    CONSTRAINT metabolic_tdee_check CHECK (tdee_calories BETWEEN 1000 AND 8000),
    CONSTRAINT metabolic_accuracy_check CHECK (accuracy_score BETWEEN 0.0 AND 1.0),
    CONSTRAINT metabolic_adjustment_check CHECK (adjustment_factor BETWEEN 0.5 AND 2.0),
    CONSTRAINT metabolic_expires_check CHECK (expires_at > calculated_at)
);

-- =============================================================================
-- PERFORMANCE INDEXES - Mobile-Optimized Queries
-- =============================================================================

-- Calorie events indexes (high-frequency queries)
CREATE INDEX IF NOT EXISTS idx_calorie_events_user_timestamp ON calorie_balance.calorie_events(user_id, event_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_calorie_events_user_type_timestamp ON calorie_balance.calorie_events(user_id, event_type, event_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_calorie_events_timestamp_type ON calorie_balance.calorie_events(event_timestamp, event_type);

-- Daily balances indexes
CREATE INDEX IF NOT EXISTS idx_daily_balances_user_date ON calorie_balance.daily_balances(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_balances_date_range ON calorie_balance.daily_balances(date);

-- Goals indexes
CREATE INDEX IF NOT EXISTS idx_calorie_goals_user_active ON calorie_balance.calorie_goals(user_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_calorie_goals_active_dates ON calorie_balance.calorie_goals(start_date, end_date) WHERE is_active = true;

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON calorie_balance.users(email);
CREATE INDEX IF NOT EXISTS idx_users_updated ON calorie_balance.users(updated_at DESC);

-- Metabolic profiles indexes
CREATE INDEX IF NOT EXISTS idx_metabolic_profiles_user_active ON calorie_balance.metabolic_profiles(user_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_metabolic_profiles_expires ON calorie_balance.metabolic_profiles(expires_at) WHERE is_active = true;

-- =============================================================================
-- BUSINESS LOGIC FUNCTIONS
-- =============================================================================

-- BMR calculation function (Mifflin-St Jeor equation)
CREATE OR REPLACE FUNCTION calorie_balance.calculate_bmr(
    weight_kg DECIMAL,
    height_cm DECIMAL,
    gender calorie_balance.gender_type,
    age_years INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    -- Mifflin-St Jeor Equation
    -- Men: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
    -- Women: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161
    CASE gender
        WHEN 'male' THEN
            RETURN (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + 5;
        WHEN 'female' THEN
            RETURN (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 161;
        ELSE
            -- Average for other/prefer_not_to_say
            RETURN (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 78;
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- TDEE calculation function
CREATE OR REPLACE FUNCTION calorie_balance.calculate_tdee(
    bmr_calories DECIMAL,
    activity_level calorie_balance.activity_level
) RETURNS DECIMAL AS $$
BEGIN
    CASE activity_level
        WHEN 'sedentary' THEN
            RETURN bmr_calories * 1.2;
        WHEN 'light' THEN
            RETURN bmr_calories * 1.375;
        WHEN 'moderate' THEN
            RETURN bmr_calories * 1.55;
        WHEN 'high' THEN
            RETURN bmr_calories * 1.725;
        WHEN 'extreme' THEN
            RETURN bmr_calories * 1.9;
        ELSE
            RETURN bmr_calories * 1.55; -- Default to moderate
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =============================================================================
-- SCHEMA VALIDATION
-- =============================================================================

-- Verify schema creation
SELECT 
    'calorie_balance' as schema_name,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema = 'calorie_balance';

-- Verify enums
SELECT 
    t.typname as enum_name,
    string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_namespace n ON t.typnamespace = n.oid
WHERE n.nspname = 'calorie_balance'
GROUP BY t.typname
ORDER BY t.typname;

-- Reset search path
RESET search_path;
