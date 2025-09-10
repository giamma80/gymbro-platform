-- Query per verificare i permessi attuali nello schema user_management
-- Eseguire nel Supabase SQL Editor PRIMA di applicare 004_grants.sql

-- 1. Verifica che lo schema esista
SELECT 
    schema_name,
    schema_owner
FROM information_schema.schemata 
WHERE schema_name = 'user_management';

-- 2. Lista delle tabelle nello schema
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'user_management'
ORDER BY table_name;

-- 3. Permessi attuali per tabelle
SELECT 
    grantee,
    privilege_type,
    table_name,
    is_grantable
FROM information_schema.table_privileges 
WHERE table_schema = 'user_management' 
ORDER BY table_name, grantee, privilege_type;

-- 4. Permessi attuali per sequenze (se esistono)
SELECT 
    grantee,
    privilege_type,
    object_name,
    object_type
FROM information_schema.usage_privileges 
WHERE object_schema = 'user_management'
ORDER BY object_name, grantee;

-- 5. Riepilogo permessi per ruolo (più leggibile)
SELECT 
    grantee as ruolo,
    string_agg(DISTINCT privilege_type, ', ' ORDER BY privilege_type) as permessi,
    count(DISTINCT table_name) as numero_tabelle
FROM information_schema.table_privileges 
WHERE table_schema = 'user_management' 
GROUP BY grantee
ORDER BY ruolo;
