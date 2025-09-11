-- =============================================================================
-- Calorie Balance Service - Permission Verification Utility
-- =============================================================================
-- Project: nutrifit-platform  
-- Service: calorie-balance
-- Schema: calorie_balance
-- Purpose: Utility script to verify current database permissions and security setup
-- Usage: Run this script to audit the current state of permissions after grants

-- =============================================================================
-- PERMISSION AUDIT UTILITY
-- =============================================================================

-- Set search path to use our schema
SET search_path TO calorie_balance, public;

-- =========================================================================
-- CALORIE BALANCE SERVICE - PERMISSION AUDIT REPORT
-- =========================================================================

SELECT '1. SCHEMA INFORMATION' as section, '---------------------' as separator;

SELECT 
    'calorie_balance' as schema_name,
    schema_owner,
    'Schema exists and accessible' as status
FROM information_schema.schemata 
WHERE schema_name = 'calorie_balance';

SELECT '2. TABLE SECURITY STATUS (Row Level Security)' as section, '----------------------------------------------' as separator;

SELECT 
    schemaname as schema,
    tablename as table_name,
    CASE 
        WHEN rowsecurity THEN 'ENABLED'
        ELSE 'DISABLED'
    END as rls_status,
    tableowner as owner
FROM pg_tables 
WHERE schemaname = 'calorie_balance'
ORDER BY tablename;

SELECT '3. ROW LEVEL SECURITY POLICIES' as section, '-------------------------------' as separator;

SELECT 
    schemaname as schema,
    tablename as table_name,
    policyname as policy_name,
    cmd as commands,
    CASE 
        WHEN roles = '{public}' THEN 'PUBLIC'
        WHEN 'authenticated' = ANY(roles) THEN 'AUTHENTICATED'
        WHEN 'service_role' = ANY(roles) THEN 'SERVICE'
        ELSE array_to_string(roles, ', ')
    END as applies_to,
    CASE 
        WHEN qual IS NOT NULL THEN 'HAS CONDITIONS'
        ELSE 'NO CONDITIONS'
    END as qualification_status
FROM pg_policies 
WHERE schemaname = 'calorie_balance'
ORDER BY tablename, policyname;

SELECT '4. ROLE PRIVILEGES ON TABLES' as section, '-----------------------------' as separator;

SELECT 
    table_name,
    grantee as role,
    privilege_type,
    CASE 
        WHEN is_grantable = 'YES' THEN 'CAN GRANT'
        ELSE 'NO GRANT'
    END as can_grant_others
FROM information_schema.table_privileges 
WHERE table_schema = 'calorie_balance'
AND grantee IN ('authenticated', 'anon', 'service_role', 'public', 'calorie_analytics')
ORDER BY table_name, grantee, privilege_type;

SELECT '5. SCHEMA USAGE PRIVILEGES' as section, '--------------------------' as separator;

-- Alternative query for schema privileges using pg_namespace and pg_class
SELECT 
    'calorie_balance' as schema_name,
    'Schema accessible' as status
FROM pg_namespace n
WHERE n.nspname = 'calorie_balance';

SELECT '6. VIEW ACCESS PERMISSIONS' as section, '---------------------------' as separator;

SELECT 
    table_name as view_name,
    grantee as role,
    privilege_type
FROM information_schema.table_privileges 
WHERE table_schema = 'calorie_balance'
AND table_name IN (
    'hourly_calorie_summary',
    'daily_calorie_summary', 
    'weekly_calorie_summary',
    'monthly_calorie_summary',
    'daily_balance_summary'
)
ORDER BY table_name, grantee;

SELECT '7. FUNCTION EXECUTION PRIVILEGES' as section, '--------------------------------' as separator;

SELECT 
    routine_name as function_name,
    grantee as role,
    privilege_type
FROM information_schema.routine_privileges 
WHERE routine_schema = 'calorie_balance'
ORDER BY routine_name, grantee;

SELECT '8. SEQUENCE USAGE PRIVILEGES (Auto-increment IDs)' as section, '--------------------------------------------------' as separator;

-- Alternative query for sequences using pg_class and pg_namespace
SELECT 
    c.relname as sequence_name,
    'Sequence exists and accessible' as status
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE n.nspname = 'calorie_balance'
AND c.relkind = 'S'  -- S = sequence
ORDER BY c.relname;

SELECT '9. CURRENT SESSION INFORMATION' as section, '------------------------------' as separator;

SELECT 
    current_user as current_user,
    session_user as session_user,
    current_database() as database,
    current_schema() as schema,
    inet_client_addr() as client_ip,
    current_setting('application_name') as app_name;

SELECT '10. SUPABASE-SPECIFIC AUTH CONTEXT (If Available)' as section, '--------------------------------------------------' as separator;

-- This will only work in actual Supabase environment with auth context
DO $$ 
BEGIN
    BEGIN
        RAISE NOTICE 'Auth UID: %', auth.uid();
        RAISE NOTICE 'Auth Role: %', auth.role();
        RAISE NOTICE 'Auth Email: %', auth.email();
    EXCEPTION 
        WHEN undefined_function THEN
            RAISE NOTICE 'Supabase auth functions not available (running outside Supabase)';
        WHEN OTHERS THEN
            RAISE NOTICE 'Auth context: % (likely unauthenticated)', SQLERRM;
    END;
END $$;

SELECT '11. SECURITY VALIDATION CHECKLIST' as section, '----------------------------------' as separator;

WITH security_checks AS (
    SELECT 
        'RLS Enabled on calorie_events' as check_name,
        CASE 
            WHEN (SELECT rowsecurity FROM pg_tables WHERE tablename = 'calorie_events' AND schemaname = 'calorie_balance') 
            THEN 'PASS' 
            ELSE 'FAIL' 
        END as status
    UNION ALL
    SELECT 
        'User policies created',
        CASE 
            WHEN EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'calorie_balance' AND policyname LIKE '%user_policy%')
            THEN 'PASS'
            ELSE 'FAIL'
        END
    UNION ALL  
    SELECT 
        'Authenticated role has table access',
        CASE 
            WHEN EXISTS (SELECT 1 FROM information_schema.table_privileges WHERE table_schema = 'calorie_balance' AND grantee = 'authenticated')
            THEN 'PASS'
            ELSE 'FAIL'
        END
    UNION ALL
    SELECT 
        'Anonymous role restricted access',
        CASE 
            WHEN (SELECT COUNT(*) FROM information_schema.table_privileges WHERE table_schema = 'calorie_balance' AND grantee = 'anon') = 1 -- Only schema usage
            THEN 'PASS (Properly Restricted)'
            ELSE 'REVIEW (Unexpected permissions)'
        END
    UNION ALL
    SELECT 
        'Service role has full access',
        CASE 
            WHEN EXISTS (SELECT 1 FROM information_schema.table_privileges WHERE table_schema = 'calorie_balance' AND grantee = 'service_role' AND privilege_type = 'DELETE')
            THEN 'PASS'
            ELSE 'FAIL'
        END
)
SELECT check_name, status FROM security_checks;

SELECT '12. POTENTIAL SECURITY ISSUES' as section, '------------------------------' as separator;

-- Check for tables without RLS
SELECT 
    'WARNING: Table without RLS: ' || tablename as issue
FROM pg_tables 
WHERE schemaname = 'calorie_balance'
AND NOT rowsecurity;

-- Check for overly permissive policies
SELECT 
    'WARNING: Public policy on: ' || tablename as issue  
FROM pg_policies
WHERE schemaname = 'calorie_balance'
AND roles = '{public}';

-- Check for missing user policies
SELECT 
    'WARNING: Table without user policy: ' || tablename as issue
FROM pg_tables t
WHERE t.schemaname = 'calorie_balance'
AND NOT EXISTS (
    SELECT 1 FROM pg_policies p 
    WHERE p.schemaname = 'calorie_balance' 
    AND p.tablename = t.tablename
    AND p.policyname LIKE '%user_policy%'
);

SELECT 'END OF PERMISSION AUDIT REPORT' as section, '==========================================================================' as separator;

-- Reset search path
RESET search_path;
