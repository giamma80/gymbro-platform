-- =============================================================================
-- Debug Script - Verifica stato attuale schema calorie_balance
-- =============================================================================

-- Test 1: Info sessione corrente
SELECT current_user, current_database(), version();

-- Test 2: Tutti gli schemi disponibili
SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;

-- Test 3: Verifica schema calorie_balance
SELECT COUNT(*) as schema_exists FROM information_schema.schemata WHERE schema_name = 'calorie_balance';

-- Test 4: Tutte le tabelle in tutti gli schemi
SELECT schemaname, tablename FROM pg_tables ORDER BY schemaname, tablename;

-- Test 5: Verifica search path
SHOW search_path;