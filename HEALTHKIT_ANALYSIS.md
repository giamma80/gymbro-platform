# 🍎 HealthKit Data Analysis - GymBro Platform Integration

## 📅 Data: 1 Settembre 2025
## 🎯 Objective: Analyze HealthKit data structure for optimal database integration

---

## 📊 **HEALTHKIT DATA MAPPING ANALYSIS**

### ✅ **CURRENT MODEL COMPATIBILITY**

#### **DailyFitnessData Table (80% Compatible)**
```sql
-- ✅ DIRECTLY MAPPABLE FROM HEALTHKIT
steps INTEGER                 ← healthData.activity.steps.dailyTotal
calories_burned FLOAT         ← healthData.calories.activeEnergyBurned.dailyTotal  
calories_consumed FLOAT       ← healthData.calories.dietaryEnergyConsumed.dailyTotal
weight_kg FLOAT              ← healthData.bodyMeasurements.weight[0].value

-- 🔄 DERIVABLE FROM HEALTHKIT
sleep_hours FLOAT            ← Calculate from healthData.sleepAnalysis (endDate - startDate)
active_minutes INTEGER       ← Sum workout durations from healthData.workouts

-- 📝 MANUAL INPUT (NOT IN HEALTHKIT)
energy_level INTEGER         ← User input (1-10 scale)
mood_score INTEGER          ← User input (1-10 scale)  
notes TEXT                  ← User input
```

#### **UserActivity Table (95% Compatible)**  
```sql
-- ✅ DIRECTLY MAPPABLE FROM HEALTHKIT
activity_type VARCHAR        ← healthData.workouts[i].workoutActivityType (mapped)
activity_name VARCHAR        ← Derived from workoutActivityType
started_at TIMESTAMP         ← healthData.workouts[i].startDate  
ended_at TIMESTAMP          ← healthData.workouts[i].endDate
duration_minutes INTEGER    ← healthData.workouts[i].duration / 60
calories_burned FLOAT       ← healthData.workouts[i].totalEnergyBurned.value
distance_km FLOAT           ← healthData.workouts[i].totalDistance.value
avg_heart_rate INTEGER      ← healthData.workouts[i].metadata.HKAverageHeartRate
max_heart_rate INTEGER      ← healthData.workouts[i].metadata.HKMaximumHeartRate

-- 🔄 ENHANCED WITH HEALTHKIT
activity_data JSON          ← Store full HealthKit workout metadata
```

---

## 🚀 **HEALTHKIT ENRICHMENT OPPORTUNITIES**

### 💎 **HIGH VALUE DATA NOT CURRENTLY CAPTURED**

#### **1. Basal Metabolic Rate**
```json
healthData.calories.basalEnergyBurned.dailyTotal: 1680
```
**Impact**: Complete calorie picture (BMR + Active = Total Daily Energy Expenditure)

#### **2. Body Composition Metrics**
```json
healthData.bodyMeasurements.bodyMassIndex.value: 22.9
healthData.bodyMeasurements.bodyFatPercentage.value: 15.2
```
**Impact**: Advanced fitness tracking beyond just weight

#### **3. Detailed Heart Rate Data**
```json
healthData.heartRate.samples: [
  {value: 72, motionContext: "Sedentary"},
  {value: 155, motionContext: "Active"}
]
healthData.heartRate.restingHeartRate.value: 65
```
**Impact**: Cardiovascular fitness trends, recovery metrics

#### **4. Activity Granularity**
```json
healthData.activity.distance.samples
healthData.activity.floorsClimbed.samples
```
**Impact**: More detailed daily activity breakdown

#### **5. Sleep Quality Analysis**
```json
healthData.sleepAnalysis: [
  {value: "InBed", duration: 8.0},
  {value: "Asleep", duration: 7.0}
]
```
**Impact**: Sleep efficiency, sleep quality metrics

---

## 🏗️ **RECOMMENDED DATABASE ENHANCEMENTS**

### **Option A: Extend Existing Tables (Minimal Impact)**
```sql
-- ADD COLUMNS TO daily_fitness_data
ALTER TABLE daily_fitness_data ADD COLUMN basal_calories_burned FLOAT;
ALTER TABLE daily_fitness_data ADD COLUMN body_fat_percentage FLOAT;
ALTER TABLE daily_fitness_data ADD COLUMN resting_heart_rate INTEGER;
ALTER TABLE daily_fitness_data ADD COLUMN floors_climbed INTEGER;
ALTER TABLE daily_fitness_data ADD COLUMN sleep_efficiency FLOAT; -- (asleep_time / in_bed_time) * 100

-- ADD COLUMNS TO user_activities  
ALTER TABLE user_activities ADD COLUMN weather_temperature FLOAT;
ALTER TABLE user_activities ADD COLUMN weather_humidity FLOAT;
ALTER TABLE user_activities ADD COLUMN source_bundle VARCHAR(255);
ALTER TABLE user_activities ADD COLUMN device_type VARCHAR(100);
```

### **Option B: New Specialized Tables (Better Normalization)**
```sql
-- Heart Rate Samples (for detailed HR analysis)
CREATE TABLE heart_rate_samples (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    heart_rate INTEGER NOT NULL,
    motion_context VARCHAR(50), -- sedentary, active, etc.
    source_bundle VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sleep Sessions (detailed sleep analysis)
CREATE TABLE sleep_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    sleep_date DATE NOT NULL,
    in_bed_start TIMESTAMP WITH TIME ZONE,
    in_bed_end TIMESTAMP WITH TIME ZONE,
    asleep_start TIMESTAMP WITH TIME ZONE,
    asleep_end TIMESTAMP WITH TIME ZONE,
    total_time_in_bed_minutes INTEGER,
    total_sleep_minutes INTEGER,
    sleep_efficiency FLOAT, -- (sleep_minutes / in_bed_minutes) * 100
    source_bundle VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, sleep_date)
);

-- Body Measurements History
CREATE TABLE body_measurements (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    weight_kg FLOAT,
    body_mass_index FLOAT,
    body_fat_percentage FLOAT,
    muscle_mass_kg FLOAT,
    source_bundle VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🔄 **DATA INGESTION SERVICE REQUIREMENTS**

### **Core Features Needed:**
```python
class HealthKitDataIngestionService:
    """
    Service to process and store HealthKit data exports
    """
    
    async def process_healthkit_export(self, user_id: str, healthkit_json: dict):
        """Process complete HealthKit export"""
        
        # 1. Profile Data Sync
        await self._sync_profile_data(user_id, healthkit_json["profile"])
        
        # 2. Daily Fitness Aggregation  
        daily_data = self._aggregate_daily_fitness(healthkit_json)
        await self._upsert_daily_fitness(user_id, daily_data)
        
        # 3. Workout Processing
        for workout in healthkit_json["workouts"]:
            await self._process_workout(user_id, workout)
            
        # 4. Heart Rate Samples (if enabled)
        await self._process_heart_rate_samples(user_id, healthkit_json["heartRate"])
        
        # 5. Sleep Analysis
        await self._process_sleep_data(user_id, healthkit_json["sleepAnalysis"])

    def _aggregate_daily_fitness(self, healthkit_json: dict) -> dict:
        """Transform HealthKit samples into daily aggregates"""
        return {
            "steps": healthkit_json["activity"]["steps"]["dailyTotal"],
            "calories_burned": healthkit_json["calories"]["activeEnergyBurned"]["dailyTotal"],
            "calories_consumed": healthkit_json["calories"]["dietaryEnergyConsumed"]["dailyTotal"],
            "basal_calories": healthkit_json["calories"]["basalEnergyBurned"]["dailyTotal"],
            "distance_km": sum([s["value"] for s in healthkit_json["activity"]["distance"]["samples"]]),
            "floors_climbed": sum([s["value"] for s in healthkit_json["activity"]["floorsClimbed"]["samples"]]),
            "sleep_hours": self._calculate_sleep_hours(healthkit_json["sleepAnalysis"]),
            "resting_heart_rate": healthkit_json["heartRate"]["restingHeartRate"]["value"]
        }
```

---

## 🎯 **IMPLEMENTATION STRATEGY**

### **Phase 1: Core Integration (FASE 3 Extension)**
- ✅ Keep existing DailyFitnessData and UserActivity tables
- ✅ Add data ingestion endpoint: `POST /fitness/healthkit-sync`
- ✅ Implement HealthKit JSON → Database mapping
- ✅ Handle workout type mapping (HKWorkoutActivityType → activity_type)

### **Phase 2: Enhanced Metrics (FASE 4)**  
- ✅ Add basal_calories, body_fat_percentage to daily_fitness_data
- ✅ Implement sleep_hours calculation from sleepAnalysis
- ✅ Add weather and source_bundle to user_activities

### **Phase 3: Advanced Analytics (FASE 5)**
- ✅ Create heart_rate_samples table for detailed HR analysis
- ✅ Create sleep_sessions table for sleep quality tracking  
- ✅ Create body_measurements table for composition trends

---

## 🔧 **HEALTHKIT ACTIVITY TYPE MAPPING**

```python
HEALTHKIT_TO_GYMBRO_ACTIVITY_MAPPING = {
    "HKWorkoutActivityTypeRunning": "running",
    "HKWorkoutActivityTypeWalking": "walking", 
    "HKWorkoutActivityTypeTraditionalStrengthTraining": "weightlifting",
    "HKWorkoutActivityTypeCycling": "cycling",
    "HKWorkoutActivityTypeYoga": "yoga",
    "HKWorkoutActivityTypeSwimming": "swimming",
    "HKWorkoutActivityTypeHIIT": "hiit",
    "HKWorkoutActivityTypePilates": "pilates",
    "HKWorkoutActivityTypeDance": "dance",
    "HKWorkoutActivityTypeBoxing": "boxing",
    # ... expand as needed
}
```

---

## 📊 **DATA QUALITY CONSIDERATIONS**

### **Duplicate Detection:**
- Multiple sources can report same data (iPhone + Apple Watch + third-party apps)
- Use `sourceBundle` to prioritize data sources
- Implement conflict resolution strategy

### **Unit Conversion:**
- HealthKit uses metric (km, kg, kcal) ✅ matches our database
- Handle different timezones with ISO 8601 timestamps
- Validate data ranges (e.g., heart rate 40-220 bpm)

### **Missing Data Handling:**
```python
# Some users might not grant all permissions
if "heartRate" not in healthkit_json:
    logger.info("Heart rate data not available for user")
    
# Gracefully handle partial data
daily_data = {
    "steps": healthkit_json.get("activity", {}).get("steps", {}).get("dailyTotal", 0),
    "calories_burned": healthkit_json.get("calories", {}).get("activeEnergyBurned", {}).get("dailyTotal", 0)
    # ... with defaults
}
```

---

## 🎉 **BUSINESS VALUE**

### **Immediate Benefits:**
- **Automatic Data Entry**: No manual logging required for iPhone/Apple Watch users
- **Higher Data Accuracy**: Sensor-based measurements vs. manual estimates
- **Complete Activity Picture**: All workouts captured automatically

### **Advanced Analytics Potential:**
- **Recovery Metrics**: Heart rate variability, resting HR trends
- **Sleep Quality Impact**: Correlate sleep with performance
- **Metabolic Insights**: Complete TDEE calculation (BMR + Active)
- **Body Composition Trends**: Fat loss vs. muscle gain tracking

### **Competitive Advantage:**  
- **Seamless iOS Integration**: Native HealthKit sync
- **Professional-Grade Data**: Medical device accuracy
- **Rich Context**: Weather, location, device info for workouts

---

**📍 RECOMMENDATION**: Extend FASE 3 to include HealthKit ingestion endpoint
**🎯 PRIORITY**: High - Native iOS integration is table stakes for fitness apps
**⏱️ EFFORT**: +1 day to FASE 3 timeline for basic HealthKit sync capability

---

*Analysis completed: 1 Settembre 2025*
*Next: Integrate HealthKit sync into FASE 3 implementation plan*
