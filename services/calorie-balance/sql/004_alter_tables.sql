-- =============================================================================
-- Calorie Balance Service - Table Alterations
-- =============================================================================
-- Project: nutrifit-platform (shared database)
-- Service: calorie-balance  
-- Schema: calorie_balance
-- Phase: 1.1 - Schema Updates and Improvements
-- Date: 12 settembre 2025

-- =============================================================================
-- SCHEMA ALTERATIONS - Add missing columns for consistency
-- =============================================================================

-- Set search path to use our schema
SET search_path TO calorie_balance, public;

-- =============================================================================
-- 1. ADD MISSING UPDATED_AT COLUMNS
-- =============================================================================

-- Add updated_at column to calorie_events table for consistency with domain model
-- Events are typically immutable in event-driven systems, but having updated_at
-- provides consistency with other entities and allows for rare corrections
ALTER TABLE calorie_balance.calorie_events 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Create trigger to auto-update the updated_at timestamp
CREATE OR REPLACE FUNCTION calorie_balance.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to calorie_events table
DROP TRIGGER IF EXISTS update_calorie_events_updated_at ON calorie_balance.calorie_events;
CREATE TRIGGER update_calorie_events_updated_at
    BEFORE UPDATE ON calorie_balance.calorie_events
    FOR EACH ROW EXECUTE FUNCTION calorie_balance.update_updated_at_column();

-- =============================================================================
-- 2. BACKFILL EXISTING DATA
-- =============================================================================

-- Set updated_at to created_at for existing records (if any)
UPDATE calorie_balance.calorie_events 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Make updated_at NOT NULL now that all records have values
ALTER TABLE calorie_balance.calorie_events 
ALTER COLUMN updated_at SET NOT NULL;

-- =============================================================================
-- 3. VERIFICATION QUERIES
-- =============================================================================

-- Verify the column was added successfully
DO $$
DECLARE
    column_exists boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'calorie_balance' 
        AND table_name = 'calorie_events' 
        AND column_name = 'updated_at'
    ) INTO column_exists;
    
    IF column_exists THEN
        RAISE NOTICE '✅ updated_at column successfully added to calorie_events';
    ELSE
        RAISE EXCEPTION '❌ updated_at column was not added to calorie_events';
    END IF;
END $$;

-- Verify trigger was created successfully
DO $$
DECLARE
    trigger_exists boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.triggers 
        WHERE event_object_schema = 'calorie_balance' 
        AND event_object_table = 'calorie_events' 
        AND trigger_name = 'update_calorie_events_updated_at'
    ) INTO trigger_exists;
    
    IF trigger_exists THEN
        RAISE NOTICE '✅ Auto-update trigger successfully created for calorie_events';
    ELSE
        RAISE EXCEPTION '❌ Auto-update trigger was not created for calorie_events';
    END IF;
END $$;

-- =============================================================================
-- 4. PERFORMANCE CONSIDERATIONS
-- =============================================================================

-- Add index on updated_at for potential future queries (optional)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_calorie_events_updated_at 
--     ON calorie_balance.calorie_events(updated_at);

-- Note: Index creation is commented out by default since calorie_events
-- are typically append-only in event-driven systems. Uncomment if needed
-- for specific use cases requiring updated_at queries.

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '🚀 Schema alterations completed successfully!';
    RAISE NOTICE '📊 calorie_events table now has updated_at column';
    RAISE NOTICE '⚡ Auto-update trigger configured';
    RAISE NOTICE '✅ Domain model consistency maintained';
END $$;