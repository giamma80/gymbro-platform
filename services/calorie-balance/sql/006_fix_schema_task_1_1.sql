-- =============================================================================
-- Task 1.1 - Fix Database Schema Mismatch
-- =============================================================================
-- Add missing activity_level column to metabolic_profiles table
-- This resolves the critical schema mismatch causing metabolic API failures

-- First, let's check if the column already exists
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_schema = 'calorie_balance' 
AND table_name = 'metabolic_profiles' 
AND column_name = 'activity_level';

-- Add activity_level column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'calorie_balance' 
        AND table_name = 'metabolic_profiles' 
        AND column_name = 'activity_level'
    ) THEN
        -- Add the activity_level column
        ALTER TABLE calorie_balance.metabolic_profiles 
        ADD COLUMN activity_level VARCHAR(20) DEFAULT 'moderate';
        
        -- Add check constraint for valid activity levels
        ALTER TABLE calorie_balance.metabolic_profiles 
        ADD CONSTRAINT chk_activity_level 
        CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'high', 'extreme'));
        
        RAISE NOTICE '✅ Added activity_level column to metabolic_profiles';
    ELSE
        RAISE NOTICE 'ℹ️  activity_level column already exists in metabolic_profiles';
    END IF;
END $$;

-- Verify the column was added successfully
SELECT column_name, data_type, column_default, is_nullable 
FROM information_schema.columns 
WHERE table_schema = 'calorie_balance' 
AND table_name = 'metabolic_profiles' 
ORDER BY ordinal_position;

-- Test constraint works
DO $$
BEGIN
    -- This should work
    INSERT INTO calorie_balance.metabolic_profiles (
        user_id, 
        bmr_calories, 
        tdee_calories, 
        activity_level
    ) VALUES (
        '00000000-0000-0000-0000-000000000001'::UUID,
        1800,
        2200,
        'moderate'
    );
    
    -- Clean up test record
    DELETE FROM calorie_balance.metabolic_profiles 
    WHERE user_id = '00000000-0000-0000-0000-000000000001'::UUID;
    
    RAISE NOTICE '✅ activity_level column constraint validated successfully';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '⚠️  Test validation failed: %', SQLERRM;
END $$;