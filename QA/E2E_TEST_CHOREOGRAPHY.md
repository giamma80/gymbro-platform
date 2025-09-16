# End-to-End Test Choreography Specification
**GymBro Platform - Comprehensive Integration Testing**

## Overview
Documento che definisce la coreografia completa di test end-to-end per validare l'intera piattaforma GymBro, dalla creazione utente all'analytics avanzato, garantendo coerenza funzionale oltre ai semplici codici HTTP.

## Test Architecture
- **Target Services**: User-Management (8001), Calorie-Balance (8002), Apollo Gateway (4000)
- **Test Approach**: Scenario-based functional testing con validazione dati cross-service
- **Data Simulation**: Multi-day, multi-hour realistic calorie tracking scenarios
- **Validation Level**: HTTP status + functional coherence + data consistency

## Test Choreography Phases

### Phase 1: User Lifecycle Management
**Objective**: Validate complete user creation and retrieval workflow

#### Step 1.1: Create Test User
- **Method**: POST `/users` via user-management service
- **Data**: 
  ```json
  {
    "email": "qa-test-user-{timestamp}@gymbrotest.com",
    "username": "qa_testuser_{timestamp}",
    "password": "TestPass123!",
    "is_active": true
  }
  ```
- **Validation**:
  - HTTP 201 Created
  - Response contains valid user_id
  - Email format preserved
  - Username uniqueness verified
  - created_at timestamp reasonable

#### Step 1.2: Retrieve Created User
- **Method**: GET `/users/{user_id}` 
- **Validation**:
  - HTTP 200 OK
  - All fields match creation data
  - is_active = true
  - Timestamps consistent with creation time
  - **Store user_id for subsequent phases**

#### Step 1.3: GraphQL User Verification
- **Method**: POST `/graphql` via Apollo Gateway
- **Query**: 
  ```graphql
  query { getUser(userId: "{user_id}") { id email username isActive createdAt } }
  ```
- **Validation**:
  - GraphQL success response
  - Data consistency with REST API
  - Federation working correctly

### Phase 2: Metabolic Profile Setup
**Objective**: Establish user baseline metabolic calculations

#### Step 2.1: Calculate Metabolic Profile
- **Method**: POST `/metabolic-profiles/calculate` via calorie-balance service
- **Data**:
  ```json
  {
    "user_id": "{user_id_from_phase1}",
    "age": 30,
    "height": 175,
    "weight": 75,
    "gender": "male",
    "activity_level": "moderate"
  }
  ```
- **Validation**:
  - HTTP 201 Created
  - BMR calculation reasonable (1600-2000 for test profile)
  - TDEE > BMR (activity multiplier applied)
  - Accuracy score > 0.7

#### Step 2.2: Verify Metabolic Profile
- **Method**: GET `/metabolic-profiles/user/{user_id}`
- **Validation**:
  - Profile exists and active
  - Calculations consistent
  - expiry date in future

### Phase 3: Calorie Goal Configuration
**Objective**: Set user calorie targets for tracking

#### Step 3.1: Create Primary Calorie Goal
- **Method**: POST `/calorie-goals` via calorie-balance service
- **Data**:
  ```json
  {
    "user_id": "{user_id}",
    "goal_type": "weight_loss",
    "daily_calorie_target": 1800,
    "daily_deficit_target": 500,
    "weekly_weight_change_kg": -0.5,
    "start_date": "{current_date}",
    "end_date": "{current_date+30d}",
    "is_active": true
  }
  ```
- **Validation**:
  - HTTP 201 Created
  - Target < TDEE (deficit logic)
  - Deficit reasonable (300-700 cal)
  - Weight change realistic (0.3-0.8 kg/week)

### Phase 4: Multi-Day Calorie Event Simulation
**Objective**: Simulate realistic multi-day calorie tracking with temporal patterns

#### Day 1 Scenario - "Baseline Day"
**Date**: Current date - 2 days

##### Morning Events (08:00-12:00)
- **8:00**: Breakfast consumed +650 cal (source: manual_entry)
- **9:30**: Exercise burned -300 cal (source: fitness_tracker)
- **11:00**: Snack consumed +150 cal (source: manual_entry)

##### Afternoon Events (12:00-18:00)
- **13:00**: Lunch consumed +750 cal (source: manual_entry)
- **15:30**: Light exercise -200 cal (source: fitness_tracker)
- **16:00**: Snack consumed +100 cal (source: manual_entry)

##### Evening Events (18:00-23:00)
- **19:30**: Dinner consumed +800 cal (source: manual_entry)
- **21:00**: Dessert consumed +200 cal (source: manual_entry)

**Expected Daily Totals**: +1650 consumed, -500 burned, +1150 net

#### Day 2 Scenario - "High Activity Day"
**Date**: Current date - 1 day

##### Morning Events
- **7:30**: Light breakfast +400 cal
- **8:00**: Intense workout -600 cal
- **10:00**: Post-workout snack +250 cal

##### Afternoon Events
- **12:30**: Lunch +700 cal
- **14:00**: Walking -150 cal
- **16:30**: Protein shake +300 cal

##### Evening Events
- **18:00**: Large dinner +900 cal
- **20:00**: Evening walk -200 cal

**Expected Daily Totals**: +2550 consumed, -950 burned, +1600 net

#### Day 3 Scenario - "Current Day"
**Date**: Current date

##### Morning Events (simulate real-time)
- **8:00**: Breakfast +550 cal
- **10:00**: Morning exercise -400 cal
- **11:30**: Snack +120 cal

**Expected Partial Totals**: +670 consumed, -400 burned, +270 net

### Phase 5: Daily Balance Validation
**Objective**: Verify daily aggregation accuracy

#### Step 5.1: Validate Day 1 Balance
- **Method**: GET `/daily-balances/user/{user_id}/date/{day1_date}`
- **Validation**:
  - calories_consumed = 1650
  - calories_burned_exercise = 500
  - net_calories = 1150
  - events_count = 8
  - data_completeness_score > 0.8
  - target_deviation = 1150 - 1800 = -650 (under target)

#### Step 5.2: Validate Day 2 Balance  
- **Method**: GET `/daily-balances/user/{user_id}/date/{day2_date}`
- **Validation**:
  - calories_consumed = 2550
  - calories_burned_exercise = 950
  - net_calories = 1600
  - events_count = 8
  - target_deviation = 1600 - 1800 = -200 (closer to target)

#### Step 5.3: Validate Current Day Balance
- **Method**: GET `/daily-balances/user/{user_id}/current`
- **Validation**:
  - Partial day data correct
  - Real-time updates working
  - Projections reasonable

### Phase 6: Timeline Analytics Validation
**Objective**: Test comprehensive analytics APIs with functional coherence

#### Step 6.1: Hourly Analytics
- **Method**: GET `/analytics/hourly?user_id={user_id}&date={day1_date}`
- **Validation**:
  - 24 hourly data points
  - Non-zero values in event hours (8,9,11,13,15,16,19,21)
  - Zero values in non-event hours
  - Cumulative totals match daily balance
  - Peak consumption hours identified correctly

#### Step 6.2: Daily Analytics Comparison
- **Method**: GET `/analytics/daily?user_id={user_id}&start_date={day1_date}&end_date={current_date}`
- **Validation**:
  - 3 daily data points
  - Trend analysis: Day 1 → Day 2 (increased intake)
  - Goal adherence progression
  - Weight trend consistency
  - Behavioral pattern identification

#### Step 6.3: Weekly Analytics
- **Method**: GET `/analytics/weekly?user_id={user_id}&weeks=1`
- **Validation**:
  - Week average calculations correct
  - Active days = 3
  - Goal adherence percentage reasonable
  - Weekly totals sum correctly

#### Step 6.4: Behavioral Pattern Detection
- **Method**: GET `/analytics/patterns?user_id={user_id}&pattern_type=eating_schedule`
- **Validation**:
  - Morning eating pattern detected (consistent 8:00 breakfast)
  - Evening consumption pattern (19:00-21:00 dinner/dessert)
  - Exercise pattern recognition (morning preference)
  - Confidence scores > 0.6

### Phase 7: GraphQL Federation End-to-End
**Objective**: Validate complete federated queries across services

#### Step 7.1: Cross-Service User Profile Query
```graphql
query {
  getUser(userId: "{user_id}") {
    id
    email
    username
    calorie_goals {
      id
      goal_type
      daily_calorie_target
      is_active
    }
    current_daily_balance {
      date
      calories_consumed
      calories_burned_exercise
      net_calories
      target_deviation
    }
    metabolic_profile {
      bmr_calories
      tdee_calories
      activity_level
      accuracy_score
    }
  }
}
```
- **Validation**:
  - All nested data resolves correctly
  - Cross-service data consistency
  - Federation performance acceptable (<2s)
  - No GraphQL errors

#### Step 7.2: Timeline Analytics via GraphQL
```graphql
query {
  getDailyAnalytics(userId: "{user_id}", startDate: "{day1_date}", endDate: "{current_date}") {
    success
    data {
      date
      calories_consumed
      calories_burned_exercise
      net_calories
      goal_target
      goal_deviation
      trend_direction
      active_hours
    }
    metadata
  }
}
```

### Phase 8: Data Consistency Cross-Validation
**Objective**: Ensure data integrity across all endpoints

#### Step 8.1: REST vs GraphQL Consistency
- Compare same data via REST and GraphQL endpoints
- Validate identical values for all fields
- Check timestamp consistency

#### Step 8.2: Aggregation Consistency  
- Sum hourly data → verify equals daily totals
- Sum daily data → verify equals weekly totals
- Validate all calculated fields

#### Step 8.3: Real-time Update Validation
- Add new calorie event
- Verify immediate balance update
- Check analytics reflect change
- Validate GraphQL real-time consistency

## Success Criteria

### HTTP Level
- All requests return expected status codes
- Response times < 1000ms (except complex analytics)
- No 500 server errors

### Functional Level  
- All calculations mathematically correct
- Temporal data properly sequenced
- Cross-service data consistency maintained
- Business rules enforced (deficits, targets, etc.)

### Integration Level
- GraphQL Federation performs correctly
- Real-time updates propagate
- Data persistence across service restarts
- Concurrent user scenarios handle correctly

## Test Data Cleanup
After test completion:
- Delete created test user
- Remove all associated calorie events
- Clean up goals and balances
- Reset database sequences if needed

## Implementation Notes
- Use dynamic timestamps to avoid conflicts
- Implement proper error handling and rollback
- Create detailed execution logs
- Measure and report performance metrics
- Support parallel test execution

---

**Next Steps**: Create executable test script implementing this choreography.