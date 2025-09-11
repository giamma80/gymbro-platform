-- =============================================================================
-- Calorie Balance Service - Database Grants & Permissions  
-- =============================================================================
-- Project: nutrifit-platform
-- Service: calorie-balance
-- Schema: calorie_balance
-- Phase: 1.1 - Security & Access Control
-- Date: 11 settembre 2025
-- Purpose: Configure Row Level Security and role-based access control

-- =============================================================================
-- SUPABASE SECURITY MODEL
-- =============================================================================

-- Set search path to use our schema
SET search_path TO calorie_balance, public;

-- =============================================================================
-- 1. ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- =============================================================================

-- Core event table - highest security priority
ALTER TABLE calorie_balance.calorie_events ENABLE ROW LEVEL SECURITY;

-- Aggregated data tables
ALTER TABLE calorie_balance.daily_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE calorie_balance.calorie_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE calorie_balance.metabolic_profiles ENABLE ROW LEVEL SECURITY;

-- User data subset (if external apps need direct access)
ALTER TABLE calorie_balance.users ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- 2. ANONYMOUS USER POLICIES (Public access - very limited)
-- =============================================================================

-- Anonymous users can only access public health information (none for calorie data)
-- No policies needed - calorie data is sensitive and private

-- =============================================================================
-- 3. AUTHENTICATED USER POLICIES (User can only access their own data)
-- =============================================================================

-- CALORIE EVENTS - Users can only access their own calorie events
CREATE POLICY calorie_events_user_policy ON calorie_balance.calorie_events
    FOR ALL 
    USING (auth.uid()::text = user_id);

-- DAILY BALANCES - Users can only access their own daily summaries  
CREATE POLICY daily_balances_user_policy ON calorie_balance.daily_balances
    FOR ALL
    USING (auth.uid()::text = user_id);

-- CALORIE GOALS - Users can only access their own goals
CREATE POLICY calorie_goals_user_policy ON calorie_balance.calorie_goals
    FOR ALL
    USING (auth.uid()::text = user_id);

-- METABOLIC PROFILES - Users can only access their own metabolic data
CREATE POLICY metabolic_profiles_user_policy ON calorie_balance.metabolic_profiles
    FOR ALL
    USING (auth.uid()::text = user_id);

-- USERS - Users can only access their own user record
CREATE POLICY users_user_policy ON calorie_balance.users
    FOR ALL
    USING (auth.uid()::text = id);

-- =============================================================================
-- 4. SERVICE ROLE POLICIES (Full access for backend services)
-- =============================================================================

-- Service role bypasses RLS automatically in Supabase
-- These policies are for additional service-specific roles if needed

CREATE POLICY calorie_events_service_policy ON calorie_balance.calorie_events
    FOR ALL
    USING (current_setting('role') = 'service_role');

CREATE POLICY daily_balances_service_policy ON calorie_balance.daily_balances  
    FOR ALL
    USING (current_setting('role') = 'service_role');

-- =============================================================================
-- 5. ROLE-BASED GRANTS FOR SUPABASE AUTHENTICATION
-- =============================================================================

-- Grant usage on schema to authenticated users
GRANT USAGE ON SCHEMA calorie_balance TO authenticated;
GRANT USAGE ON SCHEMA calorie_balance TO anon;

-- =============================================================================
-- AUTHENTICATED USER GRANTS (Standard app users)
-- =============================================================================

-- Table access for authenticated users (RLS will restrict to own data)
GRANT SELECT, INSERT, UPDATE, DELETE ON calorie_balance.calorie_events TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON calorie_balance.daily_balances TO authenticated;  
GRANT SELECT, INSERT, UPDATE, DELETE ON calorie_balance.calorie_goals TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON calorie_balance.metabolic_profiles TO authenticated;
GRANT SELECT, UPDATE ON calorie_balance.users TO authenticated;

-- Sequence access for auto-incrementing IDs
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA calorie_balance TO authenticated;

-- View access for analytics (RLS policies will apply to underlying tables)
GRANT SELECT ON calorie_balance.hourly_calorie_summary TO authenticated;
GRANT SELECT ON calorie_balance.daily_calorie_summary TO authenticated;
GRANT SELECT ON calorie_balance.weekly_calorie_summary TO authenticated;
GRANT SELECT ON calorie_balance.monthly_calorie_summary TO authenticated;
GRANT SELECT ON calorie_balance.daily_balance_summary TO authenticated;

-- Function execution for business logic
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA calorie_balance TO authenticated;

-- =============================================================================
-- ANONYMOUS USER GRANTS (Very limited - health education content only)
-- =============================================================================

-- Anonymous users get no access to personal calorie data
-- Only public health information if we add such tables later

-- =============================================================================
-- SERVICE ROLE GRANTS (Backend microservice access)
-- =============================================================================

-- Full schema access for service operations
GRANT ALL PRIVILEGES ON SCHEMA calorie_balance TO service_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA calorie_balance TO service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA calorie_balance TO service_role;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA calorie_balance TO service_role;
GRANT ALL PRIVILEGES ON ALL ROUTINES IN SCHEMA calorie_balance TO service_role;

-- =============================================================================
-- 6. CUSTOM ROLE FOR ANALYTICS (Optional - for future BI tools)
-- =============================================================================

-- Create analytics role for business intelligence tools
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'calorie_analytics') THEN
        CREATE ROLE calorie_analytics;
    END IF;
END $$;

-- Read-only access to aggregated data for analytics role
GRANT USAGE ON SCHEMA calorie_balance TO calorie_analytics;
GRANT SELECT ON calorie_balance.daily_balances TO calorie_analytics;
GRANT SELECT ON calorie_balance.calorie_goals TO calorie_analytics;
GRANT SELECT ON calorie_balance.metabolic_profiles TO calorie_analytics;

-- Analytics views access (no access to raw events for privacy)
GRANT SELECT ON calorie_balance.daily_calorie_summary TO calorie_analytics;
GRANT SELECT ON calorie_balance.weekly_calorie_summary TO calorie_analytics;
GRANT SELECT ON calorie_balance.monthly_calorie_summary TO calorie_analytics;
GRANT SELECT ON calorie_balance.daily_balance_summary TO calorie_analytics;

-- =============================================================================
-- 7. SECURITY AUDIT FUNCTIONS
-- =============================================================================

-- Function to check current user's permissions
CREATE OR REPLACE FUNCTION calorie_balance.check_user_permissions()
RETURNS TABLE (
    table_name text,
    privilege_type text,
    is_grantable boolean
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_name::text,
        t.privilege_type::text,
        t.is_grantable::boolean
    FROM information_schema.table_privileges t
    WHERE t.table_schema = 'calorie_balance'
    AND t.grantee = CURRENT_USER
    ORDER BY t.table_name, t.privilege_type;
END;
$$;

-- Function to audit RLS policies
CREATE OR REPLACE FUNCTION calorie_balance.audit_rls_policies()
RETURNS TABLE (
    table_name text,
    policy_name text,
    command text,
    roles text[],
    qual text
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.tablename::text,
        p.policyname::text,
        p.cmd::text,
        p.roles,
        p.qual::text
    FROM pg_policies p
    WHERE p.schemaname = 'calorie_balance'
    ORDER BY p.tablename, p.policyname;
END;
$$;

-- Grant execute permissions on audit functions
GRANT EXECUTE ON FUNCTION calorie_balance.check_user_permissions() TO authenticated;
GRANT EXECUTE ON FUNCTION calorie_balance.check_user_permissions() TO service_role;
GRANT EXECUTE ON FUNCTION calorie_balance.audit_rls_policies() TO service_role;

-- =============================================================================
-- 8. VALIDATION QUERIES
-- =============================================================================

-- Verify RLS is enabled on all tables
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'calorie_balance'
ORDER BY tablename;

-- Verify policies are created  
SELECT 
    schemaname,
    tablename,
    policyname,
    cmd as command,
    roles
FROM pg_policies 
WHERE schemaname = 'calorie_balance'
ORDER BY tablename, policyname;

-- Verify role grants
SELECT 
    table_schema,
    table_name,
    privilege_type,
    grantee
FROM information_schema.table_privileges 
WHERE table_schema = 'calorie_balance'
AND grantee IN ('authenticated', 'anon', 'service_role', 'calorie_analytics')
ORDER BY table_name, grantee, privilege_type;

-- Reset search path
RESET search_path;
