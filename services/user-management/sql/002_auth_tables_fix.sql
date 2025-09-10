-- =============================================================================
-- User Management Service - Schema Update 002
-- =============================================================================
-- Project: nutrifit-platform
-- Service: user-management  
-- Schema: user_management
-- Phase: 1.1 - Authentication Tables Fix
-- Date: 10 settembre 2025
-- Purpose: Ensure all authentication tables exist with correct fields

-- =============================================================================
-- AUTHENTICATION TABLES UPDATE
-- =============================================================================

-- Set search path to use our schema
SET search_path TO user_management, public;

-- Ensure auth_credentials table exists with all required fields
CREATE TABLE IF NOT EXISTS user_management.auth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_management.users(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    status user_management.credential_status DEFAULT 'active',
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login TIMESTAMP,
    requires_password_change BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_credentials UNIQUE(user_id),
    CONSTRAINT failed_attempts_check CHECK (failed_attempts >= 0 AND failed_attempts <= 10)
);

-- Add missing columns if they don't exist (safe updates)
DO $$ 
BEGIN
    -- Add last_login column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'user_management' 
        AND table_name = 'auth_credentials' 
        AND column_name = 'last_login'
    ) THEN
        ALTER TABLE user_management.auth_credentials 
        ADD COLUMN last_login TIMESTAMP;
    END IF;
    
    -- Add requires_password_change column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'user_management' 
        AND table_name = 'auth_credentials' 
        AND column_name = 'requires_password_change'
    ) THEN
        ALTER TABLE user_management.auth_credentials 
        ADD COLUMN requires_password_change BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Ensure auth_sessions table exists (compatible with 001 schema)
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

-- Ensure password reset tokens table exists (compatible with 001 schema)
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

-- Ensure email verification tokens table exists (compatible with 001 schema)
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

-- Ensure audit_logs table exists (compatible with 001 schema)
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

-- =============================================================================
-- INDEXES AND CONSTRAINTS
-- =============================================================================

-- Auth credentials indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_credentials_user_id 
    ON user_management.auth_credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_credentials_status 
    ON user_management.auth_credentials(status);
CREATE INDEX IF NOT EXISTS idx_auth_credentials_last_login 
    ON user_management.auth_credentials(last_login);

-- Auth sessions indexes (compatible with 001 schema)
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_sessions_token 
    ON user_management.auth_sessions(session_token);
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_sessions_refresh_token 
    ON user_management.auth_sessions(refresh_token);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id 
    ON user_management.auth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at 
    ON user_management.auth_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_status 
    ON user_management.auth_sessions(status);

-- Password reset tokens indexes
CREATE INDEX IF NOT EXISTS idx_password_reset_user_id 
    ON user_management.password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_expires 
    ON user_management.password_reset_tokens(expires_at);

-- Email verification tokens indexes
CREATE INDEX IF NOT EXISTS idx_email_verification_user_id 
    ON user_management.email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_expires 
    ON user_management.email_verification_tokens(expires_at);

-- Audit logs indexes (compatible with 001 schema)
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
    ON user_management.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
    ON user_management.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource 
    ON user_management.audit_logs(resource);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at 
    ON user_management.audit_logs(created_at);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================================================

-- Drop existing triggers if they exist, then recreate them
DROP TRIGGER IF EXISTS update_auth_credentials_updated_at ON user_management.auth_credentials;

-- Auth credentials trigger (only for auth_credentials as it has updated_at)
CREATE TRIGGER update_auth_credentials_updated_at 
    BEFORE UPDATE ON user_management.auth_credentials 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE user_management.auth_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.auth_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.email_verification_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_management.audit_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist, then recreate them
DROP POLICY IF EXISTS "Service role full access" ON user_management.auth_credentials;
DROP POLICY IF EXISTS "Service role full access" ON user_management.auth_sessions;
DROP POLICY IF EXISTS "Service role full access" ON user_management.password_reset_tokens;
DROP POLICY IF EXISTS "Service role full access" ON user_management.email_verification_tokens;
DROP POLICY IF EXISTS "Service role full access" ON user_management.audit_logs;

-- Service role policies (full access for backend services)
CREATE POLICY "Service role full access" ON user_management.auth_credentials
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access" ON user_management.auth_sessions
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access" ON user_management.password_reset_tokens
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access" ON user_management.email_verification_tokens
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access" ON user_management.audit_logs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- =============================================================================
-- COMPLETION
-- =============================================================================

-- Log completion (compatible with 001 audit_logs schema)
DO $$ 
BEGIN
    -- Try to insert completion log with 001-compatible structure
    BEGIN
        INSERT INTO user_management.audit_logs (action, resource, data)
        VALUES (
            'create',
            'schema_update_002',
            '{"status": "completed", "timestamp": "' || CURRENT_TIMESTAMP || '", "tables": ["auth_credentials", "auth_sessions", "password_reset_tokens", "email_verification_tokens", "audit_logs"]}'
        );
    EXCEPTION 
        WHEN OTHERS THEN
            -- If audit_logs still has issues, just log to console
            RAISE NOTICE 'Could not log to audit_logs table: %', SQLERRM;
            RAISE NOTICE 'Schema update 002 completed anyway';
    END;
END $$;

-- Final message
DO $$ 
BEGIN
    RAISE NOTICE 'Schema update 002 completed successfully!';
    RAISE NOTICE 'Authentication tables are now ready with all required fields.';
    RAISE NOTICE 'Tables created/updated: auth_credentials, auth_sessions, password_reset_tokens, email_verification_tokens, audit_logs';
END $$;
