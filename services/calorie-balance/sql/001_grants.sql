-- grants_template.sql
-- Template per concedere permessi di lettura/scrittura su qualsiasi schema di microservizio
-- Sostituire calorie_balance con il nome dello schema specifico
-- 
-- ⚠️  IMPORTANTE: Questo è un template per DDL SQL che deve essere eseguito 
--    nel portale Supabase SQL Editor, NON come script shell!
--
-- Utilizzo:
-- 1. Generare il file con: ./scripts/generate-grants-script.sh <service_name>
-- 2. Copiare il contenuto del file generato 
-- 3. Incollare nel SQL Editor di Supabase Dashboard
-- 4. Eseguire cliccando "Run"
--
-- Esempio:
-- ./scripts/generate-grants-script.sh user-management
-- Poi copiare services/user-management/sql/XXX_grants.sql nel portale Supabase

BEGIN;

-- Assicura che lo schema esista
CREATE SCHEMA IF NOT EXISTS calorie_balance;

-- Concede permessi di base a tutti i ruoli comuni (anon, authenticated, postgres, public)
-- In produzione, restringi solo ai ruoli necessari

-- USAGE sullo schema (permette l'accesso alle tabelle dello schema)
GRANT USAGE ON SCHEMA calorie_balance TO anon, authenticated, postgres, public;

-- SELECT su tutte le tabelle esistenti
GRANT SELECT ON ALL TABLES IN SCHEMA calorie_balance TO anon, authenticated, postgres, public;

-- SELECT su tutte le view esistenti (con DO block per compatibilità)
DO $$
DECLARE 
    v record;
BEGIN
    FOR v IN
        SELECT table_schema, table_name
        FROM information_schema.views
        WHERE table_schema = 'calorie_balance'
    LOOP
        EXECUTE format('GRANT SELECT ON %I.%I TO anon, authenticated, postgres, public', v.table_schema, v.table_name);
    END LOOP;
END
$$;

-- Permessi per le sequenze (necessari per INSERT con colonne auto-increment)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA calorie_balance TO anon, authenticated, postgres, public;

-- DEFAULT PRIVILEGES: assicura che le future tabelle/view/sequenze ereditino i permessi
ALTER DEFAULT PRIVILEGES IN SCHEMA calorie_balance
    GRANT SELECT ON TABLES TO anon, authenticated, postgres, public;

ALTER DEFAULT PRIVILEGES IN SCHEMA calorie_balance
    GRANT USAGE, SELECT ON SEQUENCES TO anon, authenticated, postgres, public;

-- OPZIONALE: Permessi di scrittura per sviluppo (commentati per default)
-- Decommentare se il microservizio ha bisogno di INSERT/UPDATE/DELETE in dev

-- GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA calorie_balance TO anon, authenticated;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA calorie_balance
--     GRANT INSERT, UPDATE, DELETE ON TABLES TO anon, authenticated;

COMMIT;

-- Post-esecuzione: verificare i permessi
-- SELECT grantee, privilege_type, table_schema, table_name 
-- FROM information_schema.table_privileges 
-- WHERE table_schema = 'calorie_balance' 
-- ORDER BY grantee, table_name;
