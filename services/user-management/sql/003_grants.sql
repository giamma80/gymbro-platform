-- 003_grants.sql
-- Purpose: Grant minimal read access to the public/anon role for local/dev clients.
-- Run this in Supabase SQL editor after you created the schema and tables.

-- NOTE: Replace "anon" below with the specific role your frontend/anon clients use
-- if you differ from the default Supabase setup.

BEGIN;

-- Ensure the schema exists
CREATE SCHEMA IF NOT EXISTS user_management;

-- Allow usage of the schema to anon (or your chosen role)
GRANT USAGE ON SCHEMA user_management TO anon;

-- Grant SELECT on existing tables to anon
GRANT SELECT ON ALL TABLES IN SCHEMA user_management TO anon;

-- Grant SELECT on existing views to anon
-- Grant SELECT on existing views to anon (GRANT ... ON ALL VIEWS is not supported
-- on all Postgres versions; use a DO block to grant per-view)
DO $$
DECLARE
	v record;
BEGIN
	FOR v IN
		SELECT table_schema, table_name
		FROM information_schema.views
		WHERE table_schema = 'user_management'
	LOOP
		EXECUTE format('GRANT SELECT ON %I.%I TO anon', v.table_schema, v.table_name);
	END LOOP;
END
$$;

-- Ensure future tables/views inherit the same privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA user_management
GRANT SELECT ON TABLES TO anon;

ALTER DEFAULT PRIVILEGES IN SCHEMA user_management
GRANT SELECT ON SEQUENCES TO anon;

COMMIT;

-- Optional: if your application needs INSERT/UPDATE/DELETE in dev, run the following (commented out):
-- GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA user_management TO anon;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA user_management GRANT INSERT, UPDATE, DELETE ON TABLES TO anon;
