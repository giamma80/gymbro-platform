"""
🍎 HealthKit Data Mapping Service
===============================

Helper functions per convertire dati HealthKit in formato GymBro.
Supporta mapping completo dei dati Apple Health -> Database models.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# ==========================================
# 🗺️ HEALTHKIT ACTIVITY TYPE MAPPING
# ==========================================

HEALTHKIT_TO_GYMBRO_ACTIVITY_MAPPING = {
    "HKWorkoutActivityTypeRunning": "running",
    "HKWorkoutActivityTypeWalking": "walking",
    "HKWorkoutActivityTypeTraditionalStrengthTraining": "weightlifting",
    "HKWorkoutActivityTypeFunctionalStrengthTraining": "functional_training",
    "HKWorkoutActivityTypeHighIntensityIntervalTraining": "hiit",
    "HKWorkoutActivityTypeCycling": "cycling",
    "HKWorkoutActivityTypeYoga": "yoga",
    "HKWorkoutActivityTypeSwimming": "swimming",
    "HKWorkoutActivityTypePilates": "pilates",
    "HKWorkoutActivityTypeDance": "dance",
    "HKWorkoutActivityTypeBoxing": "boxing",
    "HKWorkoutActivityTypeRowing": "rowing",
    "HKWorkoutActivityTypeElliptical": "elliptical",
    "HKWorkoutActivityTypeStairClimbing": "stair_climbing",
    "HKWorkoutActivityTypeCrossTraining": "cross_training",
    "HKWorkoutActivityTypeCoreTraining": "core_training",
    "HKWorkoutActivityTypeFlexibility": "stretching",
    "HKWorkoutActivityTypeMindAndBody": "mind_body",
    "HKWorkoutActivityTypeOther": "other",
}

# ==========================================
# 📊 DAILY FITNESS DATA MAPPING
# ==========================================

class HealthKitDataMapper:
    """Helper class for mapping HealthKit data to GymBro models"""
    
    @staticmethod
    def map_daily_fitness_data(
        healthkit_data: Dict[str, Any], 
        target_date: date
    ) -> Dict[str, Any]:
        """
        Map HealthKit daily data to DailyFitnessData model
        
        Args:
            healthkit_data: Complete HealthKit export JSON
            target_date: Date for which to extract daily data
            
        Returns:
            Dict with DailyFitnessData fields
        """
        try:
            # Extract activity data
            activity_data = healthkit_data.get("activity", {})
            steps = activity_data.get("steps", {}).get("dailyTotal", 0)
            distance_samples = activity_data.get("distance", {}).get("samples", [])
            floors_samples = activity_data.get("floorsClimbed", {}).get("samples", [])
            
            # Calculate distance and floors for the day
            daily_distance = sum([
                sample.get("value", 0) for sample in distance_samples 
                if sample.get("date") == target_date.isoformat()
            ])
            
            daily_floors = sum([
                sample.get("value", 0) for sample in floors_samples
                if sample.get("date") == target_date.isoformat()
            ])
            
            # Extract calorie data
            calories_data = healthkit_data.get("calories", {})
            calories_active = calories_data.get("activeEnergyBurned", {}).get("dailyTotal", 0)
            calories_basal = calories_data.get("basalEnergyBurned", {}).get("dailyTotal", 0)
            calories_consumed = calories_data.get("dietaryEnergyConsumed", {}).get("dailyTotal", 0)
            
            # Extract body measurements
            body_data = healthkit_data.get("bodyMeasurements", {})
            weight_kg = None
            body_mass_index = None
            body_fat_percentage = None
            
            if "weight" in body_data and body_data["weight"]:
                weight_kg = body_data["weight"][0].get("value")
            if "bodyMassIndex" in body_data and body_data["bodyMassIndex"]:
                body_mass_index = body_data["bodyMassIndex"][0].get("value")
            if "bodyFatPercentage" in body_data and body_data["bodyFatPercentage"]:
                body_fat_percentage = body_data["bodyFatPercentage"][0].get("value")
            
            # Extract heart rate data
            heart_data = healthkit_data.get("heartRate", {})
            resting_hr = None
            hrv = None
            
            if "restingHeartRate" in heart_data and heart_data["restingHeartRate"]:
                resting_hr = heart_data["restingHeartRate"].get("value")
            if "heartRateVariability" in heart_data and heart_data["heartRateVariability"]:
                hrv = heart_data["heartRateVariability"][0].get("value")
            
            # Extract sleep data
            sleep_data = healthkit_data.get("sleepAnalysis", [])
            total_sleep_hours = 0
            total_bed_hours = 0
            
            for sleep_session in sleep_data:
                if sleep_session.get("date") == target_date.isoformat():
                    if sleep_session.get("value") == "Asleep":
                        total_sleep_hours += sleep_session.get("duration", 0)
                    elif sleep_session.get("value") == "InBed":
                        total_bed_hours += sleep_session.get("duration", 0)
            
            # Calculate active minutes from workouts
            workouts = healthkit_data.get("workouts", [])
            active_minutes = sum([
                workout.get("duration", 0) / 60 for workout in workouts
                if workout.get("startDate", "").startswith(target_date.isoformat())
            ])
            
            return {
                "date": target_date,
                "steps": int(steps),
                "active_minutes": int(active_minutes),
                "floors_climbed": int(daily_floors),
                "distance_km": round(daily_distance, 2),
                
                # Enhanced calorie tracking
                "calories_active": round(calories_active, 1),
                "calories_basal": round(calories_basal, 1),
                "calories_consumed": round(calories_consumed, 1),
                # Legacy compatibility
                "calories_burned": round(calories_active, 1),
                
                # Body composition
                "weight_kg": round(weight_kg, 1) if weight_kg else None,
                "body_mass_index": round(body_mass_index, 1) if body_mass_index else None,
                "body_fat_percentage": round(body_fat_percentage, 1) if body_fat_percentage else None,
                
                # Health metrics
                "resting_heart_rate": int(resting_hr) if resting_hr else None,
                "heart_rate_variability": round(hrv, 1) if hrv else None,
                
                # Sleep analysis
                "sleep_hours_total": round(total_sleep_hours, 1) if total_sleep_hours > 0 else None,
                "sleep_hours_in_bed": round(total_bed_hours, 1) if total_bed_hours > 0 else None,
                # Legacy compatibility
                "sleep_hours": round(total_sleep_hours, 1) if total_sleep_hours > 0 else None,
                
                # Metadata
                "data_source": "healthkit",
                "notes": f"Imported from HealthKit on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            
        except Exception as e:
            logger.error(f"Error mapping HealthKit daily fitness data: {e}")
            raise

    @staticmethod
    def map_workout_data(healthkit_workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map single HealthKit workout to UserActivity model
        
        Args:
            healthkit_workout: Single workout object from HealthKit export
            
        Returns:
            Dict with UserActivity fields
        """
        try:
            # Map activity type
            healthkit_type = healthkit_workout.get("workoutActivityType", "HKWorkoutActivityTypeOther")
            activity_type = HEALTHKIT_TO_GYMBRO_ACTIVITY_MAPPING.get(
                healthkit_type, 
                "other"
            )
            
            # Parse timing
            start_date_str = healthkit_workout.get("startDate", "")
            end_date_str = healthkit_workout.get("endDate", "")
            
            started_at = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")) if start_date_str else None
            ended_at = datetime.fromisoformat(end_date_str.replace("Z", "+00:00")) if end_date_str else None
            
            duration_minutes = healthkit_workout.get("duration", 0) / 60
            
            # Extract metrics
            calories_burned = healthkit_workout.get("totalEnergyBurned", {}).get("value", 0)
            distance_km = healthkit_workout.get("totalDistance", {}).get("value", 0)
            
            # Heart rate data
            metadata = healthkit_workout.get("metadata", {})
            avg_hr = metadata.get("HKAverageHeartRate")
            max_hr = metadata.get("HKMaximumHeartRate")
            min_hr = metadata.get("HKMinimumHeartRate")
            
            # Environmental data
            weather_temp = metadata.get("HKWeatherTemperature")
            weather_humidity = metadata.get("HKWeatherHumidity")
            
            # Elevation data
            elevation_gain = healthkit_workout.get("totalElevationAscended", {}).get("value")
            elevation_loss = healthkit_workout.get("totalElevationDescended", {}).get("value")
            
            # Create activity name
            activity_name = f"{activity_type.replace('_', ' ').title()}"
            if distance_km > 0:
                activity_name += f" ({distance_km:.1f}km)"
            
            # Heart rate zones (if available in metadata)
            hr_zones = {
                "hr_zone_1_seconds": metadata.get("HKTimeInHeartRateZone1", 0),
                "hr_zone_2_seconds": metadata.get("HKTimeInHeartRateZone2", 0),
                "hr_zone_3_seconds": metadata.get("HKTimeInHeartRateZone3", 0),
                "hr_zone_4_seconds": metadata.get("HKTimeInHeartRateZone4", 0),
                "hr_zone_5_seconds": metadata.get("HKTimeInHeartRateZone5", 0),
            }
            
            return {
                "activity_type": activity_type,
                "activity_name": activity_name,
                "started_at": started_at,
                "ended_at": ended_at,
                "duration_minutes": int(duration_minutes),
                
                # Performance metrics
                "calories_burned": round(calories_burned, 1) if calories_burned else None,
                "distance_km": round(distance_km, 2) if distance_km else None,
                
                # Heart rate data
                "avg_heart_rate": int(avg_hr) if avg_hr else None,
                "max_heart_rate": int(max_hr) if max_hr else None,
                "min_heart_rate": int(min_hr) if min_hr else None,
                
                # Environmental context
                "weather_temperature": round(weather_temp, 1) if weather_temp else None,
                "weather_humidity": round(weather_humidity, 1) if weather_humidity else None,
                
                # Elevation data
                "elevation_gain_m": round(elevation_gain, 1) if elevation_gain else None,
                "elevation_loss_m": round(elevation_loss, 1) if elevation_loss else None,
                
                # Heart rate zones
                **hr_zones,
                
                # Metadata
                "data_source": "healthkit",
                "source_bundle": "com.apple.Health",
                "device_type": metadata.get("HKDeviceName", "iPhone"),
                "healthkit_uuid": healthkit_workout.get("uuid"),
                
                # Structured data (preserve original HealthKit data)
                "activity_data": {
                    "healthkit_metadata": metadata,
                    "original_type": healthkit_type,
                    "workout_events": healthkit_workout.get("workoutEvents", [])
                },
                
                "notes": f"Imported from HealthKit - {healthkit_type}"
            }
            
        except Exception as e:
            logger.error(f"Error mapping HealthKit workout data: {e}")
            raise

    @staticmethod
    def validate_healthkit_export(healthkit_data: Dict[str, Any]) -> bool:
        """
        Validate that HealthKit export contains required data structures
        
        Args:
            healthkit_data: HealthKit export JSON
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_keys = ["activity", "calories", "workouts"]
        
        for key in required_keys:
            if key not in healthkit_data:
                logger.warning(f"Missing required key in HealthKit export: {key}")
                return False
        
        # Check for basic activity data
        activity_data = healthkit_data.get("activity", {})
        if "steps" not in activity_data:
            logger.warning("Missing steps data in HealthKit activity")
            return False
        
        logger.info("✅ HealthKit export validation passed")
        return True

    @staticmethod
    def estimate_missing_data(mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate missing data points using available information
        
        Args:
            mapped_data: Partially mapped fitness data
            
        Returns:
            Enhanced data with estimated values
        """
        # Estimate active minutes from steps (rough approximation)
        if mapped_data.get("active_minutes", 0) == 0 and mapped_data.get("steps", 0) > 0:
            steps = mapped_data["steps"]
            # Rough estimate: every 100 steps = 1 minute of activity
            estimated_active_minutes = max(0, (steps - 5000) // 100)
            mapped_data["active_minutes"] = int(estimated_active_minutes)
        
        # Estimate muscle mass from weight and body fat
        weight_kg = mapped_data.get("weight_kg")
        body_fat_pct = mapped_data.get("body_fat_percentage")
        
        if weight_kg and body_fat_pct and not mapped_data.get("muscle_mass_kg"):
            muscle_mass = weight_kg * (1 - (body_fat_pct / 100))
            mapped_data["muscle_mass_kg"] = round(muscle_mass, 1)
        
        return mapped_data


# ==========================================
# 🧪 TESTING FUNCTIONS
# ==========================================

def test_healthkit_mapping():
    """Test function per verificare il mapping HealthKit"""
    
    # Sample HealthKit data structure
    sample_data = {
        "activity": {
            "steps": {"dailyTotal": 12500},
            "distance": {
                "samples": [
                    {"date": "2025-09-01", "value": 8.2},
                    {"date": "2025-09-02", "value": 6.1}
                ]
            },
            "floorsClimbed": {
                "samples": [
                    {"date": "2025-09-01", "value": 15}
                ]
            }
        },
        "calories": {
            "activeEnergyBurned": {"dailyTotal": 520},
            "basalEnergyBurned": {"dailyTotal": 1680},
            "dietaryEnergyConsumed": {"dailyTotal": 2100}
        },
        "bodyMeasurements": {
            "weight": [{"value": 72.5}],
            "bodyMassIndex": [{"value": 22.8}],
            "bodyFatPercentage": [{"value": 15.3}]
        },
        "heartRate": {
            "restingHeartRate": {"value": 64}
        },
        "sleepAnalysis": [
            {"date": "2025-09-01", "value": "Asleep", "duration": 7.2},
            {"date": "2025-09-01", "value": "InBed", "duration": 8.1}
        ],
        "workouts": [
            {
                "workoutActivityType": "HKWorkoutActivityTypeRunning",
                "startDate": "2025-09-01T07:00:00Z",
                "endDate": "2025-09-01T07:45:00Z",
                "duration": 2700,  # 45 minutes
                "totalEnergyBurned": {"value": 420},
                "totalDistance": {"value": 6.5},
                "metadata": {
                    "HKAverageHeartRate": 155,
                    "HKMaximumHeartRate": 175,
                    "HKWeatherTemperature": 18.5
                },
                "uuid": "ABC123-DEF456"
            }
        ]
    }
    
    mapper = HealthKitDataMapper()
    
    # Test daily fitness mapping
    target_date = date(2025, 9, 1)
    daily_data = mapper.map_daily_fitness_data(sample_data, target_date)
    print("📊 Daily Fitness Mapping:")
    print(f"  Steps: {daily_data['steps']}")
    print(f"  Calories Active: {daily_data['calories_active']}")
    print(f"  Calories Total: {daily_data['calories_active'] + daily_data['calories_basal']}")
    print(f"  Sleep Efficiency: {(daily_data['sleep_hours_total'] / daily_data['sleep_hours_in_bed']) * 100:.1f}%")
    
    # Test workout mapping
    workout_data = mapper.map_workout_data(sample_data["workouts"][0])
    print("\n🏃‍♂️ Workout Mapping:")
    print(f"  Activity: {workout_data['activity_name']}")
    print(f"  Duration: {workout_data['duration_minutes']} minutes")
    print(f"  Avg HR: {workout_data['avg_heart_rate']} bpm")
    print(f"  Distance: {workout_data['distance_km']} km")
    
    print("\n✅ HealthKit mapping test completed!")

if __name__ == "__main__":
    test_healthkit_mapping()
