-- ============================================================================
-- 009_test_data_preparation.sql
-- 
-- Prepare comprehensive test data for calorie-balance service testing
-- User: 550e8400-e29b-41d4-a716-446655440000
-- Purpose: Create realistic data for GraphQL resolver testing
-- ============================================================================

-- Set search path to avoid schema prefixes
SET search_path TO calorie_balance, user_management, public;

-- ============================================================================
-- CREATE TEST USER IN USER_MANAGEMENT SCHEMA
-- ============================================================================
-- First, create the test user in user_management.users if it doesn't exist
INSERT INTO user_management.users (
    id, 
    email, 
    username,
    status,
    email_verified_at,
    created_at,
    updated_at,
    last_login_at
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    'testuser@gymbro.platform',
    'testuser_550e8400',  -- Use part of UUID to make unique
    'active',
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '60 days',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 hour'
) ON CONFLICT (id) DO UPDATE SET
    updated_at = NOW(),
    last_login_at = NOW() - INTERVAL '1 hour';

-- Create user profile in user_management.user_profiles
INSERT INTO user_management.user_profiles (
    id,
    user_id,
    first_name,
    last_name, 
    display_name,
    avatar_url,
    date_of_birth,
    gender,
    timezone,
    locale,
    preferences,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    'Test',
    'User',
    'Test User',
    NULL,
    '1993-06-15'::date,  -- Makes user 30+ years old
    'male',
    'Europe/Rome',
    'it-IT',
    '{"height_cm": 175, "weight_kg": 75.0, "activity_level": "moderate", "fitness_goals": ["weight_loss", "muscle_gain"]}',
    NOW() - INTERVAL '60 days',
    NOW() - INTERVAL '1 day'
) ON CONFLICT (user_id) DO UPDATE SET
    updated_at = NOW(),
    preferences = '{"height_cm": 175, "weight_kg": 75.0, "activity_level": "moderate", "fitness_goals": ["weight_loss", "muscle_gain"]}';

-- Create auth credentials for the test user
INSERT INTO user_management.auth_credentials (
    id,
    user_id,
    password_hash,
    salt,
    status,
    password_changed_at,
    failed_attempts,
    locked_until,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '$2a$12$rOOWNQ7HjRh0Qm3VyEQfmOGdE2LyGQvxvkwVfSJjSNV.kpO8tG8k.',  -- bcrypt hash for "Test123!"
    'test_salt_12345',
    'active',
    NOW() - INTERVAL '30 days',
    0,
    NULL,
    NOW() - INTERVAL '60 days',
    NOW() - INTERVAL '30 days'
) ON CONFLICT (user_id) DO UPDATE SET
    updated_at = NOW(),
    failed_attempts = 0,
    locked_until = NULL;

-- Create privacy settings for the test user
INSERT INTO user_management.privacy_settings (
    id,
    user_id,
    data_processing_consent,
    marketing_consent,
    analytics_consent,
    profile_visibility,
    health_data_sharing,
    preferences,
    consent_given_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    true,
    false,
    true,
    false,
    true,  -- Important for health/calorie data
    '{"data_retention_days": 365, "export_format": "json"}',
    NOW() - INTERVAL '60 days',
    NOW() - INTERVAL '1 day'
) ON CONFLICT (user_id) DO UPDATE SET
    updated_at = NOW(),
    health_data_sharing = true;

-- ============================================================================
-- CLEANUP EXISTING TEST DATA (if any)
-- ============================================================================
-- Using a real UUID for test user
DELETE FROM calorie_balance.daily_balances WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid;
DELETE FROM calorie_balance.calorie_events WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid;
DELETE FROM calorie_balance.calorie_goals WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid;
DELETE FROM calorie_balance.metabolic_profiles WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid;

-- ============================================================================
-- 1. CALORIE GOALS - Obiettivi calorici
-- ============================================================================

-- Goal attivo corrente (perdita peso)
INSERT INTO calorie_balance.calorie_goals (
    id, user_id, daily_calorie_target, goal_type, 
    is_active, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    2000,
    'weight_loss',
    true,
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '1 day'
);

-- Goal precedente (mantenimento)
INSERT INTO calorie_balance.calorie_goals (
    id, user_id, daily_calorie_target, goal_type, 
    is_active, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    2200,
    'maintain_weight',
    false,
    NOW() - INTERVAL '90 days',
    NOW() - INTERVAL '30 days'
);

-- ============================================================================
-- 2. METABOLIC PROFILE - Profilo metabolico
-- ============================================================================

INSERT INTO calorie_balance.metabolic_profiles (
    id, user_id, bmr_calories, tdee_calories, rmr_calories,
    calculation_method, accuracy_score,
    sedentary_multiplier, light_multiplier, moderate_multiplier, 
    high_multiplier, extreme_multiplier,
    activity_level,  -- Added missing column from 006_fix_schema_task_1_1.sql
    ai_adjusted, adjustment_factor, learning_iterations,
    calculated_at, expires_at, is_active
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    1650,  -- BMR
    2100,  -- TDEE (BMR * 1.27 - lightly active)
    1720,  -- RMR (slightly higher than BMR)
    'harris_benedict_revised',
    0.85,
    1.2,   -- sedentary
    1.375, -- light activity
    1.55,  -- moderate activity
    1.725, -- high activity
    1.9,   -- extreme activity
    'moderate',  -- activity_level value (valid: sedentary, light, moderate, high, extreme)
    true,
    1.05,  -- AI adjustment factor
    15,    -- learning iterations
    NOW() - INTERVAL '7 days',
    NOW() + INTERVAL '23 days', -- expires in 23 days
    true
);

-- ============================================================================
-- 3. CALORIE EVENTS - Eventi calorici realistici (ultimi 14 giorni)
-- ============================================================================

-- Oggi (2025-09-17)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 380, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: avocado toast e caffè", "items": ["avocado toast", "coffee"]}', '2025-09-17 08:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 520, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: insalata caesar con pollo", "items": ["caesar salad", "grilled chicken"]}', '2025-09-17 13:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 150, 'manual', 1.0, '{"meal": "snack", "description": "Snack: frutta mista", "items": ["mixed fruits"]}', '2025-09-17 16:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 620, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: salmone grigliato con verdure", "items": ["grilled salmon", "roasted vegetables"]}', '2025-09-17 19:45:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 320, 'fitness_tracker', 0.9, '{"activity": "running", "description": "Corsa 35 minuti nel parco", "duration": 35, "intensity": "moderate"}', '2025-09-17 07:00:00'::timestamp, NOW());

-- Ieri (2025-09-16)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 350, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: yogurt greco con muesli"}', '2025-09-16 08:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 480, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: pasta integrale al pesto"}', '2025-09-16 12:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 580, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: pollo al curry con riso basmati"}', '2025-09-16 20:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 280, 'fitness_tracker', 0.85, '{"activity": "weight_training", "description": "Palestra - allenamento pesi", "duration": 50}', '2025-09-16 18:00:00'::timestamp, NOW());

-- 2 giorni fa (2025-09-15)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 320, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: smoothie verde"}', '2025-09-15 08:45:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 450, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: wrap di tonno e verdure"}', '2025-09-15 13:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 100, 'manual', 1.0, '{"meal": "snack", "description": "Snack: mandorle"}', '2025-09-15 15:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 650, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: pizza margherita (weekend treat)"}', '2025-09-15 19:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 420, 'fitness_tracker', 0.9, '{"activity": "cycling", "description": "Ciclismo 60 minuti", "duration": 60}', '2025-09-15 10:00:00'::timestamp, NOW());

-- 3 giorni fa (2025-09-14)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 360, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: pancakes integrali"}', '2025-09-14 09:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 500, 'nutrition_scan', 0.88, '{"meal": "lunch", "description": "Pranzo: zuppa di lenticchie", "scan_type": "photo", "ingredients": ["lentils", "vegetables"]}', '2025-09-14 12:45:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 590, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: bistecca con patate arrosto"}', '2025-09-14 20:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 200, 'fitness_tracker', 0.8, '{"activity": "walking", "description": "Camminata veloce 40 minuti", "duration": 40}', '2025-09-14 18:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 0, 'smart_scale', 0.99, '{"description": "Misura peso mattutina", "weight_kg": 75.5, "body_fat_percent": 12.8, "hydration_percent": 58.2}', '2025-09-14 07:00:00'::timestamp, NOW());

-- 4 giorni fa (2025-09-13)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 340, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: porridge con banana"}', '2025-09-13 08:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 470, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: quinoa bowl con verdure"}', '2025-09-13 13:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 560, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: pesce spada alla griglia"}', '2025-09-13 19:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 350, 'fitness_tracker', 0.9, '{"activity": "swimming", "description": "Nuoto 45 minuti", "duration": 45}', '2025-09-13 17:00:00'::timestamp, NOW());

-- 5 giorni fa (2025-09-12)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 380, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: uova strapazzate con toast"}', '2025-09-12 08:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 490, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: risotto ai funghi porcini"}', '2025-09-12 12:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 120, 'manual', 1.0, '{"meal": "snack", "description": "Snack: yogurt con miele"}', '2025-09-12 16:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 580, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: pollo tandoori con naan"}', '2025-09-12 19:45:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 300, 'fitness_tracker', 0.8, '{"activity": "pilates", "description": "Pilates 50 minuti", "duration": 50}', '2025-09-12 18:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 150, 'healthkit', 0.95, '{"activity": "active_calories", "description": "Calorie bruciate passive (Apple Watch)", "duration": 1440, "source_device": "Apple Watch Series 9"}', '2025-09-12 23:59:00'::timestamp, NOW());

-- 6 giorni fa (2025-09-11)
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 330, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: cereali con latte di mandorla"}', '2025-09-11 08:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 460, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: burger vegetariano con patatine dolci"}', '2025-09-11 13:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 600, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: paella di mare"}', '2025-09-11 20:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 380, 'fitness_tracker', 0.9, '{"activity": "hiit", "description": "HIIT workout 30 minuti", "duration": 30}', '2025-09-11 07:30:00'::timestamp, NOW());

-- 7 giorni fa (2025-09-10) - una settimana fa
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 350, 'manual', 1.0, '{"meal": "breakfast", "description": "Colazione: toast francese"}', '2025-09-10 09:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 520, 'nutrition_scan', 0.95, '{"meal": "lunch", "description": "Pranzo: sushi misto", "scan_confidence": 0.95, "items": ["sashimi", "nigiri", "maki"]}', '2025-09-10 12:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 80, 'manual', 1.0, '{"meal": "snack", "description": "Snack: mela"}', '2025-09-10 15:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 540, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: lasagne vegetariane"}', '2025-09-10 19:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 250, 'fitness_tracker', 0.8, '{"activity": "yoga", "description": "Yoga flow 60 minuti", "duration": 60}', '2025-09-10 17:30:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 180, 'google_fit', 0.85, '{"activity": "walking", "description": "Camminata sincronizzata da Google Fit", "duration": 45, "steps": 4200}', '2025-09-10 20:00:00'::timestamp, NOW());

-- 8 giorni fa (2025-09-09) - Eventi aggiuntivi con source diversificati
INSERT INTO calorie_balance.calorie_events (id, user_id, event_type, value, source, confidence_score, metadata, event_timestamp, created_at) VALUES
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 320, 'nutrition_scan', 0.92, '{"meal": "breakfast", "description": "Colazione: smoothie proteico", "scan_type": "barcode", "protein_powder": "whey"}', '2025-09-09 08:15:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 450, 'manual', 1.0, '{"meal": "lunch", "description": "Pranzo: bowl poke"}', '2025-09-09 12:45:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 590, 'manual', 1.0, '{"meal": "dinner", "description": "Cena: hamburger artigianale"}', '2025-09-09 20:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'burned_exercise', 420, 'healthkit', 0.93, '{"activity": "running", "description": "Corsa sincronizzata da HealthKit", "duration": 42, "distance_km": 5.2, "avg_heart_rate": 155}', '2025-09-09 07:00:00'::timestamp, NOW()),
(gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000'::uuid, 'consumed', 0, 'smart_scale', 0.98, '{"description": "Peso corporeo registrato", "weight_kg": 75.1, "body_fat_percent": 12.5, "muscle_mass_kg": 63.2}', '2025-09-09 07:30:00'::timestamp, NOW());

-- ============================================================================
-- 4. DAILY BALANCES - Bilanci giornalieri calcolati
-- ============================================================================

-- Oggi (2025-09-17) - calorie parziali (giornata in corso)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-17'::date,
    1670,  -- 380+520+150+620
    320,
    2000,
    75.2,
    NOW(),
    NOW()
);

-- Ieri (2025-09-16)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-16'::date,
    1410,  -- 350+480+580
    280,
    2000,
    75.3,
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day'
);

-- 2 giorni fa (2025-09-15)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-15'::date,
    1520,  -- 320+450+100+650
    420,
    2000,
    75.4,
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days'
);

-- 3 giorni fa (2025-09-14)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-14'::date,
    1450,  -- 360+500+590
    200,
    2000,
    75.5,
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days'
);

-- 4 giorni fa (2025-09-13)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-13'::date,
    1370,  -- 340+470+560
    350,
    2000,
    75.6,
    NOW() - INTERVAL '4 days',
    NOW() - INTERVAL '4 days'
);

-- 5 giorni fa (2025-09-12)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-12'::date,
    1570,  -- 380+490+120+580
    450,   -- 300 (pilates) + 150 (healthkit active calories)
    2000,
    75.7,
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days'
);

-- 6 giorni fa (2025-09-11)
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-11'::date,
    1390,  -- 330+460+600
    380,
    2000,
    75.8,
    NOW() - INTERVAL '6 days',
    NOW() - INTERVAL '6 days'
);

-- 7 giorni fa (2025-09-10) - una settimana fa
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-10'::date,
    1490,  -- 350+520+80+540
    430,   -- 250+180 (yoga + google fit walking)
    2000,
    75.9,
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '7 days'
);

-- 8 giorni fa (2025-09-09) - Con dati multi-source
INSERT INTO calorie_balance.daily_balances (
    id, user_id, date, calories_consumed, calories_burned_exercise,
    daily_calorie_target, morning_weight_kg, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    '2025-09-09'::date,
    1360,  -- 320+450+590 (smart scale event has 0 calories)
    420,   -- healthkit running
    2000,
    75.1,  -- weight from smart scale
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '8 days'
);

-- ============================================================================
-- SUMMARY & VERIFICATION
-- ============================================================================

-- Display summary of inserted data
SELECT 
    'CALORIE GOALS' as table_name, 
    COUNT(*) as records,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM calorie_balance.calorie_goals 
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid

UNION ALL

SELECT 
    'METABOLIC PROFILES' as table_name, 
    COUNT(*) as records,
    MIN(calculated_at) as earliest,
    MAX(calculated_at) as latest
FROM calorie_balance.metabolic_profiles 
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid

UNION ALL

SELECT 
    'CALORIE EVENTS' as table_name, 
    COUNT(*) as records,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM calorie_balance.calorie_events 
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid

UNION ALL

SELECT 
    'DAILY BALANCES' as table_name, 
    COUNT(*) as records,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM calorie_balance.daily_balances 
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'::uuid

ORDER BY table_name;

-- ============================================================================
-- DATA PREPARATION COMPLETE ✅
-- 
-- Test user: 550e8400-e29b-41d4-a716-446655440000
-- Data span: Last 9 days (2025-09-09 to 2025-09-17)
-- 
-- 📊 Data Sources Diversified:
-- ✅ manual - Inserimenti manuali utente (maggioranza)
-- ✅ fitness_tracker - Dati da app fitness/wearables 
-- ✅ nutrition_scan - Scansione barcode/foto cibo
-- ✅ smart_scale - Dati da bilancia intelligente 
-- ✅ healthkit - Dati sincronizzati da HealthKit/Apple
-- ✅ google_fit - Dati sincronizzati da Google Fit
--
-- Ready for GraphQL resolver testing:
-- ✅ getBehavioralPatterns (now with diverse data sources!)
-- ✅ getCurrentCalorieGoal  
-- ✅ getUserDailyBalances
-- ✅ getUserMetabolicProfile
-- ✅ getWeeklyAnalytics
-- ✅ getHourlyAnalytics
-- ✅ updateCalorieGoal
-- ✅ createCalorieEvent
-- ✅ And many more...
-- ============================================================================