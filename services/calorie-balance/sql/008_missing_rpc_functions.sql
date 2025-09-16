-- ============================================================================
-- 008_missing_rpc_functions.sql
-- 
-- Create missing RPC functions called by calorie-balance service
-- Issue: Repository calls functions that don't exist in database
-- ============================================================================

-- Set search path to avoid schema prefixes
SET search_path TO calorie_balance, public;

-- ============================================================================
-- 1. RECALCULATE DAILY BALANCE
-- ============================================================================
-- Function to recalculate daily balance from calorie events
-- Called by: SupabaseDailyBalanceRepository.recalculate_balance()

CREATE OR REPLACE FUNCTION recalculate_daily_balance(
    p_user_id TEXT,
    p_date DATE
) RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_consumed DECIMAL := 0;
    v_burned DECIMAL := 0;
    v_goal DECIMAL := 0;
    v_result JSON;
BEGIN
    -- Calculate consumed calories from events
    SELECT COALESCE(SUM(value), 0)
    INTO v_consumed
    FROM calorie_balance.calorie_events
    WHERE user_id = p_user_id::UUID
      AND DATE(event_timestamp) = p_date
      AND event_type = 'consumed';

    -- Calculate burned calories from events  
    SELECT COALESCE(SUM(value), 0)
    INTO v_burned
    FROM calorie_balance.calorie_events
    WHERE user_id = p_user_id::UUID
      AND DATE(event_timestamp) = p_date
      AND event_type = 'burned_exercise';

    -- Get daily goal (from daily_balances or calorie_goals)
    SELECT COALESCE(daily_calorie_target, 0)
    INTO v_goal
    FROM calorie_balance.daily_balances
    WHERE user_id = p_user_id::UUID
      AND date = p_date
    LIMIT 1;

    -- If no goal found in daily_balances, get from calorie_goals
    IF v_goal = 0 THEN
        SELECT COALESCE(daily_calorie_target, 0)
        INTO v_goal
        FROM calorie_balance.calorie_goals
        WHERE user_id = p_user_id::UUID
          AND is_active = true
        ORDER BY created_at DESC
        LIMIT 1;
    END IF;

    -- Insert or update daily_balances
    INSERT INTO calorie_balance.daily_balances (
        user_id, date, calories_consumed, calories_burned_exercise, 
        daily_calorie_target, created_at, updated_at
    ) VALUES (
        p_user_id::UUID, p_date, v_consumed, v_burned,
        v_goal, NOW(), NOW()
    )
    ON CONFLICT (user_id, date) DO UPDATE SET
        calories_consumed = v_consumed,
        calories_burned_exercise = v_burned,
        daily_calorie_target = v_goal,
        updated_at = NOW();

    -- Return the balance data
    SELECT json_build_object(
        'user_id', p_user_id,
        'date', p_date,
        'calories_consumed', v_consumed::text,
        'calories_burned', v_burned::text,
        'net_calories', (v_consumed - v_burned)::text,
        'daily_goal', v_goal::text,
        'progress_percentage', 
        CASE 
            WHEN v_goal > 0 THEN (v_consumed / v_goal * 100)::DECIMAL(5,2)
            ELSE 0
        END,
        'weight_kg', NULL,
        'metabolic_data', '{}'::json
    ) INTO v_result;

    RETURN v_result;
END;
$$;

-- ============================================================================
-- 2. GET USER STATISTICS
-- ============================================================================
-- Function to get comprehensive user statistics
-- Called by: SupabaseTemporalAnalyticsRepository.get_statistics()

CREATE OR REPLACE FUNCTION get_user_statistics(
    p_user_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_result JSON;
    v_total_days INTEGER;
    v_avg_consumed DECIMAL;
    v_avg_burned DECIMAL;
    v_avg_net DECIMAL;
    v_total_events INTEGER;
BEGIN
    -- Calculate date range
    v_total_days := (p_end_date - p_start_date) + 1;

    -- Get average values from daily_balances
    SELECT 
        COALESCE(AVG(calories_consumed::DECIMAL), 0),
        COALESCE(AVG(calories_burned_exercise::DECIMAL), 0),
        COALESCE(AVG(net_calories::DECIMAL), 0)
    INTO v_avg_consumed, v_avg_burned, v_avg_net
    FROM calorie_balance.daily_balances
    WHERE user_id = p_user_id::UUID
      AND date BETWEEN p_start_date AND p_end_date;

    -- Get total events count
    SELECT COUNT(*)
    INTO v_total_events
    FROM calorie_balance.calorie_events
    WHERE user_id = p_user_id::UUID
      AND DATE(event_timestamp) BETWEEN p_start_date AND p_end_date;

    -- Build result JSON
    SELECT json_build_object(
        'period', json_build_object(
            'start_date', p_start_date,
            'end_date', p_end_date,
            'total_days', v_total_days
        ),
        'averages', json_build_object(
            'daily_consumed', v_avg_consumed,
            'daily_burned', v_avg_burned,
            'daily_net', v_avg_net
        ),
        'totals', json_build_object(
            'events_logged', v_total_events
        ),
        'trends', json_build_object(
            'weight_trend', 'stable',
            'calorie_trend', 'consistent'
        )
    ) INTO v_result;

    RETURN v_result;
END;
$$;

-- ============================================================================
-- 3. GET USER TRENDS  
-- ============================================================================
-- Function to get user trends analysis
-- Called by: SupabaseTemporalAnalyticsRepository.get_trends()

CREATE OR REPLACE FUNCTION get_user_trends(
    p_user_id TEXT,
    p_days INTEGER DEFAULT 30
) RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_result JSON;
    v_start_date DATE;
    v_recent_avg DECIMAL;
    v_previous_avg DECIMAL;
    v_trend VARCHAR(20);
BEGIN
    -- Calculate date ranges
    v_start_date := CURRENT_DATE - INTERVAL '1 day' * p_days;

    -- Get recent period average (last half of period)
    SELECT COALESCE(AVG(net_calories::DECIMAL), 0)
    INTO v_recent_avg
    FROM calorie_balance.daily_balances
    WHERE user_id = p_user_id::UUID
      AND date BETWEEN (v_start_date + INTERVAL '1 day' * (p_days/2)) AND CURRENT_DATE;

    -- Get previous period average (first half of period)
    SELECT COALESCE(AVG(net_calories::DECIMAL), 0)
    INTO v_previous_avg
    FROM calorie_balance.daily_balances
    WHERE user_id = p_user_id::UUID
      AND date BETWEEN v_start_date AND (v_start_date + INTERVAL '1 day' * (p_days/2));

    -- Determine trend
    IF v_recent_avg > v_previous_avg + 100 THEN
        v_trend := 'increasing';
    ELSIF v_recent_avg < v_previous_avg - 100 THEN
        v_trend := 'decreasing';
    ELSE
        v_trend := 'stable';
    END IF;

    -- Build result JSON
    SELECT json_build_object(
        'analysis_period', p_days,
        'trend_direction', v_trend,
        'recent_average', v_recent_avg,
        'previous_average', v_previous_avg,
        'change_calories', v_recent_avg - v_previous_avg,
        'recommendations', CASE v_trend
            WHEN 'increasing' THEN 'Consider increasing physical activity'
            WHEN 'decreasing' THEN 'Monitor energy levels and nutrition'
            ELSE 'Maintain current routine'
        END
    ) INTO v_result;

    RETURN v_result;
END;
$$;

-- ============================================================================
-- 4. GRANTS AND PERMISSIONS
-- ============================================================================

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION recalculate_daily_balance(TEXT, DATE) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_statistics(TEXT, DATE, DATE) TO authenticated;  
GRANT EXECUTE ON FUNCTION get_user_trends(TEXT, INTEGER) TO authenticated;

-- Grant execute permissions to service role
GRANT EXECUTE ON FUNCTION recalculate_daily_balance(TEXT, DATE) TO service_role;
GRANT EXECUTE ON FUNCTION get_user_statistics(TEXT, DATE, DATE) TO service_role;
GRANT EXECUTE ON FUNCTION get_user_trends(TEXT, INTEGER) TO service_role;

-- ============================================================================
-- 5. FUNCTION COMMENTS
-- ============================================================================

COMMENT ON FUNCTION recalculate_daily_balance(TEXT, DATE) IS 
'Recalculates daily balance from calorie events for data consistency';

COMMENT ON FUNCTION get_user_statistics(TEXT, DATE, DATE) IS 
'Returns comprehensive user statistics for specified date range';

COMMENT ON FUNCTION get_user_trends(TEXT, INTEGER) IS 
'Analyzes user trends and provides recommendations based on recent data';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================