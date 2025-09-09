-- =============================================================================
-- User Management Service - Initial Database Schema
-- =============================================================================
-- Project: nutrifit-platform (shared database)
-- Service: user-management  
-- Schema: user_management (dedicated schema to save costs)
-- Phase: 1.0 - Foundation Setup
-- Date: 9 settembre 2025

-- =============================================================================
-- SCHEMA SETUP - Cost-Effective Multi-Service Database
-- =============================================================================

-- Create dedicated schema for user-management service
CREATE SCHEMA IF NOT EXISTS user_management;

-- Set search path to use our schema
SET search_path TO user_management, public;

-- Enable required extensions (global)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- CUSTOM ENUMS - user_management schema
-- =============================================================================

-- User status enumeration
CREATE TYPE user_management.user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');

-- Gender enumeration for profiles
CREATE TYPE user_management.gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');

-- =============================================================================
-- CORE TABLES - Phase 1 (user_management schema)
-- =============================================================================

-- 1. Users table (core identity) - FOUNDATION
CREATE TABLE user_management.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    status user_management.user_status DEFAULT 'active',
    email_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT username_format CHECK (username ~* '^[a-zA-Z0-9_]{3,50}$')
);

-- 2. User profiles table (extended info) - FOUNDATION
CREATE TABLE user_management.user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(150),
    avatar_url TEXT,
    date_of_birth DATE,
    gender user_management.gender_type,
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en-US',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_profile UNIQUE(user_id),
    CONSTRAINT age_check CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '13 years')
);

-- 3. Privacy settings table (GDPR compliance) - FOUNDATION
CREATE TABLE user_management.privacy_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    data_processing_consent BOOLEAN DEFAULT false,
    marketing_consent BOOLEAN DEFAULT false,
    analytics_consent BOOLEAN DEFAULT false,
    profile_visibility BOOLEAN DEFAULT false,
    health_data_sharing BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}',
    consent_given_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_privacy UNIQUE(user_id)
);

-- =============================================================================
-- INDEXES - Performance Optimization (user_management schema)
-- =============================================================================

-- Core user lookups
CREATE INDEX idx_users_email ON user_management.users(email);
CREATE INDEX idx_users_username ON user_management.users(username);
CREATE INDEX idx_users_status ON user_management.users(status);
CREATE INDEX idx_users_last_login ON user_management.users(last_login_at);

-- User profiles
CREATE UNIQUE INDEX idx_user_profiles_user_id ON user_management.user_profiles(user_id);
CREATE INDEX idx_user_profiles_display_name ON user_management.user_profiles(display_name);

-- Privacy settings
CREATE UNIQUE INDEX idx_privacy_settings_user_id ON user_management.privacy_settings(user_id);
CREATE INDEX idx_privacy_consent_given ON user_management.privacy_settings(consent_given_at);

-- Composite indexes for common queries
CREATE INDEX idx_users_active_verified ON user_management.users(status, email_verified_at) WHERE status = 'active';

-- =============================================================================
-- VIEWS - Service Integration (user_management schema)
-- =============================================================================

-- User context view for other microservices (GraphQL Federation)
CREATE VIEW user_management.user_service_context AS
SELECT 
    u.id as user_id,
    u.email,
    u.username,
    u.status as user_status,
    u.email_verified_at,
    up.display_name,
    up.first_name,
    up.last_name,
    up.timezone,
    up.locale,
    up.preferences,
    ps.health_data_sharing,
    ps.analytics_consent,
    u.created_at,
    u.updated_at
FROM user_management.users u
LEFT JOIN user_management.user_profiles up ON u.id = up.user_id
LEFT JOIN user_management.privacy_settings ps ON u.id = ps.user_id
WHERE u.status = 'active';

-- =============================================================================
-- TRIGGERS - Auto-update timestamps (user_management schema)
-- =============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION user_management.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating timestamps
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON user_management.users 
    FOR EACH ROW EXECUTE FUNCTION user_management.update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_management.user_profiles 
    FOR EACH ROW EXECUTE FUNCTION user_management.update_updated_at_column();

CREATE TRIGGER update_privacy_settings_updated_at 
    BEFORE UPDATE ON user_management.privacy_settings 
    FOR EACH ROW EXECUTE FUNCTION user_management.update_updated_at_column();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) - Basic Setup (user_management schema)
-- =============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE user_management.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.privacy_settings ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (to be expanded in Phase 2)
-- For now, allow service role full access
CREATE POLICY "Service role full access" ON user_management.users
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.user_profiles
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.privacy_settings
    FOR ALL USING (true);

-- =============================================================================
-- SAMPLE DATA - Development Only (user_management schema)
-- =============================================================================

-- Insert sample user for testing
INSERT INTO user_management.users (id, email, username, status, email_verified_at) 
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'test@nutrifit.com',
    'testuser',
    'active',
    CURRENT_TIMESTAMP
) ON CONFLICT (email) DO NOTHING;

-- Insert sample profile
INSERT INTO user_management.user_profiles (user_id, first_name, last_name, display_name, gender, timezone, locale)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Test',
    'User',
    'Test User',
    'other',
    'Europe/Rome',
    'it-IT'
) ON CONFLICT (user_id) DO NOTHING;

-- Insert sample privacy settings
INSERT INTO user_management.privacy_settings (user_id, data_processing_consent, analytics_consent)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    true,
    true
) ON CONFLICT (user_id) DO NOTHING;

-- =============================================================================
-- VERIFICATION QUERIES (user_management schema)
-- =============================================================================

-- Test queries to verify setup
-- SELECT * FROM user_management.users;
-- SELECT * FROM user_management.user_profiles;
-- SELECT * FROM user_management.privacy_settings;
-- SELECT * FROM user_management.user_service_context;

-- Verify constraints
-- INSERT INTO user_management.users (email, username) VALUES ('invalid-email', 'te'); -- Should fail
-- INSERT INTO user_profiles (user_id, date_of_birth) VALUES ('00000000-0000-0000-0000-000000000001', '2020-01-01'); -- Should fail (too young)

-- =============================================================================
-- SCHEMA COMPLETE - PHASE 1
-- =============================================================================
-- Tables created: users, user_profiles, privacy_settings
-- Views created: user_service_context
-- Ready for user-management service implementation
-- Next Phase: Authentication tables (auth_credentials, auth_sessions)
-- =============================================================================
