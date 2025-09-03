# 📈 Analytics Service

Advanced time-series fitness analytics service for the GymBro Platform.

**DUAL API ARCHITECTURE**: REST + GraphQL endpoints following standardized template.

## 🎯 Service Purpose

Provides comprehensive fitness data analytics with temporal dimensions:

- **Daily Statistics**: Granular daily fitness tracking
- **Time-Series Analytics**: Trends, comparisons, historical analysis  
- **Dashboard Generation**: Multi-timeframe performance overview
- **Trend Analysis**: Progress tracking and insights

## 🏗️ Architecture Compliance

✅ **TEMPLATE COMPLIANCE**: Follows GymBro microservice template v1.0
✅ **DUAL API**: REST endpoints + GraphQL schema  
✅ **APOLLO FEDERATION**: Ready for gateway integration
✅ **POETRY DEPENDENCIES**: Standard dependency management
✅ **DOMAIN-DRIVEN DESIGN**: Business logic separation

## 🚀 Quick Start

### Development Setup

```bash
# Install dependencies with Poetry (MANDATORY)
poetry install

# Run development server
poetry run python app/main.py
```

### Docker Deployment

```bash
# Build image
docker build -t gymbro/analytics-service .

# Run container
docker run -p 8003:8003 gymbro/analytics-service
```

## 📡 API Endpoints

### REST API (`/api/v1/analytics`)

#### Daily Statistics
- `GET /users/{user_id}/daily-stats` - Get daily statistics
- `POST /users/{user_id}/daily-stats` - Record daily statistics

#### Time Range Analytics
- `GET /users/{user_id}/stats/{time_range}` - Get aggregated stats

#### Dashboard
- `GET /users/{user_id}/dashboard` - Complete analytics dashboard

#### Trends
- `GET /users/{user_id}/trends/{metric}` - Trend analysis

### GraphQL API (`/graphql`)

```graphql
# Daily Statistics
query DailyStats($userId: String!, $timeRange: TimeRangeType) {
  dailyStats(userId: $userId, timeRange: $timeRange) {
    date
    caloriesBurned
    caloriesConsumed
    activeMinutes
    stepsCount
    isActiveDay
  }
}

# Time Range Analytics  
query TimeRangeStats($userId: String!, $timeRange: TimeRangeType!) {
  timeRangeStats(userId: $userId, timeRange: $timeRange) {
    startDate
    endDate
    totalCaloriesBurned
    avgDailyCaloriesBurned
    totalActiveMinutes
    activeDaysCount
    activityPercentage
    caloriesTrend
    weightTrend
    activityTrend
  }
}

# Complete Dashboard
query UserDashboard($userId: String!) {
  userDashboard(userId: $userId) {
    currentStreak
    currentWeightKg
    weeklyGoalProgress
    monthlyGoalProgress
    consistencyScore
    improvementScore
    
    today { totalCaloriesBurned, activeMinutes }
    thisWeek { totalCaloriesBurned, activeDaysCount }
    thisMonth { avgDailyCaloriesBurned, weightChangeKg }
  }
}
```

## 🔗 Apollo Federation Integration

### Gateway Schema Extension
```graphql
extend type User @key(fields: "id") {
  id: ID! @external
  analytics: UserAnalytics
}

type UserAnalytics {
  dashboard: UserDashboard
  dailyStats(timeRange: TimeRangeType): [DailyStatsRecord!]!
  trends(metric: String!, days: Int = 30): [DailyStatsRecord!]!
}
```

### Usage in Federated Queries
```graphql
query UserWithAnalytics($userId: ID!) {
  user(id: $userId) {
    id
    profile { name, email }
    analytics {
      dashboard {
        currentStreak
        weeklyGoalProgress
        consistencyScore
      }
    }
  }
}
```

## 📊 Data Models

### Time Range Types
- `TODAY`, `YESTERDAY`, `WEEK`, `MONTH`, `QUARTER`, `YEAR`, `ALL_TIME`

### Trend Directions  
- `UP`, `DOWN`, `STABLE`, `NO_DATA`

### Activity Intensity
- `LOW`, `MODERATE`, `HIGH`, `VERY_HIGH`

## 🧪 Testing

### Run Tests
```bash
# Full test suite with coverage
poetry run pytest

# Unit tests only
poetry run pytest tests/ -m unit

# Integration tests
poetry run pytest tests/ -m integration
```

### Coverage Requirements
- **Minimum**: 80% code coverage
- **Target**: 90% for business logic
- **Tests**: REST + GraphQL endpoints

## 🛠️ Development Tools

### Code Quality
```bash
# Format code
poetry run black app/ tests/

# Sort imports
poetry run isort app/ tests/

# Lint code
poetry run flake8 app/ tests/

# Type checking
poetry run mypy app/
```

### Pre-commit Hooks
```bash
# Install hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

## 🔧 Configuration

### Environment Variables
```bash
# Service Configuration
SERVICE_NAME=analytics-service
VERSION=0.1.0
DEBUG=false
HOST=0.0.0.0
PORT=8003

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=gymbro_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres123

# Cache (Redis)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=jwt-secret-key
JWT_ALGORITHM=HS256

# External Services
USER_MANAGEMENT_URL=http://localhost:8001
GRAPHQL_GATEWAY_URL=http://localhost:4000

# Analytics Settings
TIME_SERIES_RETENTION_DAYS=365
ANALYTICS_CACHE_TTL=3600
MAX_DASHBOARD_DAYS=90
```

## ⚡ Performance Features

- **Efficient Aggregations**: Optimized time-series calculations
- **Caching Strategy**: Redis for dashboard performance  
- **Mock Data Service**: Realistic test data generation
- **Data Quality Scoring**: Completeness and reliability metrics

## 🔮 Advanced Analytics

### Dashboard Insights
- **Current Streak**: Consecutive active days
- **Goal Progress**: Weekly/monthly target achievement
- **Performance Indicators**: Multi-dimensional fitness scoring
- **Consistency Score**: Activity regularity measurement
- **Improvement Metrics**: Week-over-week progress tracking

### Trend Calculations
- **Moving Averages**: 7-day, 30-day trend analysis
- **Percentage Changes**: Period-over-period comparisons
- **Weight Tracking**: Specialized weight trend analysis
- **Activity Patterns**: Intensity and frequency analysis

## 🚦 Status

- **Version**: 0.1.0
- **Template Compliance**: ✅ Following GymBro template v1.0
- **DUAL API**: ✅ REST + GraphQL implemented
- **Apollo Federation**: ✅ Gateway integration ready
- **Poetry Dependencies**: ✅ Standard dependency management
- **Test Coverage**: 🔄 Implementation pending
- **Database Integration**: 🔄 Mock data (production ready)

## 📋 Next Steps

1. **Database Integration**: PostgreSQL + time-series tables
2. **Real Data Integration**: Connect with User Management service
3. **Caching Layer**: Redis implementation for performance  
4. **Background Jobs**: Daily aggregation processing
5. **Advanced ML**: Predictive analytics and recommendations
6. **Test Suite**: Complete REST + GraphQL test coverage

## 🎯 Template Compliance Checklist

- ✅ Poetry dependency management (`pyproject.toml`)
- ✅ Standardized directory structure (`app/`, `tests/`, `alembic/`)
- ✅ DUAL API architecture (REST + GraphQL)
- ✅ Apollo Federation ready
- ✅ Pydantic models shared between APIs
- ✅ FastAPI with proper middleware
- ✅ Health check endpoints
- ✅ Docker configuration
- ✅ Code quality tools (black, isort, flake8, mypy)
- ✅ Comprehensive README
- 🔄 Test suite (structure ready)
- 🔄 Database models (structure ready)
