-- ==========================================
-- 🍎 HealthKit Enhancement Migration
-- ==========================================
-- Data: 1 Settembre 2025
-- Versione: v1.4.0-healthkit-enhanced
-- Descrizione: Aggiunge campi HealthKit per analytics avanzati

-- ==========================================
-- 📊 DAILY_FITNESS_DATA TABLE ENHANCEMENTS
-- ==========================================

-- Add new activity metrics
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS floors_climbed INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS distance_km FLOAT DEFAULT 0.0 NOT NULL;

-- Enhanced calorie tracking (HealthKit compatible)
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS calories_active FLOAT DEFAULT 0.0 NOT NULL;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS calories_basal FLOAT DEFAULT 0.0 NOT NULL;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS calories_total FLOAT DEFAULT 0.0 NOT NULL;

-- Body composition & health metrics
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS body_mass_index FLOAT;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS body_fat_percentage FLOAT;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS muscle_mass_kg FLOAT;

-- Cardiovascular health
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS resting_heart_rate INTEGER;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS heart_rate_variability FLOAT;

-- Sleep quality analysis
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS sleep_hours_total FLOAT;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS sleep_hours_in_bed FLOAT;
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS sleep_efficiency FLOAT;

-- Subjective metrics
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS stress_level INTEGER;

-- Data source & metadata
ALTER TABLE daily_fitness_data ADD COLUMN IF NOT EXISTS data_source VARCHAR(100) DEFAULT 'manual' NOT NULL;

-- Update legacy data to use new calorie structure
UPDATE daily_fitness_data 
SET calories_active = calories_burned 
WHERE calories_active = 0 AND calories_burned > 0;

UPDATE daily_fitness_data 
SET sleep_hours_total = sleep_hours 
WHERE sleep_hours_total IS NULL AND sleep_hours IS NOT NULL;

-- ==========================================
-- 🏃‍♂️ USER_ACTIVITIES TABLE ENHANCEMENTS
-- ==========================================

-- Enhanced cardiovascular metrics
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS min_heart_rate INTEGER;

-- Environmental context
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS weather_temperature FLOAT;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS weather_humidity FLOAT;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS location_name VARCHAR(200);

-- Elevation data
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS elevation_gain_m FLOAT;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS elevation_loss_m FLOAT;

-- Heart rate zones (time in seconds)
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS hr_zone_1_seconds INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS hr_zone_2_seconds INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS hr_zone_3_seconds INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS hr_zone_4_seconds INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS hr_zone_5_seconds INTEGER DEFAULT 0 NOT NULL;

-- Data source & metadata
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS data_source VARCHAR(100) DEFAULT 'manual' NOT NULL;
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS source_bundle VARCHAR(255);
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS device_type VARCHAR(100);
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS healthkit_uuid VARCHAR(255) UNIQUE;

-- User feedback
ALTER TABLE user_activities ADD COLUMN IF NOT EXISTS perceived_exertion INTEGER;

-- ==========================================
-- 🗂️ CREATE NEW INDEXES
-- ==========================================

-- DailyFitnessData indexes
CREATE INDEX IF NOT EXISTS idx_daily_fitness_data_source ON daily_fitness_data(data_source);

-- UserActivity indexes  
CREATE INDEX IF NOT EXISTS idx_user_activities_type ON user_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_user_activities_source ON user_activities(data_source);
CREATE INDEX IF NOT EXISTS idx_user_activities_date_range ON user_activities(started_at);
CREATE INDEX IF NOT EXISTS idx_user_activities_healthkit ON user_activities(healthkit_uuid);

-- ==========================================
-- 🔒 ADD FOREIGN KEY CONSTRAINTS
-- ==========================================

-- Add foreign key constraints if they don't exist
DO $$ 
BEGIN
    -- DailyFitnessData foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_daily_fitness_data_user_id'
    ) THEN
        ALTER TABLE daily_fitness_data 
        ADD CONSTRAINT fk_daily_fitness_data_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;

    -- UserActivity foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_user_activities_user_id'
    ) THEN
        ALTER TABLE user_activities 
        ADD CONSTRAINT fk_user_activities_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ==========================================
-- 📊 CREATE COMPUTED COLUMNS FUNCTIONS
-- ==========================================

-- Function to calculate Total Daily Energy Expenditure
CREATE OR REPLACE FUNCTION update_calories_total()
RETURNS TRIGGER AS $$
BEGIN
    NEW.calories_total = COALESCE(NEW.calories_active, 0) + COALESCE(NEW.calories_basal, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update calories_total
DROP TRIGGER IF EXISTS trigger_update_calories_total ON daily_fitness_data;
CREATE TRIGGER trigger_update_calories_total
    BEFORE INSERT OR UPDATE ON daily_fitness_data
    FOR EACH ROW
    EXECUTE FUNCTION update_calories_total();

-- Function to calculate sleep efficiency
CREATE OR REPLACE FUNCTION update_sleep_efficiency()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sleep_hours_in_bed IS NOT NULL AND NEW.sleep_hours_in_bed > 0 THEN
        NEW.sleep_efficiency = (COALESCE(NEW.sleep_hours_total, 0) / NEW.sleep_hours_in_bed) * 100;
    ELSE
        NEW.sleep_efficiency = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update sleep efficiency
DROP TRIGGER IF EXISTS trigger_update_sleep_efficiency ON daily_fitness_data;
CREATE TRIGGER trigger_update_sleep_efficiency
    BEFORE INSERT OR UPDATE ON daily_fitness_data
    FOR EACH ROW
    EXECUTE FUNCTION update_sleep_efficiency();

-- ==========================================
-- ✅ VALIDATE MIGRATION SUCCESS
-- ==========================================

-- Verify new columns exist
DO $$
DECLARE
    column_count INTEGER;
BEGIN
    -- Check DailyFitnessData enhancements
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_name = 'daily_fitness_data'
    AND column_name IN (
        'floors_climbed', 'distance_km', 'calories_active', 'calories_basal',
        'calories_total', 'body_mass_index', 'body_fat_percentage', 'muscle_mass_kg',
        'resting_heart_rate', 'heart_rate_variability', 'sleep_hours_total',
        'sleep_hours_in_bed', 'sleep_efficiency', 'stress_level', 'data_source'
    );
    
    IF column_count < 15 THEN
        RAISE EXCEPTION 'Migration failed: Missing columns in daily_fitness_data. Expected 15, found %', column_count;
    END IF;
    
    -- Check UserActivity enhancements
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_name = 'user_activities'
    AND column_name IN (
        'min_heart_rate', 'weather_temperature', 'weather_humidity', 'location_name',
        'elevation_gain_m', 'elevation_loss_m', 'hr_zone_1_seconds', 'hr_zone_2_seconds',
        'hr_zone_3_seconds', 'hr_zone_4_seconds', 'hr_zone_5_seconds', 'data_source',
        'source_bundle', 'device_type', 'healthkit_uuid', 'perceived_exertion'
    );
    
    IF column_count < 16 THEN
        RAISE EXCEPTION 'Migration failed: Missing columns in user_activities. Expected 16, found %', column_count;
    END IF;
    
    RAISE NOTICE '✅ Migration completed successfully! Enhanced database models for HealthKit integration.';
    RAISE NOTICE '📊 Added % new columns to daily_fitness_data', 15;
    RAISE NOTICE '🏃‍♂️ Added % new columns to user_activities', 16;
END $$;

-- ==========================================
-- 📈 MIGRATION SUMMARY
-- ==========================================

/*
🎯 MIGRATION SUMMARY
===================

✅ Enhanced DailyFitnessData with 15 new fields:
   - Activity: floors_climbed, distance_km
   - Calories: calories_active, calories_basal, calories_total
   - Body: body_mass_index, body_fat_percentage, muscle_mass_kg
   - Heart: resting_heart_rate, heart_rate_variability
   - Sleep: sleep_hours_total, sleep_hours_in_bed, sleep_efficiency
   - Subjective: stress_level
   - Meta: data_source

✅ Enhanced UserActivity with 16 new fields:
   - Heart Rate: min_heart_rate
   - Environment: weather_temperature, weather_humidity, location_name
   - Elevation: elevation_gain_m, elevation_loss_m
   - HR Zones: hr_zone_1_seconds through hr_zone_5_seconds (5 fields)
   - Meta: data_source, source_bundle, device_type, healthkit_uuid
   - Feedback: perceived_exertion

✅ Added database constraints and indexes for performance
✅ Added computed columns with triggers for automatic calculations
✅ Maintained backward compatibility with legacy fields

🚀 Next Steps:
   - Update services.py to use new enhanced models
   - Implement HealthKit data mapping functions
   - Create HealthKit sync endpoint
   - Test enhanced analytics capabilities
*/
