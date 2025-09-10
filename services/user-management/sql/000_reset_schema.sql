-- =============================================================================
-- User Management Service - Database Reset Script
-- =============================================================================
-- Use this script if you need to completely reset the database schema
-- WARNING: This will delete ALL data in the user_management schema!

-- =============================================================================
-- CLEANUP SCRIPT - Use with caution!
-- =============================================================================

-- Drop all tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS user_management.email_verification_tokens CASCADE;
DROP TABLE IF EXISTS user_management.password_reset_tokens CASCADE;
DROP TABLE IF EXISTS user_management.audit_logs CASCADE;
DROP TABLE IF EXISTS user_management.social_auth_profiles CASCADE;
DROP TABLE IF EXISTS user_management.auth_sessions CASCADE;
DROP TABLE IF EXISTS user_management.auth_credentials CASCADE;
DROP TABLE IF EXISTS user_management.privacy_settings CASCADE;
DROP TABLE IF EXISTS user_management.user_profiles CASCADE;
DROP TABLE IF EXISTS user_management.users CASCADE;

-- Drop all views
DROP VIEW IF EXISTS user_management.user_service_context CASCADE;

-- Drop all functions
DROP FUNCTION IF EXISTS user_management.update_updated_at_column() CASCADE;

-- Drop all types
DROP TYPE IF EXISTS user_management.social_auth_status CASCADE;
DROP TYPE IF EXISTS user_management.auth_provider CASCADE;
DROP TYPE IF EXISTS user_management.device_type CASCADE;
DROP TYPE IF EXISTS user_management.session_status CASCADE;
DROP TYPE IF EXISTS user_management.credential_status CASCADE;
DROP TYPE IF EXISTS user_management.gender_type CASCADE;
DROP TYPE IF EXISTS user_management.user_status CASCADE;

-- Drop the entire schema (optional - use with extreme caution)
-- DROP SCHEMA IF EXISTS user_management CASCADE;

-- Reset complete! You can now run 001_initial_schema.sql again.
