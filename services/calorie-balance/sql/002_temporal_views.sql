-- =============================================================================
-- Calorie Balance Service - Temporal Views Creation
-- =============================================================================
-- Project: nutrifit-platform
-- Service: calorie-balance  
-- Schema: calorie_balance
-- Phase: 1.1 - 5-Level Temporal Analytics Views
-- Date: 11 settembre 2025
-- Purpose: Create high-performance aggregation views for mobile analytics

-- =============================================================================
-- 5-LEVEL TEMPORAL ANALYTICS SYSTEM
-- =============================================================================

-- Set search path to use our schema
SET search_path TO calorie_balance, public;

-- =============================================================================
-- LEVEL 1: HOURLY CALORIE SUMMARY (Real-time intraday trends)
-- =============================================================================

CREATE OR REPLACE VIEW calorie_balance.hourly_calorie_summary AS
WITH hourly_aggregates AS (
    SELECT 
        user_id,
        DATE(event_timestamp) as date,
        EXTRACT(HOUR FROM event_timestamp) as hour,
        event_type,
        SUM(value) as total_value,
        COUNT(*) as event_count,
        AVG(confidence_score) as avg_confidence,
        COUNT(DISTINCT source) as source_variety,
        MIN(event_timestamp) as first_event,
        MAX(event_timestamp) as last_event
    FROM calorie_balance.calorie_events
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY user_id, DATE(event_timestamp), EXTRACT(HOUR FROM event_timestamp), event_type
),
hourly_weights AS (
    SELECT DISTINCT
        user_id,
        DATE(event_timestamp) as date,
        EXTRACT(HOUR FROM event_timestamp) as hour,
        LAST_VALUE(value) OVER (
            PARTITION BY user_id, DATE(event_timestamp), EXTRACT(HOUR FROM event_timestamp) 
            ORDER BY event_timestamp 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as weight_kg
    FROM calorie_balance.calorie_events
    WHERE event_type = 'weight' 
    AND event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
)
SELECT 
    ha.user_id,
    ha.date,
    ha.hour,
    
    -- Calorie aggregations
    COALESCE(SUM(CASE WHEN ha.event_type = 'consumed' THEN ha.total_value END), 0) as calories_consumed,
    COALESCE(SUM(CASE WHEN ha.event_type = 'burned_exercise' THEN ha.total_value END), 0) as calories_burned_exercise,
    COALESCE(SUM(CASE WHEN ha.event_type = 'burned_bmr' THEN ha.total_value END), 0) as calories_burned_bmr,
    
    -- Net calculations
    COALESCE(SUM(CASE WHEN ha.event_type = 'consumed' THEN ha.total_value END), 0) - 
    COALESCE(SUM(CASE WHEN ha.event_type IN ('burned_exercise', 'burned_bmr') THEN ha.total_value END), 0) as net_calories,
    
    -- Weight tracking
    hw.weight_kg,
    
    -- Event metadata
    SUM(ha.event_count) as event_count,
    MIN(ha.first_event) as first_event,
    MAX(ha.last_event) as last_event,
    
    -- Data quality metrics
    AVG(ha.avg_confidence) as avg_confidence,
    SUM(ha.source_variety) as source_variety

FROM hourly_aggregates ha
LEFT JOIN hourly_weights hw ON ha.user_id = hw.user_id AND ha.date = hw.date AND ha.hour = hw.hour
GROUP BY ha.user_id, ha.date, ha.hour, hw.weight_kg
ORDER BY ha.user_id, ha.date DESC, ha.hour DESC;

-- =============================================================================
-- LEVEL 2: DAILY CALORIE SUMMARY (Day-over-day comparisons)
-- =============================================================================

CREATE OR REPLACE VIEW calorie_balance.daily_calorie_summary AS
WITH daily_aggregates AS (
    SELECT 
        user_id,
        DATE(event_timestamp) as date,
        event_type,
        SUM(value) as total_value,
        COUNT(*) as event_count,
        AVG(confidence_score) as avg_confidence,
        COUNT(DISTINCT source) as source_variety,
        COUNT(DISTINCT EXTRACT(HOUR FROM event_timestamp)) as active_hours,
        MIN(event_timestamp) as first_event,
        MAX(event_timestamp) as last_event
    FROM calorie_balance.calorie_events
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id, DATE(event_timestamp), event_type
),
daily_weights AS (
    SELECT DISTINCT
        user_id,
        DATE(event_timestamp) as date,
        -- Morning weight (first weight between 5-10 AM)
        FIRST_VALUE(
            CASE WHEN EXTRACT(HOUR FROM event_timestamp) BETWEEN 5 AND 10 
                 THEN value ELSE NULL END
        ) OVER (
            PARTITION BY user_id, DATE(event_timestamp) 
            ORDER BY event_timestamp ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as morning_weight_kg,
        -- Evening weight (last weight between 6-11 PM)
        LAST_VALUE(
            CASE WHEN EXTRACT(HOUR FROM event_timestamp) BETWEEN 18 AND 23 
                 THEN value ELSE NULL END
        ) OVER (
            PARTITION BY user_id, DATE(event_timestamp) 
            ORDER BY event_timestamp ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as evening_weight_kg
    FROM calorie_balance.calorie_events
    WHERE event_type = 'weight' 
    AND event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
),
daily_goals AS (
    SELECT DISTINCT
        user_id,
        date,
        daily_calorie_target
    FROM (
        SELECT 
            cg.user_id,
            d.date,
            cg.daily_calorie_target,
            ROW_NUMBER() OVER (PARTITION BY cg.user_id, d.date ORDER BY cg.start_date DESC) as rn
        FROM calorie_balance.calorie_goals cg
        CROSS JOIN (
            SELECT DISTINCT DATE(event_timestamp) as date
            FROM calorie_balance.calorie_events
            WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
        ) d
        WHERE cg.is_active = true
        AND d.date BETWEEN cg.start_date AND COALESCE(cg.end_date, CURRENT_DATE)
    ) ranked_goals
    WHERE rn = 1
)
SELECT 
    da.user_id,
    da.date,
    
    -- Calorie aggregations
    COALESCE(SUM(CASE WHEN da.event_type = 'consumed' THEN da.total_value END), 0) as calories_consumed,
    COALESCE(SUM(CASE WHEN da.event_type = 'burned_exercise' THEN da.total_value END), 0) as calories_burned_exercise,
    COALESCE(SUM(CASE WHEN da.event_type = 'burned_bmr' THEN da.total_value END), 0) as calories_burned_bmr,
    
    -- Net calculations
    COALESCE(SUM(CASE WHEN da.event_type = 'consumed' THEN da.total_value END), 0) - 
    COALESCE(SUM(CASE WHEN da.event_type IN ('burned_exercise', 'burned_bmr') THEN da.total_value END), 0) as net_calories,
    
    -- Weight tracking
    dw.morning_weight_kg,
    dw.evening_weight_kg,
    
    -- Event metadata
    SUM(da.event_count) as event_count,
    MIN(da.first_event) as first_event,
    MAX(da.last_event) as last_event,
    
    -- Data quality and completeness
    AVG(da.avg_confidence) as avg_confidence,
    SUM(da.source_variety) as source_variety,
    MAX(da.active_hours) as active_hours,
    
    -- Goal comparison
    dg.daily_calorie_target

FROM daily_aggregates da
LEFT JOIN daily_weights dw ON da.user_id = dw.user_id AND da.date = dw.date
LEFT JOIN daily_goals dg ON da.user_id = dg.user_id AND da.date = dg.date
GROUP BY da.user_id, da.date, dw.morning_weight_kg, dw.evening_weight_kg, dg.daily_calorie_target
ORDER BY da.user_id, da.date DESC;

-- =============================================================================
-- LEVEL 3: WEEKLY CALORIE SUMMARY (Weekly patterns, habit formation)
-- =============================================================================

CREATE OR REPLACE VIEW calorie_balance.weekly_calorie_summary AS
WITH weekly_aggregates AS (
    SELECT 
        user_id,
        DATE_TRUNC('week', event_timestamp)::DATE as week_start,
        DATE_TRUNC('week', event_timestamp)::DATE + INTERVAL '6 days' as week_end,
        EXTRACT(YEAR FROM event_timestamp) as year,
        EXTRACT(WEEK FROM event_timestamp) as week_number,
        event_type,
        SUM(value) as total_value,
        COUNT(*) as total_events,
        COUNT(DISTINCT DATE(event_timestamp)) as active_days,
        AVG(confidence_score) as avg_confidence,
        COUNT(DISTINCT source) as source_variety,
        MIN(event_timestamp) as first_event,
        MAX(event_timestamp) as last_event
    FROM calorie_balance.calorie_events
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY user_id, DATE_TRUNC('week', event_timestamp), EXTRACT(YEAR FROM event_timestamp), EXTRACT(WEEK FROM event_timestamp), event_type
),
weekly_weights AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('week', event_timestamp)::DATE as week_start,
        FIRST_VALUE(value) OVER (
            PARTITION BY user_id, DATE_TRUNC('week', event_timestamp)
            ORDER BY event_timestamp ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as week_start_weight,
        LAST_VALUE(value) OVER (
            PARTITION BY user_id, DATE_TRUNC('week', event_timestamp)
            ORDER BY event_timestamp ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as week_end_weight
    FROM calorie_balance.calorie_events
    WHERE event_type = 'weight'
    AND event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT 
    wa.user_id,
    wa.week_start,
    wa.week_end,
    wa.year,
    wa.week_number,
    
    -- Weekly calorie aggregations
    COALESCE(SUM(CASE WHEN wa.event_type = 'consumed' THEN wa.total_value END), 0) as weekly_calories_consumed,
    COALESCE(SUM(CASE WHEN wa.event_type = 'burned_exercise' THEN wa.total_value END), 0) as weekly_calories_burned_exercise,
    COALESCE(SUM(CASE WHEN wa.event_type = 'burned_bmr' THEN wa.total_value END), 0) as weekly_calories_burned_bmr,
    
    -- Weekly net calculations
    COALESCE(SUM(CASE WHEN wa.event_type = 'consumed' THEN wa.total_value END), 0) - 
    COALESCE(SUM(CASE WHEN wa.event_type IN ('burned_exercise', 'burned_bmr') THEN wa.total_value END), 0) as weekly_net_calories,
    
    -- Daily averages for the week
    COALESCE(SUM(CASE WHEN wa.event_type = 'consumed' THEN wa.total_value END), 0) / 
    GREATEST(MAX(wa.active_days), 1) as avg_daily_consumed,
    
    COALESCE(SUM(CASE WHEN wa.event_type IN ('burned_exercise', 'burned_bmr') THEN wa.total_value END), 0) / 
    GREATEST(MAX(wa.active_days), 1) as avg_daily_burned,
    
    -- Weight change tracking
    ww.week_start_weight,
    ww.week_end_weight,
    
    -- Activity and engagement metrics
    MAX(wa.active_days) as active_days,
    SUM(wa.total_events) as total_events,
    AVG(wa.avg_confidence) as avg_confidence,
    SUM(wa.source_variety) as source_variety,
    
    -- Time range
    MIN(wa.first_event) as first_event,
    MAX(wa.last_event) as last_event

FROM weekly_aggregates wa
LEFT JOIN weekly_weights ww ON wa.user_id = ww.user_id AND wa.week_start = ww.week_start
GROUP BY wa.user_id, wa.week_start, wa.week_end, wa.year, wa.week_number, ww.week_start_weight, ww.week_end_weight
ORDER BY wa.user_id, wa.week_start DESC;

-- =============================================================================
-- LEVEL 4: MONTHLY CALORIE SUMMARY (Long-term trends, monthly reports)
-- =============================================================================

CREATE OR REPLACE VIEW calorie_balance.monthly_calorie_summary AS
WITH monthly_aggregates AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', event_timestamp)::DATE as month_start,
        (DATE_TRUNC('month', event_timestamp) + INTERVAL '1 month - 1 day')::DATE as month_end,
        EXTRACT(YEAR FROM event_timestamp) as year,
        EXTRACT(MONTH FROM event_timestamp) as month,
        TO_CHAR(event_timestamp, 'YYYY-MM') as month_label,
        event_type,
        SUM(value) as total_value,
        COUNT(*) as total_events,
        COUNT(DISTINCT DATE(event_timestamp)) as active_days,
        COUNT(DISTINCT DATE_TRUNC('week', event_timestamp)) as active_weeks,
        AVG(confidence_score) as avg_confidence,
        COUNT(DISTINCT source) as source_variety,
        MIN(event_timestamp) as first_event,
        MAX(event_timestamp) as last_event
    FROM calorie_balance.calorie_events
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY user_id, DATE_TRUNC('month', event_timestamp), EXTRACT(YEAR FROM event_timestamp), EXTRACT(MONTH FROM event_timestamp), TO_CHAR(event_timestamp, 'YYYY-MM'), event_type
),
monthly_weights AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', event_timestamp)::DATE as month_start,
        FIRST_VALUE(value) OVER (
            PARTITION BY user_id, DATE_TRUNC('month', event_timestamp)
            ORDER BY event_timestamp ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as month_start_weight,
        LAST_VALUE(value) OVER (
            PARTITION BY user_id, DATE_TRUNC('month', event_timestamp)
            ORDER BY event_timestamp ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as month_end_weight
    FROM calorie_balance.calorie_events
    WHERE event_type = 'weight'
    AND event_timestamp >= CURRENT_DATE - INTERVAL '12 months'
)
SELECT 
    ma.user_id,
    ma.month_start,
    ma.month_end,
    ma.year,
    ma.month,
    ma.month_label,
    
    -- Monthly calorie aggregations
    COALESCE(SUM(CASE WHEN ma.event_type = 'consumed' THEN ma.total_value END), 0) as monthly_calories_consumed,
    COALESCE(SUM(CASE WHEN ma.event_type = 'burned_exercise' THEN ma.total_value END), 0) as monthly_calories_burned_exercise,
    COALESCE(SUM(CASE WHEN ma.event_type = 'burned_bmr' THEN ma.total_value END), 0) as monthly_calories_burned_bmr,
    
    -- Monthly net calculations
    COALESCE(SUM(CASE WHEN ma.event_type = 'consumed' THEN ma.total_value END), 0) - 
    COALESCE(SUM(CASE WHEN ma.event_type IN ('burned_exercise', 'burned_bmr') THEN ma.total_value END), 0) as monthly_net_calories,
    
    -- Daily averages for the month
    COALESCE(SUM(CASE WHEN ma.event_type = 'consumed' THEN ma.total_value END), 0) / 
    GREATEST(MAX(ma.active_days), 1) as avg_daily_consumed,
    
    -- Weekly averages for trend analysis
    COALESCE(SUM(CASE WHEN ma.event_type = 'consumed' THEN ma.total_value END), 0) / 
    GREATEST(MAX(ma.active_weeks), 1) as avg_weekly_consumed,
    
    -- Weight change tracking
    mw.month_start_weight,
    mw.month_end_weight,
    
    -- Engagement and consistency metrics
    MAX(ma.active_days) as active_days,
    MAX(ma.active_weeks) as active_weeks,
    SUM(ma.total_events) as total_events,
    AVG(ma.avg_confidence) as avg_confidence,
    SUM(ma.source_variety) as source_variety,
    
    -- Time range
    MIN(ma.first_event) as first_event,
    MAX(ma.last_event) as last_event

FROM monthly_aggregates ma
LEFT JOIN monthly_weights mw ON ma.user_id = mw.user_id AND ma.month_start = mw.month_start
GROUP BY ma.user_id, ma.month_start, ma.month_end, ma.year, ma.month, ma.month_label, mw.month_start_weight, mw.month_end_weight
ORDER BY ma.user_id, ma.month_start DESC;

-- =============================================================================
-- LEVEL 5: DAILY BALANCE SUMMARY (Net calories, weight correlation)
-- =============================================================================

CREATE OR REPLACE VIEW calorie_balance.daily_balance_summary AS
WITH daily_events AS (
    SELECT 
        user_id,
        DATE(event_timestamp) as date,
        SUM(CASE WHEN event_type = 'consumed' THEN value ELSE 0 END) as consumed,
        SUM(CASE WHEN event_type = 'burned_exercise' THEN value ELSE 0 END) as burned_exercise,
        SUM(CASE WHEN event_type = 'burned_bmr' THEN value ELSE 0 END) as burned_bmr,
        COUNT(*) as event_count,
        AVG(confidence_score) as avg_confidence
    FROM calorie_balance.calorie_events
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY user_id, DATE(event_timestamp)
),
daily_weights AS (
    SELECT DISTINCT
        user_id,
        DATE(event_timestamp) as date,
        FIRST_VALUE(value) OVER (PARTITION BY user_id, DATE(event_timestamp) ORDER BY event_timestamp ASC) as morning_weight,
        LAST_VALUE(value) OVER (PARTITION BY user_id, DATE(event_timestamp) ORDER BY event_timestamp DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as evening_weight,
        AVG(value) OVER (PARTITION BY user_id, DATE(event_timestamp)) as avg_weight
    FROM calorie_balance.calorie_events
    WHERE event_type = 'weight'
    AND event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
),
daily_goals AS (
    SELECT DISTINCT
        cg.user_id,
        d.date,
        cg.daily_calorie_target,
        cg.daily_deficit_target,
        cg.goal_type
    FROM calorie_balance.calorie_goals cg
    CROSS JOIN (
        SELECT DISTINCT DATE(event_timestamp) as date
        FROM calorie_balance.calorie_events
        WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
    ) d
    WHERE cg.is_active = true
    AND d.date BETWEEN cg.start_date AND COALESCE(cg.end_date, CURRENT_DATE)
)
SELECT 
    COALESCE(de.user_id, dw.user_id, dg.user_id) as user_id,
    COALESCE(de.date, dw.date, dg.date) as date,
    
    -- Calorie balance calculations
    COALESCE(de.consumed, 0) as calories_consumed,
    COALESCE(de.burned_exercise, 0) as calories_burned_exercise,
    COALESCE(de.burned_bmr, 0) as calories_burned_bmr,
    COALESCE(de.consumed, 0) - COALESCE(de.burned_exercise, 0) - COALESCE(de.burned_bmr, 0) as net_calories,
    
    -- Weight tracking
    dw.morning_weight,
    dw.evening_weight,
    dw.avg_weight,
    dw.evening_weight - dw.morning_weight as daily_weight_change,
    
    -- Goal tracking
    dg.daily_calorie_target,
    dg.daily_deficit_target,
    dg.goal_type,
    
    -- Goal deviation analysis
    CASE 
        WHEN dg.daily_calorie_target IS NOT NULL THEN
            (COALESCE(de.consumed, 0) - COALESCE(de.burned_exercise, 0) - COALESCE(de.burned_bmr, 0)) - dg.daily_calorie_target
        ELSE NULL
    END as target_deviation,
    
    -- Success indicators
    CASE 
        WHEN dg.daily_deficit_target IS NOT NULL THEN
            CASE 
                WHEN (COALESCE(de.consumed, 0) - COALESCE(de.burned_exercise, 0) - COALESCE(de.burned_bmr, 0)) <= (dg.daily_calorie_target + dg.daily_deficit_target) THEN true
                ELSE false
            END
        ELSE NULL
    END as goal_achieved,
    
    -- Data quality metrics
    COALESCE(de.event_count, 0) as event_count,
    de.avg_confidence,
    
    -- Completeness score (basic heuristic)
    CASE 
        WHEN de.consumed > 0 AND (de.burned_exercise > 0 OR de.burned_bmr > 0) THEN 1.0
        WHEN de.consumed > 0 OR de.burned_exercise > 0 OR de.burned_bmr > 0 THEN 0.7
        WHEN dw.morning_weight IS NOT NULL OR dw.evening_weight IS NOT NULL THEN 0.3
        ELSE 0.0
    END as data_completeness_score

FROM daily_events de
FULL OUTER JOIN daily_weights dw ON de.user_id = dw.user_id AND de.date = dw.date
FULL OUTER JOIN daily_goals dg ON COALESCE(de.user_id, dw.user_id) = dg.user_id AND COALESCE(de.date, dw.date) = dg.date
ORDER BY user_id, date DESC;

-- =============================================================================
-- VIEW PERFORMANCE INDEXES
-- =============================================================================

-- Additional indexes to optimize view queries (using IMMUTABLE-safe approaches)
-- Note: Removed EXTRACT-based index as EXTRACT is not IMMUTABLE in PostgreSQL
CREATE INDEX IF NOT EXISTS idx_calorie_events_user_weekly ON calorie_balance.calorie_events(user_id, event_timestamp) WHERE event_timestamp >= '2024-01-01'; -- More efficient than DATE_TRUNC 
CREATE INDEX IF NOT EXISTS idx_calorie_events_user_monthly ON calorie_balance.calorie_events(user_id, event_timestamp) WHERE event_timestamp >= '2024-01-01'; -- More efficient than DATE_TRUNC
CREATE INDEX IF NOT EXISTS idx_calorie_events_weight_user ON calorie_balance.calorie_events(user_id, event_timestamp) WHERE event_type = 'weight';

-- =============================================================================
-- VIEW VALIDATION
-- =============================================================================

-- Verify all views were created successfully
SELECT 
    table_name as view_name,
    'VIEW' as object_type
FROM information_schema.views 
WHERE table_schema = 'calorie_balance'
ORDER BY table_name;

-- Reset search path
RESET search_path;
