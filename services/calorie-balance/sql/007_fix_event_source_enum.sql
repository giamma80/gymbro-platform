-- ==========================================
-- Script: 007_fix_event_source_enum.sql
-- Descrizione: Allinea enum event_source con il codice Python 
-- Task: 2.3 Fix Events API Validation
-- Versione: 1.0
-- Data: $(date +%Y-%m-%d)
-- ==========================================

-- PROBLEMA IDENTIFICATO:
-- Triple incongruenza tra documentazione, database e codice Python per enum event_source
-- 
-- DOCUMENTAZIONE: ('app', 'smartwatch', 'manual', 'api', 'sync')  
-- DATABASE SQL:   ('healthkit', 'google_fit', 'manual', 'app_tracking', 'ai_estimation')
-- CODICE PYTHON:  ('manual', 'fitness_tracker', 'smart_scale', 'nutrition_scan', 'healthkit', 'google_fit')
--
-- CAUSA: Il codice Python usa valori non presenti nel database, causando errori 500:
-- "invalid input value for enum event_source: 'fitness_tracker'"

-- ==========================================
-- STEP 1: Backup dei dati esistenti per rollback
-- ==========================================

-- Verifica contenuti attuali prima della modifica
SELECT DISTINCT source, COUNT(*) as count 
FROM calorie_balance.calorie_events 
GROUP BY source
ORDER BY source;

-- ==========================================  
-- STEP 2: Aggiungi i nuovi valori enum mancanti
-- ==========================================

-- Il codice Python usa questi 6 valori:
-- 'manual', 'fitness_tracker', 'smart_scale', 'nutrition_scan', 'healthkit', 'google_fit'

-- Aggiungi i valori mancanti uno per uno (PostgreSQL richiede ALTER separati)
-- IMPORTANTE: I nuovi valori devono essere committati prima di poterli usare
ALTER TYPE calorie_balance.event_source ADD VALUE IF NOT EXISTS 'fitness_tracker';
COMMIT;

ALTER TYPE calorie_balance.event_source ADD VALUE IF NOT EXISTS 'smart_scale';  
COMMIT;

ALTER TYPE calorie_balance.event_source ADD VALUE IF NOT EXISTS 'nutrition_scan';
COMMIT;

-- ==========================================
-- STEP 3: Migra i dati esistenti ai nuovi valori  
-- ==========================================

-- NOTA IMPORTANTE: I valori enum appena aggiunti sono ora disponibili
-- perché sono stati committati nelle transazioni precedenti.

-- Mappa i valori obsoleti ai nuovi seguendo la logica di business:
-- 'app_tracking' -> 'manual' (inserimento manuale via app)
-- 'ai_estimation' -> 'nutrition_scan' (stima AI/scansione)

BEGIN;

-- Backup temporaneo per rollback
CREATE TEMP TABLE event_source_backup AS 
SELECT id, source, created_at 
FROM calorie_balance.calorie_events;

-- Migrazione dati con mapping logico
UPDATE calorie_balance.calorie_events 
SET source = 'manual'
WHERE source = 'app_tracking';

UPDATE calorie_balance.calorie_events 
SET source = 'nutrition_scan' 
WHERE source = 'ai_estimation';

-- Verifica migrazione
SELECT 'DOPO MIGRAZIONE:' as status;
SELECT DISTINCT source, COUNT(*) as count 
FROM calorie_balance.calorie_events 
GROUP BY source
ORDER BY source;

COMMIT;

-- ==========================================
-- STEP 4: Rimuovi valori enum obsoleti (OPZIONALE)
-- ==========================================

-- NOTA: PostgreSQL non supporta DROP VALUE per enum types
-- I valori obsoleti rimangono disponibili ma non usati:
-- - 'app_tracking' (migrato a 'manual')  
-- - 'ai_estimation' (migrato a 'nutrition_scan')
-- 
-- Per rimuoverli completamente sarebbe necessario:
-- 1. DROP TYPE e CREATE TYPE (ma rompe dipendenze)
-- 2. O mantenere valori legacy per compatibilità

-- ==========================================
-- STEP 5: Validazione finale 
-- ==========================================

-- Verifica che tutti i valori del codice Python siano supportati
DO $$
DECLARE
    python_values text[] := ARRAY['manual', 'fitness_tracker', 'smart_scale', 'nutrition_scan', 'healthkit', 'google_fit'];
    val text;
    enum_exists boolean;
BEGIN
    FOREACH val IN ARRAY python_values LOOP
        SELECT EXISTS(
            SELECT 1 FROM pg_enum e 
            JOIN pg_type t ON e.enumtypid = t.oid 
            WHERE t.typname = 'event_source' 
            AND e.enumlabel = val
        ) INTO enum_exists;
        
        IF NOT enum_exists THEN
            RAISE EXCEPTION 'Valore enum mancante: %', val;
        ELSE
            RAISE NOTICE 'Valore enum presente: %', val;
        END IF;
    END LOOP;
    
    RAISE NOTICE '✅ Tutti i valori del codice Python sono supportati nel database!';
END $$;

-- ==========================================
-- STEP 6: Documentazione dello stato finale
-- ==========================================

-- Visualizza tutti i valori enum disponibili
SELECT 'VALORI ENUM FINALI:' as info;
SELECT e.enumlabel as event_source_value, e.enumsortorder as order_num
FROM pg_enum e
JOIN pg_type t ON e.enumtypid = t.oid  
WHERE t.typname = 'event_source'
ORDER BY e.enumsortorder;

-- Statistiche finali sui dati
SELECT 'DISTRIBUZIONE DATI FINALI:' as info;
SELECT source, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM calorie_balance.calorie_events), 2) as percentage
FROM calorie_balance.calorie_events
GROUP BY source  
ORDER BY count DESC;

-- ==========================================
-- ROLLBACK PROCEDURE (se necessario)
-- ==========================================

/*
-- In caso di problemi, eseguire questo rollback:

BEGIN;

-- Ripristina da backup temporaneo (disponibile solo nella stessa sessione)
UPDATE calorie_balance.calorie_events c
SET source = b.source
FROM event_source_backup b  
WHERE c.id = b.id
AND c.source != b.source;

-- Verifica rollback
SELECT 'DOPO ROLLBACK:' as status;
SELECT DISTINCT source, COUNT(*) as count 
FROM calorie_balance.calorie_events 
GROUP BY source;

COMMIT;
*/

-- ==========================================
-- NOTES PER DEVELOPER  
-- ==========================================

/*
AZIONE RICHIESTA DOPO QUESTO SCRIPT:

1. ✅ Eseguire questo script SQL manualmente su dashboard Supabase
2. 🧪 Testare gli endpoint API /burned e /weight per verificare risoluzione errori 500  
3. 📝 Aggiornare documentazione in docs/databases/calorie-balance-db.md con i nuovi valori
4. 🔄 Eventualmente allineare altri microservizi se usano event_source

VALORI ENUM FINALI SUPPORTATI:
- 'manual' (inserimento manuale utente) 
- 'fitness_tracker' (dispositivi fitness generici)
- 'smart_scale' (bilance smart per peso) 
- 'nutrition_scan' (scansione AI alimenti)
- 'healthkit' (Apple HealthKit sync)
- 'google_fit' (Google Fit sync) 
- 'app_tracking' (legacy, migrato a manual)
- 'ai_estimation' (legacy, migrato a nutrition_scan)

PATTERN ARCHITETTURALE:
Allineato con DataSource pattern da docs/microservizi_python.md
*/