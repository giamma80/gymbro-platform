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
-- CUSTOM ENUMS - user_management schema (with safe creation)
-- =============================================================================

-- User status enumeration (create if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
    END IF;
END $$;

-- Gender enumeration for profiles
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');
    END IF;
END $$;

-- Authentication enums (create if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'credential_status' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.credential_status AS ENUM ('active', 'expired', 'disabled');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'session_status' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.session_status AS ENUM ('active', 'expired', 'revoked');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'device_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.device_type AS ENUM ('mobile', 'web', 'desktop');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'auth_provider' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.auth_provider AS ENUM ('google', 'apple', 'facebook');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'social_auth_status' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'user_management')) THEN
        CREATE TYPE user_management.social_auth_status AS ENUM ('active', 'revoked', 'expired');
    END IF;
END $$;

-- =============================================================================
-- CORE TABLES - Phase 1 (user_management schema) - Safe Creation
-- =============================================================================

-- 1. Users table (core identity) - FOUNDATION
CREATE TABLE IF NOT EXISTS user_management.users (
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
CREATE TABLE IF NOT EXISTS user_management.user_profiles (
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
CREATE TABLE IF NOT EXISTS user_management.privacy_settings (
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

-- 4. Auth credentials table (password management) - AUTHENTICATION
CREATE TABLE IF NOT EXISTS user_management.auth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    status user_management.credential_status DEFAULT 'active',
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_credentials UNIQUE(user_id),
    CONSTRAINT failed_attempts_check CHECK (failed_attempts >= 0 AND failed_attempts <= 10)
);

-- 5. Auth sessions table (JWT session management) - AUTHENTICATION
CREATE TABLE IF NOT EXISTS user_management.auth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NOT NULL,
    device_id VARCHAR(255),
    device_type user_management.device_type,
    user_agent TEXT,
    ip_address INET,
    location VARCHAR(255),
    status user_management.session_status DEFAULT 'active',
    expires_at TIMESTAMP NOT NULL,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_session_token UNIQUE(session_token),
    CONSTRAINT unique_refresh_token UNIQUE(refresh_token),
    CONSTRAINT expires_future CHECK (expires_at > created_at)
);

-- 6. Social auth profiles table (OAuth integration) - AUTHENTICATION
CREATE TABLE IF NOT EXISTS user_management.social_auth_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    provider user_management.auth_provider NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    provider_data JSONB DEFAULT '{}',
    status user_management.social_auth_status DEFAULT 'active',
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_provider_user UNIQUE(provider, provider_user_id),
    CONSTRAINT unique_user_provider UNIQUE(user_id, provider)
);

-- 7. Audit logs table (security and compliance) - SECURITY
CREATE TABLE IF NOT EXISTS user_management.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_management.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Password reset tokens table - AUTHENTICATION  
CREATE TABLE IF NOT EXISTS user_management.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT token_not_expired CHECK (expires_at > created_at)
);

-- 9. Email verification tokens table - AUTHENTICATION
CREATE TABLE IF NOT EXISTS user_management.email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT verification_token_not_expired CHECK (expires_at > created_at)
);

-- =============================================================================
-- INDEXES - Performance Optimization (user_management schema) - Safe Creation
-- =============================================================================

-- Core user lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON user_management.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON user_management.users(username);
CREATE INDEX IF NOT EXISTS idx_users_status ON user_management.users(status);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON user_management.users(last_login_at);

-- User profiles
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_management.user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_display_name ON user_management.user_profiles(display_name);

-- Privacy settings
CREATE UNIQUE INDEX IF NOT EXISTS idx_privacy_settings_user_id ON user_management.privacy_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_given ON user_management.privacy_settings(consent_given_at);

-- Auth credentials
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_credentials_user_id ON user_management.auth_credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_credentials_status ON user_management.auth_credentials(status);

-- Auth sessions  
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON user_management.auth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_status ON user_management.auth_sessions(status);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires ON user_management.auth_sessions(expires_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_sessions_token ON user_management.auth_sessions(session_token);
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_sessions_refresh ON user_management.auth_sessions(refresh_token);

-- Social auth profiles
CREATE INDEX IF NOT EXISTS idx_social_auth_user_id ON user_management.social_auth_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_social_auth_provider ON user_management.social_auth_profiles(provider);
CREATE UNIQUE INDEX IF NOT EXISTS idx_social_auth_provider_user ON user_management.social_auth_profiles(provider, provider_user_id);

-- Audit logs (for performance)
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON user_management.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON user_management.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON user_management.audit_logs(created_at);

-- Password reset tokens
CREATE INDEX IF NOT EXISTS idx_password_reset_user_id ON user_management.password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_expires ON user_management.password_reset_tokens(expires_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_password_reset_token ON user_management.password_reset_tokens(token);

-- Email verification tokens
CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON user_management.email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_expires ON user_management.email_verification_tokens(expires_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_email_verification_token ON user_management.email_verification_tokens(token);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_users_active_verified ON user_management.users(status, email_verified_at) WHERE status = 'active';

-- =============================================================================
-- VIEWS - Service Integration (user_management schema) - Safe Creation
-- =============================================================================

-- Drop existing view if it exists and recreate
DROP VIEW IF EXISTS user_management.user_service_context;

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
-- TRIGGERS - Auto-update timestamps (user_management schema) - Safe Creation
-- =============================================================================

-- Function to update timestamps (create or replace)
CREATE OR REPLACE FUNCTION user_management.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist before creating new ones
DROP TRIGGER IF EXISTS update_users_updated_at ON user_management.users;
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_management.user_profiles;
DROP TRIGGER IF EXISTS update_privacy_settings_updated_at ON user_management.privacy_settings;
DROP TRIGGER IF EXISTS update_auth_credentials_updated_at ON user_management.auth_credentials;
DROP TRIGGER IF EXISTS update_social_auth_profiles_updated_at ON user_management.social_auth_profiles;

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

CREATE TRIGGER update_auth_credentials_updated_at 
    BEFORE UPDATE ON user_management.auth_credentials 
    FOR EACH ROW EXECUTE FUNCTION user_management.update_updated_at_column();

CREATE TRIGGER update_social_auth_profiles_updated_at 
    BEFORE UPDATE ON user_management.social_auth_profiles 
    FOR EACH ROW EXECUTE FUNCTION user_management.update_updated_at_column();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) - Basic Setup (user_management schema) - Safe Creation
-- =============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE user_management.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.privacy_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.auth_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.auth_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.social_auth_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Service role full access" ON user_management.users;
DROP POLICY IF EXISTS "Service role full access" ON user_management.user_profiles;
DROP POLICY IF EXISTS "Service role full access" ON user_management.privacy_settings;
DROP POLICY IF EXISTS "Service role full access" ON user_management.auth_credentials;
DROP POLICY IF EXISTS "Service role full access" ON user_management.auth_sessions;
DROP POLICY IF EXISTS "Service role full access" ON user_management.social_auth_profiles;

-- Basic RLS policies (to be expanded in Phase 2)
-- For now, allow service role full access
CREATE POLICY "Service role full access" ON user_management.users
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.user_profiles
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.privacy_settings
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.auth_credentials
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.auth_sessions
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_management.social_auth_profiles
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
