# 🏋️ GymBro Platform - Changelog

Tutte le modifiche significative al progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.3] - 2025-08-15 - 🚀 PRODUCTION DEPLOYMENT

### 🎉 **MILESTONE: First Service Live in Production!**

Il **User Management Service** è ora **operativo in produzione** su Render.com!

#### Added
- **🌐 Production Deployment**: Servizio live su https://gymbro-user-service.onrender.com
- **💰 Zero-Cost Architecture**: PostgreSQL + Web Service gratuiti ($0/mese)
- **🏥 Production Health Checks**: Endpoint `/health`, `/ping`, `/health/detailed`
- **📚 Live API Documentation**: https://gymbro-user-service.onrender.com/docs
- **🔒 Full Security Stack**: JWT authentication, CORS, input validation
- **📊 Production Monitoring**: Render dashboard integration
- **⚡ Performance Optimization**: Multi-stage Docker build (~40% faster)

#### Fixed
- **🗄️ SQLAlchemy 2.x Compatibility**: Added `text()` wrapper for raw SQL queries
- **🛡️ Middleware Issues**: Disabled TrustedHostMiddleware to prevent request hanging
- **🌐 CORS Configuration**: Property-based parsing for environment variables
- **🚪 Port Binding**: Dynamic PORT environment variable support for Render
- **🔧 Database Connection**: Proper error handling for PostgreSQL managed service

#### Technical Achievements
- **Response Time**: <550ms (production)
- **Uptime**: 100% since deployment
- **Database**: PostgreSQL managed connected and operational
- **Security**: Full JWT token validation working
- **API Validation**: Complete input validation with proper error messages

---

## [v0.1.2] - 2025-08-14 - 💰 ZERO-COST MVP

### 💰 **Zero-Cost Architecture Achievement**

#### Added
- **🧠 In-Memory Cache System**: Thread-safe cache with TTL and LRU eviction
- **📊 Cache Performance**: <1ms cache hits, 1000 keys max capacity
- **🔄 Redis-Compatible API**: Drop-in replacement for basic Redis operations
- **📈 Cache Statistics**: Built-in monitoring and metrics

#### Removed
- **🗑️ Redis Dependency**: Completely removed Redis from all services
- **💵 Monthly Costs**: Eliminated $7/mese Redis costs → $0/mese total
- **🐳 Redis Containers**: Removed from Docker Compose configurations
- **⚙️ Redis Configuration**: Removed REDIS_URL from all environment files

#### Changed
- **🏗️ Architecture**: From Redis-dependent to in-memory cache architecture
- **💾 Caching Strategy**: Thread-safe Python dictionaries with TTL support
- **🧪 Test Environment**: Updated all test fixtures for in-memory cache
- **📦 Dependencies**: Updated pyproject.toml to remove Redis packages

#### Cost Impact
- **Before**: $7/mese (Redis)
- **After**: $0/mese (In-memory cache)
- **Savings**: 100% cost reduction for MVP phase

---

## [v0.1.1] - 2025-08-14 - 🚀 CI/CD PIPELINE

### 🚀 **CI/CD Integration & Production Ready**

#### Added
- **🐳 GitHub Container Registry**: Automatic Docker image builds
- **🔄 GitHub Actions CI/CD**: Complete pipeline con test automatici
- **📊 Test Coverage**: 14/14 test passanti, target 80% coverage
- **🛡️ Security Scanning**: Trivy vulnerability detection
- **📦 Multi-Service Build**: Support per 8 microservizi
- **🏥 Health Check Integration**: Automated health monitoring

#### Changed
- **📝 GitHub Actions v4**: Aggiornate tutte le azioni deprecate
- **🐳 Docker Strategy**: Multi-stage builds per performance
- **🔧 Poetry Migration**: Dockerfile ottimizzato per Poetry
- **⚙️ Environment Setup**: Script automatizzato `setup-test-env.sh`

#### Technical Improvements
- **SQLAlchemy 2.0**: Compatibility fixes per raw queries
- **Pydantic v2**: Migrazione completa con model_config
- **Zero Deprecations**: Risolte tutte le deprecation warnings
- **Code Quality**: Black, isort, flake8, mypy integration

---

## [v0.1.0] - 2025-08-14 - 🎉 INITIAL RELEASE

### 🎉 **User Management Service Launch**

#### Added
- **👤 User Registration**: Complete user registration with validation
- **🔐 JWT Authentication**: Access token + refresh token system
- **📧 Email Validation**: Unique email constraint and format validation
- **👥 User Profiles**: Complete user profile management
- **⚙️ User Preferences**: Notification and privacy settings
- **📊 User Statistics**: BMI calculation, activity tracking
- **🔒 Password Management**: Secure password change functionality
- **🗑️ GDPR Compliance**: Account deletion with "Right to be Forgotten"
- **👑 Admin Features**: User management for admin roles

#### API Endpoints
- `POST /auth/register` - User registration with complete profile
- `POST /auth/login` - User authentication with JWT tokens
- `GET /profile` - Get current user profile
- `PUT /profile` - Update user profile
- `GET /profile/stats` - Get user statistics and metrics
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update user preferences
- `POST /auth/change-password` - Change user password
- `DELETE /account` - Delete user account (GDPR)
- `GET /admin/users` - List users (admin only)

#### Security Features
- **JWT Tokens**: Access (15 min) + Refresh (30 days)
- **Password Hashing**: bcrypt secure hashing
- **Input Validation**: Pydantic models with comprehensive validation
- **Rate Limiting**: Built-in protection against abuse
- **CORS**: Configurable cross-origin resource sharing
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

#### Data Models
- **User Profile**: Complete user information with physical metrics
- **Activity Levels**: sedentary, lightly_active, moderately_active, very_active, extra_active
- **Gender Options**: male, female, other
- **User Roles**: user, admin
- **Preferences**: Notifications, privacy, units of measurement

#### Technical Stack
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Authentication**: JWT with configurable expiration
- **Validation**: Pydantic v2 with custom validators
- **Testing**: pytest with 80% coverage target
- **Container**: Docker with multi-stage builds
- **Documentation**: Auto-generated OpenAPI/Swagger docs

---

## 🔗 Links

- **Repository**: https://github.com/giamma80/gymbro-platform
- **Production Service**: https://gymbro-user-service.onrender.com
- **Documentation**: https://gymbro-user-service.onrender.com/docs
- **Docker Images**: https://github.com/giamma80/gymbro-platform/pkgs/container/gymbro-user-management

---

*Changelog generato automaticamente - Ultimo aggiornamento: 15 Agosto 2025*
