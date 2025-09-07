# NutriFit Health Monitor Service

## Overview

Il **Health Monitor Service** centralizza la raccolta e analisi dei dati di salute da dispositivi wearable, smartphone sensors e input manuali, fornendo **real-time health tracking** con correlazioni AI-powered.

### Core Responsibilities
- 📱 **HealthKit/Google Fit Integration**: Sincronizzazione automatica da dispositivi mobile
- ⌚ **Wearable Data**: Apple Watch, Fitbit, Garmin per continuous monitoring
- 💓 **Vital Signs Tracking**: Heart rate, blood pressure, sleep patterns, stress levels
- 🏃 **Activity Monitoring**: Steps, distance, exercise sessions, calorie burn
- 📊 **Health Analytics**: Trend analysis, anomaly detection, health scoring
- 🔄 **Event Publishing**: Health data events ai servizi correlati

> **📋 [API Development Roadmap](API-roadmap.md)** - Stato sviluppo integrations e health metrics  
> **Status**: 🚧 **IN DEVELOPMENT** | **v0.1.0** | **Integration Phase**

## 🔗 Device Integration Matrix

### Mobile Platforms
- **iOS HealthKit**: Complete health data access via native APIs
- **Android Health Connect**: Unified health platform per Android ecosystem
- **Samsung Health**: Direct integration per Samsung devices
- **Manual Entry**: Backup input per users senza wearables

### Wearable Devices
- **Apple Watch**: Real-time vitals, workout detection, fall detection
- **Fitbit**: Sleep tracking, heart rate zones, activity goals
- **Garmin**: Advanced sports metrics, recovery analysis
- **Whoop**: Recovery e strain monitoring 24/7

### Medical Devices
- **Smart Scales**: Weight, BMI, body composition
- **Blood Pressure Monitors**: Automated readings con timestamp
- **Glucose Meters**: Continuous glucose monitoring (CGM)
- **Sleep Trackers**: Sleep stages, REM analysis

## Architecture

Event-Driven + Health Data Pipeline:

```
app/
├── core/              # Configuration, health data models, shared utilities
├── domain/            # Health entities, vital signs, device profiles
├── application/       # Health data ingestion, analytics, alerting
├── infrastructure/    # HealthKit/Health Connect clients, device APIs
└── api/              # REST endpoints, WebHooks per device data
```

## Domain Model

### Core Entities
- **HealthProfile**: Comprehensive user health profile con baseline metrics
- **VitalSigns**: Heart rate, blood pressure, respiratory rate measurements
- **ActivitySession**: Exercise sessions con duration, intensity, calorie burn
- **SleepData**: Sleep stages, quality score, REM/deep sleep analysis
- **DeviceReading**: Raw data from specific device con metadata

### Health Metrics
- **HeartRateZones**: Target zones per fitness goals
- **SleepQuality**: Sleep efficiency, wake episodes, total sleep time
- **ActivityLevel**: Daily activity classification (sedentary → very active)
- **StressLevel**: HRV-based stress calculation
- **RecoveryScore**: Comprehensive recovery metric

### Value Objects
- **HealthScore**: Overall health rating (0-100)
- **TrendAnalysis**: Short/medium/long term health trends
- **AnomalyDetection**: Outlier identification con severity levels
- **DeviceAccuracy**: Device-specific accuracy ratings

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### 📱 Device Integration
- `POST /api/v1/devices/register` - Register new health device 🚧
- `GET /api/v1/devices/users/{user_id}` - Get user's connected devices 🚧
- `DELETE /api/v1/devices/{device_id}` - Unregister device 🚧
- `POST /api/v1/sync/healthkit` - Sync from iOS HealthKit 🚧
- `POST /api/v1/sync/health-connect` - Sync from Android Health Connect 🚧

### 💓 Vital Signs
- `POST /api/v1/vitals/heart-rate` - Log heart rate measurement 🚧
- `POST /api/v1/vitals/blood-pressure` - Log blood pressure reading 🚧
- `GET /api/v1/vitals/users/{user_id}/latest` - Get latest vital signs 🚧
- `GET /api/v1/vitals/users/{user_id}/trends` - Vital signs trends 🚧
- `POST /api/v1/vitals/batch` - Batch vital signs upload 🚧

### 🏃 Activity Tracking
- `POST /api/v1/activity/session` - Log exercise session 🚧
- `GET /api/v1/activity/users/{user_id}/daily` - Daily activity summary 🚧
- `GET /api/v1/activity/users/{user_id}/weekly` - Weekly activity patterns 🚧
- `POST /api/v1/activity/steps` - Log step count 🚧
- `GET /api/v1/activity/users/{user_id}/goals` - Activity goals progress 🚧

### 😴 Sleep Monitoring
- `POST /api/v1/sleep/session` - Log sleep session 🚧
- `GET /api/v1/sleep/users/{user_id}/latest` - Latest sleep data 🚧
- `GET /api/v1/sleep/users/{user_id}/quality` - Sleep quality trends 🚧
- `POST /api/v1/sleep/stages` - Log detailed sleep stages 🚧

### 📊 Health Analytics
- `GET /api/v1/analytics/users/{user_id}/health-score` - Overall health score 🚧
- `GET /api/v1/analytics/users/{user_id}/trends` - Comprehensive health trends 🚧
- `GET /api/v1/analytics/users/{user_id}/anomalies` - Health anomaly detection 🚧
- `GET /api/v1/analytics/users/{user_id}/correlations` - Health data correlations 🚧
- `GET /api/v1/analytics/users/{user_id}/recovery` - Recovery analysis 🚧

### 🔔 Health Alerts
- `GET /api/v1/alerts/users/{user_id}` - Get health alerts 🚧
- `POST /api/v1/alerts/thresholds` - Set health thresholds 🚧
- `PUT /api/v1/alerts/{alert_id}/acknowledge` - Acknowledge alert 🚧

### 🔄 Integration Events
- `POST /api/v1/events/calorie-burned` - Send calorie burn to balance service 🚧
- `POST /api/v1/events/activity-completed` - Activity completion event 🚧
- `GET /api/v1/events/status` - Check integration status 🚧

## Database Schema

### Core Tables (Planned)
- **`health_profiles`** - User health baselines e goals
- **`vital_signs`** - Heart rate, blood pressure, respiratory measurements
- **`activity_sessions`** - Exercise sessions con GPS data
- **`sleep_data`** - Sleep tracking con stages breakdown
- **`device_readings`** - Raw device data con device metadata
- **`health_alerts`** - Active health alerts e thresholds
- **`data_sync_logs`** - Device synchronization tracking

### Analytics Views (Planned)
- **`daily_health_summary`** - Aggregazioni giornaliere health metrics
- **`weekly_activity_patterns`** - Activity patterns e trends
- **`sleep_quality_trends`** - Sleep quality analysis
- **`health_score_history`** - Historical health score calculations
- **`anomaly_detection_log`** - Health anomalies con severity

## External Integrations

### 📱 Mobile Health Platforms
- **iOS HealthKit**: Comprehensive health data via native APIs
- **Android Health Connect**: Cross-app health data sharing
- **Samsung Health SDK**: Direct Samsung device integration
- **Huawei Health**: Huawei ecosystem health data

### ⌚ Wearable APIs
- **Apple Watch HealthKit**: Real-time workout e vital signs
- **Fitbit Web API**: Sleep, activity, heart rate data
- **Garmin Connect IQ**: Advanced sports e recovery metrics
- **Polar API**: Training load e recovery analysis

### 🏥 Medical Device Integration
- **Withings API**: Smart scales, blood pressure monitors
- **Omron Connect**: Blood pressure e body composition
- **Dexcom API**: Continuous glucose monitoring
- **CPAP Devices**: Sleep apnea monitoring integration

### 🔄 Microservices Integration
- **Calorie Balance Service**: Activity-based calorie burn events
- **AI Coach Service**: Health data for coaching insights
- **Meal Tracking Service**: Nutrition impact on health metrics
- **Notifications Service**: Health alerts e reminders

## Development Roadmap

### Phase 1: Foundation (Current)
- [ ] Setup service structure con health data models
- [ ] Database schema per vital signs e activity tracking
- [ ] Basic REST API skeleton
- [ ] Manual health data entry endpoints

### Phase 2: Device Integration
- [ ] iOS HealthKit integration
- [ ] Android Health Connect setup
- [ ] Wearable device API integrations
- [ ] Real-time data synchronization

### Phase 3: Analytics Engine
- [ ] Health trend analysis algorithms
- [ ] Anomaly detection system
- [ ] Health scoring calculation
- [ ] Predictive health insights

### Phase 4: Advanced Features
- [ ] AI-powered health coaching
- [ ] Personalized health recommendations
- [ ] Health risk assessment
- [ ] Integration con medical providers

## Security & Privacy

### Data Protection
- **HIPAA Compliance**: Health data encryption e access controls
- **GDPR Compliance**: Right to data portability e deletion
- **Device Authentication**: Secure device registration e verification
- **Data Anonymization**: Personal identifiers stripped per analytics

### Privacy Controls
- **Granular Permissions**: User control over data sharing levels
- **Data Retention**: Automatic purging of old health data
- **Export Functionality**: User data export in standard formats
- **Audit Logging**: Complete audit trail per health data access

## Performance Considerations

### Real-time Processing
- **Stream Processing**: Real-time vital signs analysis
- **Batch Processing**: Bulk device data ingestion
- **Caching Strategy**: Frequently accessed health data cached
- **Event Sourcing**: Complete health timeline reconstruction

### Mobile Optimization
- **Background Sync**: Health data upload senza user interaction
- **Delta Sync**: Only changed data transmitted
- **Compression**: Efficient data transfer per mobile networks
- **Offline Support**: Local storage per poor connectivity

---

## 💊 Technology Stack

**Core**: FastAPI + SQLAlchemy + Supabase + Redis  
**Health APIs**: HealthKit + Health Connect + Fitbit API + Garmin Connect  
**Analytics**: Pandas + NumPy + scikit-learn per health insights  
**Real-time**: WebSockets + Server-Sent Events per live monitoring  
**Architecture**: Event-Driven + Stream Processing + Domain-Driven Design

---

**Status**: 🚧 **Integration Phase** - Device API setup e health data models  
**Next Milestone**: HealthKit integration + Basic vital signs tracking  
**Advanced Analytics**: Planned for Phase 3 development
