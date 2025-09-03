"""
Enhanced Analytics Service with HealthKit Integration
Processes enhanced fitness data from User Management Service
"""

from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
from dataclasses import dataclass
import structlog

from app.http_client import user_management_client, ServiceError
from app.models import (
    DailyStatsRecord, TimeRangeStats, UserDashboard, DashboardFilters
)

logger = structlog.get_logger()


@dataclass
class MetabolicAnalysis:
    """Metabolic analysis results"""
    avg_bmr: float  # Basal Metabolic Rate
    avg_active_calories: float  # Active calories burned
    avg_tdee: float  # Total Daily Energy Expenditure
    caloric_balance_trend: str  # "surplus", "deficit", "maintenance"
    metabolic_efficiency: float  # % of target calories achieved


@dataclass
class BodyCompositionTrend:
    """Body composition trend analysis"""
    weight_change_kg: float
    bmi_change: float
    body_fat_change_percent: Optional[float] = None
    muscle_mass_change_kg: Optional[float] = None
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable"


@dataclass
class CardiovascularAnalysis:
    """Cardiovascular fitness analysis"""
    avg_resting_hr: Optional[float] = None
    avg_hrv: Optional[float] = None
    cardiovascular_fitness_trend: str = "stable"
    zone_distribution: Dict[str, float] = None  # HR zones 1-5 percentages


@dataclass
class SleepPerformanceCorrelation:
    """Sleep quality vs performance correlation"""
    avg_sleep_efficiency: float
    sleep_quality_score: float  # 1-10
    performance_on_good_sleep: float
    performance_on_poor_sleep: float
    correlation_strength: str  # "strong", "moderate", "weak"


class EnhancedAnalyticsService:
    """Enhanced Analytics Service with HealthKit integration"""
    
    def __init__(self):
        self.client = user_management_client
        
    async def get_enhanced_user_dashboard(
        self, 
        user_id: str,
        filters: Optional[DashboardFilters] = None
    ) -> Dict[str, Any]:
        """Generate enhanced dashboard with HealthKit analytics"""
        
        try:
            # Get base fitness data and activities
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            fitness_data = await self.client.get_daily_fitness_data(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            activities = await self.client.get_user_activities(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not fitness_data:
                return self._empty_dashboard(user_id)
            
            # Perform enhanced analytics
            metabolic = await self._analyze_metabolic_data(fitness_data)
            body_comp = await self._analyze_body_composition(fitness_data)
            cardio = await self._analyze_cardiovascular_health(
                fitness_data, activities
            )
            sleep_perf = await self._analyze_sleep_performance(
                fitness_data, activities
            )
            
            return {
                "user_id": user_id,
                "generated_at": datetime.now(),
                "period_days": 30,
                
                # Enhanced Analytics
                "metabolic_analysis": metabolic,
                "body_composition_trend": body_comp,
                "cardiovascular_analysis": cardio,
                "sleep_performance_correlation": sleep_perf,
                
                # Traditional metrics
                "current_stats": self._get_current_stats(fitness_data),
                "weekly_summary": self._get_weekly_summary(fitness_data[-7:]),
                "monthly_summary": self._get_monthly_summary(fitness_data),
                
                # Activity insights
                "top_activities": self._get_top_activities(activities),
                "activity_consistency": self._calculate_consistency(activities),
                
                # Recommendations
                "recommendations": await self._generate_recommendations(
                    metabolic, body_comp, cardio, sleep_perf
                )
            }
            
        except ServiceError as e:
            logger.error("Service error in enhanced dashboard", 
                        user_id=user_id, error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error in enhanced dashboard", 
                        user_id=user_id, error=str(e))
            return self._empty_dashboard(user_id)
    
    async def _analyze_metabolic_data(
        self, fitness_data: List[Dict]
    ) -> MetabolicAnalysis:
        """Analyze metabolic data with enhanced HealthKit fields"""
        
        if not fitness_data:
            return MetabolicAnalysis(0, 0, 0, "insufficient_data", 0)
            
        # Extract enhanced metabolic fields
        bmr_values = [
            d.get("basal_energy_burned", 0) for d in fitness_data 
            if d.get("basal_energy_burned")
        ]
        active_cal_values = [
            d.get("active_energy_burned", 0) for d in fitness_data
            if d.get("active_energy_burned")
        ]
        
        avg_bmr = sum(bmr_values) / len(bmr_values) if bmr_values else 0
        avg_active = sum(active_cal_values) / len(active_cal_values) if active_cal_values else 0
        avg_tdee = avg_bmr + avg_active
        
        # Calculate caloric balance trend
        consumed_values = [
            d.get("calories_consumed", 0) for d in fitness_data[-7:]  # Last week
        ]
        burned_values = [
            (d.get("active_energy_burned", 0) + d.get("basal_energy_burned", 0))
            for d in fitness_data[-7:]
        ]
        
        avg_consumed = sum(consumed_values) / len(consumed_values) if consumed_values else 0
        avg_burned = sum(burned_values) / len(burned_values) if burned_values else 0
        
        balance_ratio = avg_consumed / avg_burned if avg_burned > 0 else 1
        
        if balance_ratio > 1.1:
            trend = "surplus"
        elif balance_ratio < 0.9:
            trend = "deficit"
        else:
            trend = "maintenance"
            
        # Calculate metabolic efficiency (% of realistic calorie target achieved)
        target_active = avg_bmr * 0.3  # Rough 30% of BMR as active goal
        efficiency = min(100, (avg_active / target_active * 100)) if target_active > 0 else 0
        
        return MetabolicAnalysis(
            avg_bmr=round(avg_bmr, 1),
            avg_active_calories=round(avg_active, 1),
            avg_tdee=round(avg_tdee, 1),
            caloric_balance_trend=trend,
            metabolic_efficiency=round(efficiency, 1)
        )
    
    async def _analyze_body_composition(
        self, fitness_data: List[Dict]
    ) -> BodyCompositionTrend:
        """Analyze body composition trends"""
        
        if len(fitness_data) < 2:
            return BodyCompositionTrend(0, 0)
            
        # Get first and last measurements
        first_record = fitness_data[0]
        last_record = fitness_data[-1]
        
        weight_change = (
            last_record.get("weight_kg", 0) - first_record.get("weight_kg", 0)
        )
        
        bmi_change = (
            last_record.get("bmi", 0) - first_record.get("bmi", 0)
        )
        
        body_fat_change = None
        if (last_record.get("body_fat_percentage") and 
            first_record.get("body_fat_percentage")):
            body_fat_change = (
                last_record["body_fat_percentage"] - 
                first_record["body_fat_percentage"]
            )
        
        muscle_mass_change = None
        if (last_record.get("lean_body_mass_kg") and 
            first_record.get("lean_body_mass_kg")):
            muscle_mass_change = (
                last_record["lean_body_mass_kg"] - 
                first_record["lean_body_mass_kg"]
            )
        
        # Determine trend direction
        if abs(weight_change) < 0.5:
            trend = "stable"
        elif weight_change > 0:
            trend = "increasing" 
        else:
            trend = "decreasing"
            
        return BodyCompositionTrend(
            weight_change_kg=round(weight_change, 2),
            bmi_change=round(bmi_change, 2),
            body_fat_change_percent=round(body_fat_change, 2) if body_fat_change else None,
            muscle_mass_change_kg=round(muscle_mass_change, 2) if muscle_mass_change else None,
            trend_direction=trend
        )
    
    async def _analyze_cardiovascular_health(
        self, fitness_data: List[Dict], activities: List[Dict]
    ) -> CardiovascularAnalysis:
        """Analyze cardiovascular health metrics"""
        
        # Extract resting HR data
        resting_hrs = [
            d.get("resting_heart_rate") for d in fitness_data
            if d.get("resting_heart_rate")
        ]
        avg_resting_hr = sum(resting_hrs) / len(resting_hrs) if resting_hrs else None
        
        # Extract HRV data
        hrv_values = [
            d.get("heart_rate_variability") for d in fitness_data
            if d.get("heart_rate_variability")
        ]
        avg_hrv = sum(hrv_values) / len(hrv_values) if hrv_values else None
        
        # Analyze HR zone distribution from activities
        zone_distribution = {}
        total_zone_minutes = 0
        
        for activity in activities:
            for zone in range(1, 6):  # Zones 1-5
                zone_key = f"heart_rate_zone_{zone}_minutes"
                zone_minutes = activity.get(zone_key, 0)
                zone_name = f"zone_{zone}"
                
                if zone_name not in zone_distribution:
                    zone_distribution[zone_name] = 0
                zone_distribution[zone_name] += zone_minutes
                total_zone_minutes += zone_minutes
        
        # Convert to percentages
        if total_zone_minutes > 0:
            for zone in zone_distribution:
                zone_distribution[zone] = round(
                    zone_distribution[zone] / total_zone_minutes * 100, 1
                )
        
        # Determine cardiovascular fitness trend
        fitness_trend = "stable"
        if avg_resting_hr and len(resting_hrs) >= 7:
            recent_avg = sum(resting_hrs[-7:]) / 7
            older_avg = sum(resting_hrs[:7]) / 7
            
            if recent_avg < older_avg - 2:
                fitness_trend = "improving"
            elif recent_avg > older_avg + 2:
                fitness_trend = "declining"
        
        return CardiovascularAnalysis(
            avg_resting_hr=round(avg_resting_hr, 1) if avg_resting_hr else None,
            avg_hrv=round(avg_hrv, 1) if avg_hrv else None,
            cardiovascular_fitness_trend=fitness_trend,
            zone_distribution=zone_distribution if zone_distribution else {}
        )
    
    async def _analyze_sleep_performance(
        self, fitness_data: List[Dict], activities: List[Dict]
    ) -> SleepPerformanceCorrelation:
        """Analyze correlation between sleep and performance"""
        
        sleep_data = []
        performance_data = []
        
        for record in fitness_data:
            sleep_efficiency = record.get("sleep_efficiency")
            if sleep_efficiency:
                sleep_data.append({
                    "date": record.get("date"),
                    "efficiency": sleep_efficiency,
                    "quality": min(10, sleep_efficiency * 10)  # Scale to 1-10
                })
        
        # Match activities with sleep data for correlation
        performance_on_good_sleep = []
        performance_on_poor_sleep = []
        
        for activity in activities:
            activity_date = activity.get("started_at", "")[:10]  # Extract date
            
            # Find matching sleep data
            sleep_match = next(
                (s for s in sleep_data if s["date"][:10] == activity_date), 
                None
            )
            
            if sleep_match:
                performance_score = self._calculate_activity_performance(activity)
                
                if sleep_match["efficiency"] > 0.85:  # Good sleep
                    performance_on_good_sleep.append(performance_score)
                elif sleep_match["efficiency"] < 0.70:  # Poor sleep
                    performance_on_poor_sleep.append(performance_score)
        
        # Calculate averages and correlation
        avg_sleep_efficiency = (
            sum(s["efficiency"] for s in sleep_data) / len(sleep_data)
            if sleep_data else 0
        )
        
        avg_sleep_quality = (
            sum(s["quality"] for s in sleep_data) / len(sleep_data)
            if sleep_data else 0
        )
        
        avg_good_sleep_perf = (
            sum(performance_on_good_sleep) / len(performance_on_good_sleep)
            if performance_on_good_sleep else 0
        )
        
        avg_poor_sleep_perf = (
            sum(performance_on_poor_sleep) / len(performance_on_poor_sleep)
            if performance_on_poor_sleep else 0
        )
        
        # Determine correlation strength
        if (avg_good_sleep_perf > 0 and avg_poor_sleep_perf > 0):
            performance_diff = avg_good_sleep_perf - avg_poor_sleep_perf
            if performance_diff > 2:
                correlation = "strong"
            elif performance_diff > 1:
                correlation = "moderate"
            else:
                correlation = "weak"
        else:
            correlation = "insufficient_data"
        
        return SleepPerformanceCorrelation(
            avg_sleep_efficiency=round(avg_sleep_efficiency, 3),
            sleep_quality_score=round(avg_sleep_quality, 1),
            performance_on_good_sleep=round(avg_good_sleep_perf, 1),
            performance_on_poor_sleep=round(avg_poor_sleep_perf, 1),
            correlation_strength=correlation
        )
    
    def _calculate_activity_performance(self, activity: Dict) -> float:
        """Calculate performance score for an activity (1-10 scale)"""
        
        # Base factors for performance calculation
        factors = []
        
        # Duration vs target (assuming 45 min target for most activities)
        duration = activity.get("duration_minutes", 0)
        if duration > 0:
            duration_score = min(10, duration / 45 * 10)
            factors.append(duration_score)
        
        # Heart rate efficiency (if available)
        avg_hr = activity.get("avg_heart_rate")
        max_hr = activity.get("max_heart_rate")
        if avg_hr and max_hr:
            hr_efficiency = avg_hr / max_hr
            hr_score = min(10, hr_efficiency * 15)  # Scaled scoring
            factors.append(hr_score)
        
        # User-reported ratings
        difficulty = activity.get("difficulty_rating", 5)
        enjoyment = activity.get("enjoyment_rating", 5)
        
        # Composite performance score
        performance_factors = factors + [difficulty, enjoyment]
        return sum(performance_factors) / len(performance_factors) if performance_factors else 5.0
    
    def _empty_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Return empty dashboard structure"""
        return {
            "user_id": user_id,
            "generated_at": datetime.now(),
            "error": "insufficient_data",
            "message": "Not enough fitness data available for analysis"
        }
    
    def _get_current_stats(self, fitness_data: List[Dict]) -> Dict[str, Any]:
        """Get current day statistics"""
        if not fitness_data:
            return {}
            
        latest = fitness_data[-1]
        return {
            "date": latest.get("date"),
            "steps": latest.get("steps", 0),
            "active_calories": latest.get("active_energy_burned", 0),
            "basal_calories": latest.get("basal_energy_burned", 0),
            "total_calories": (
                latest.get("active_energy_burned", 0) + 
                latest.get("basal_energy_burned", 0)
            ),
            "active_minutes": latest.get("active_minutes", 0),
            "weight_kg": latest.get("weight_kg"),
            "sleep_efficiency": latest.get("sleep_efficiency")
        }
    
    def _get_weekly_summary(self, week_data: List[Dict]) -> Dict[str, Any]:
        """Get weekly summary statistics"""
        if not week_data:
            return {}
            
        total_steps = sum(d.get("steps", 0) for d in week_data)
        total_active_cal = sum(d.get("active_energy_burned", 0) for d in week_data)
        avg_sleep_eff = sum(d.get("sleep_efficiency", 0) for d in week_data if d.get("sleep_efficiency")) / len(week_data)
        
        return {
            "total_steps": total_steps,
            "daily_avg_steps": total_steps // 7,
            "total_active_calories": round(total_active_cal, 1),
            "avg_sleep_efficiency": round(avg_sleep_eff, 3) if avg_sleep_eff else None,
            "active_days": len([d for d in week_data if d.get("active_minutes", 0) > 30])
        }
    
    def _get_monthly_summary(self, month_data: List[Dict]) -> Dict[str, Any]:
        """Get monthly summary statistics"""
        if not month_data:
            return {}
            
        days = len(month_data)
        total_steps = sum(d.get("steps", 0) for d in month_data)
        total_active_cal = sum(d.get("active_energy_burned", 0) for d in month_data)
        
        return {
            "total_steps": total_steps,
            "daily_avg_steps": total_steps // days,
            "total_active_calories": round(total_active_cal, 1),
            "active_days": len([d for d in month_data if d.get("active_minutes", 0) > 30]),
            "consistency_percentage": round(
                len([d for d in month_data if d.get("active_minutes", 0) > 30]) / days * 100, 1
            )
        }
    
    def _get_top_activities(self, activities: List[Dict]) -> List[Dict]:
        """Get top activities by frequency and performance"""
        if not activities:
            return []
            
        activity_stats = {}
        
        for activity in activities:
            activity_type = activity.get("activity_type", "unknown")
            
            if activity_type not in activity_stats:
                activity_stats[activity_type] = {
                    "type": activity_type,
                    "count": 0,
                    "total_calories": 0,
                    "total_duration": 0
                }
            
            stats = activity_stats[activity_type]
            stats["count"] += 1
            stats["total_calories"] += activity.get("calories_burned", 0)
            stats["total_duration"] += activity.get("duration_minutes", 0)
        
        # Sort by frequency and return top 5
        sorted_activities = sorted(
            activity_stats.values(), 
            key=lambda x: x["count"], 
            reverse=True
        )
        
        return sorted_activities[:5]
    
    def _calculate_consistency(self, activities: List[Dict]) -> Dict[str, Any]:
        """Calculate activity consistency metrics"""
        if not activities:
            return {"score": 0, "trend": "insufficient_data"}
            
        # Group activities by week
        weekly_counts = {}
        for activity in activities:
            week_start = activity.get("started_at", "")[:10]  # Simplified week grouping
            weekly_counts[week_start] = weekly_counts.get(week_start, 0) + 1
        
        if len(weekly_counts) < 2:
            return {"score": 0, "trend": "insufficient_data"}
        
        weekly_values = list(weekly_counts.values())
        avg_weekly = sum(weekly_values) / len(weekly_values)
        consistency_score = min(100, avg_weekly * 25)  # Scale to 0-100
        
        # Trend calculation
        recent_half = weekly_values[len(weekly_values)//2:]
        older_half = weekly_values[:len(weekly_values)//2]
        
        recent_avg = sum(recent_half) / len(recent_half)
        older_avg = sum(older_half) / len(older_half)
        
        if recent_avg > older_avg * 1.2:
            trend = "improving"
        elif recent_avg < older_avg * 0.8:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "score": round(consistency_score, 1),
            "trend": trend,
            "avg_weekly_activities": round(avg_weekly, 1)
        }
    
    async def _generate_recommendations(
        self,
        metabolic: MetabolicAnalysis,
        body_comp: BodyCompositionTrend, 
        cardio: CardiovascularAnalysis,
        sleep_perf: SleepPerformanceCorrelation
    ) -> List[Dict[str, str]]:
        """Generate personalized recommendations based on analytics"""
        
        recommendations = []
        
        # Metabolic recommendations
        if metabolic.metabolic_efficiency < 70:
            recommendations.append({
                "category": "metabolic",
                "priority": "high",
                "title": "Increase Active Calorie Burn",
                "description": f"Your metabolic efficiency is {metabolic.metabolic_efficiency}%. Try adding 15-20 minutes of moderate activity daily."
            })
        
        if metabolic.caloric_balance_trend == "surplus":
            recommendations.append({
                "category": "nutrition",
                "priority": "medium", 
                "title": "Caloric Balance Adjustment",
                "description": "You're in a caloric surplus. Consider reducing portion sizes or increasing activity."
            })
        
        # Cardiovascular recommendations
        if cardio.avg_resting_hr and cardio.avg_resting_hr > 80:
            recommendations.append({
                "category": "cardiovascular",
                "priority": "high",
                "title": "Focus on Cardio Fitness",
                "description": f"Your resting HR is {cardio.avg_resting_hr} bpm. Regular cardio can help lower it."
            })
        
        # Zone distribution recommendations
        if cardio.zone_distribution.get("zone_1", 0) > 60:
            recommendations.append({
                "category": "training",
                "priority": "medium",
                "title": "Increase Training Intensity",
                "description": "60%+ of your training is in low intensity. Try adding some higher intensity intervals."
            })
        
        # Sleep recommendations
        if sleep_perf.avg_sleep_efficiency < 0.80:
            recommendations.append({
                "category": "sleep",
                "priority": "high", 
                "title": "Improve Sleep Quality",
                "description": f"Your sleep efficiency is {sleep_perf.avg_sleep_efficiency:.1%}. Focus on sleep hygiene for better recovery."
            })
        
        # Body composition recommendations
        if body_comp.trend_direction == "increasing" and body_comp.weight_change_kg > 2:
            recommendations.append({
                "category": "body_composition",
                "priority": "medium",
                "title": "Weight Management",
                "description": f"You've gained {body_comp.weight_change_kg}kg. Consider adjusting nutrition and activity."
            })
        
        return recommendations[:6]  # Limit to top 6 recommendations


# Singleton instance
enhanced_analytics_service = EnhancedAnalyticsService()
