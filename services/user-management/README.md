# NutriFit User Management Service

## Overview

Il **User Management Service** è il servizio centralizzato per **autenticazione**, **autorizzazione** e **gestione profili utente** dell'intera piattaforma NutriFit, implementando **Single Sign-On (SSO)** e **centralized user data management**.

### Core Responsibilities
- 🔐 **Authentication & Authorization**: JWT + Supabase Auth integration
- 👤 **User Profile Management**: Centralized user data e preferences
- 🔑 **Session Management**: Cross-service session handling
- 📱 **Social Login**: Google, Apple, Facebook integration
- 🏥 **GDPR Compliance**: User data privacy e deletion workflows
- 🔄 **Service Integration**: User context provider per tutti i microservizi

> **🚨 CRITICAL ARCHITECTURAL SERVICE**: Tutti gli altri microservizi dipendono da questo per user management  
> **📋 [API Development Roadmap](API-roadmap.md)** - Foundation per architettura centralizzata  
> **Status**: 🚧 **CRITICAL PRIORITY** | **v0.1.0** | **Foundation Blocker**

## 🏗️ Architectural Decision Impact

### **BEFORE: Distributed User Tables**
```
❌ calorie-balance/users
❌ meal-tracking/users  
❌ health-monitor/users
❌ notifications/users
❌ ai-coach/users
```
**Problems:**
- User data inconsistency
- Complex user updates across services
- GDPR compliance nightmare
- Authentication scattered

### **AFTER: Centralized User Service**
```
✅ user-management/users (SINGLE SOURCE OF TRUTH)
✅ calorie-balance/user_profiles (domain-specific data)
✅ meal-tracking/user_preferences (service-specific data)
✅ health-monitor/user_settings (health-specific data)
✅ notifications/user_preferences (notification settings)
✅ ai-coach/user_context (coaching personalization)
```

**Benefits:**
- ✅ Single source of truth per user data
- ✅ Consistent authentication across services
- ✅ Simplified GDPR compliance
- ✅ Clean service boundaries
- ✅ Easy user migration e data portability

## Architecture

Centralized Authentication + Domain-Specific Profiles:

```
app/
├── core/              # Auth configuration, JWT handling, Supabase integration
├── domain/            # User entities, profile models, auth workflows
├── application/       # Auth use cases, profile management, GDPR workflows
├── infrastructure/    # Supabase Auth client, social providers, external services
└── api/              # Auth endpoints, profile management, service integration
```

## Domain Model

### Core Entities
- **User**: Core user identity con authentication credentials
- **UserProfile**: Extended profile information (demographics, preferences)
- **AuthSession**: Active sessions con device tracking
- **ServicePermissions**: Granular permissions per microservice access
- **DataPrivacySettings**: GDPR consent e privacy preferences

### Authentication Models
- **AuthCredentials**: Login credentials e security settings
- **SocialAuthProfile**: Social login integrations (Google, Apple, Facebook)
- **MFASettings**: Multi-factor authentication configuration
- **DeviceSession**: Device-specific session management
- **SecurityLog**: Authentication attempts e security events

### Value Objects
- **UserID**: Global user identifier (UUID)
- **AuthToken**: JWT token con claims
- **PermissionScope**: Service-specific permission levels
- **PrivacyLevel**: User data privacy granularity

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### 🔐 Authentication & Authorization
- `POST /api/v1/auth/register` - User registration 🚧
- `POST /api/v1/auth/login` - User login 🚧
- `POST /api/v1/auth/logout` - User logout 🚧
- `POST /api/v1/auth/refresh` - Refresh JWT token 🚧
- `POST /api/v1/auth/verify-email` - Email verification 🚧
- `POST /api/v1/auth/reset-password` - Password reset workflow 🚧

### 🔑 Social Authentication
- `POST /api/v1/auth/social/google` - Google OAuth login 🚧
- `POST /api/v1/auth/social/apple` - Apple Sign-In 🚧
- `POST /api/v1/auth/social/facebook` - Facebook login 🚧
- `GET /api/v1/auth/social/callback/{provider}` - OAuth callback 🚧

### 👤 User Profile Management
- `GET /api/v1/users/{user_id}` - Get user profile 🚧
- `PUT /api/v1/users/{user_id}` - Update user profile 🚧
- `DELETE /api/v1/users/{user_id}` - Delete user account (GDPR) 🚧
- `GET /api/v1/users/{user_id}/preferences` - Get user preferences 🚧
- `PUT /api/v1/users/{user_id}/preferences` - Update preferences 🚧

### 🔒 Session Management
- `GET /api/v1/sessions/users/{user_id}` - Get active sessions 🚧
- `DELETE /api/v1/sessions/{session_id}` - Terminate session 🚧
- `DELETE /api/v1/sessions/users/{user_id}/all` - Terminate all sessions 🚧
- `GET /api/v1/sessions/current` - Get current session info 🚧

### 🛡️ Security & MFA
- `POST /api/v1/security/mfa/setup` - Setup multi-factor auth 🚧
- `POST /api/v1/security/mfa/verify` - Verify MFA token 🚧
- `GET /api/v1/security/devices/users/{user_id}` - Get trusted devices 🚧
- `DELETE /api/v1/security/devices/{device_id}` - Remove trusted device 🚧

### 🏥 GDPR & Data Privacy
- `GET /api/v1/privacy/users/{user_id}/data` - Export user data 🚧
- `DELETE /api/v1/privacy/users/{user_id}/data` - Delete all user data 🚧
- `GET /api/v1/privacy/users/{user_id}/consent` - Get consent status 🚧
- `PUT /api/v1/privacy/users/{user_id}/consent` - Update consent 🚧

### 🔄 Service Integration
- `GET /api/v1/integration/users/{user_id}/context` - User context per services 🚧
- `POST /api/v1/integration/users/{user_id}/permissions` - Grant service permissions 🚧
- `GET /api/v1/integration/users/{user_id}/services` - Get connected services 🚧
- `DELETE /api/v1/integration/users/{user_id}/services/{service}` - Disconnect service 🚧

## Database Schema

### Core Tables (SINGLE SOURCE OF TRUTH)
```sql
-- Primary user identity table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3)
);

-- Extended user profile information
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    height_cm DECIMAL(5,1) CHECK (height_cm >= 50 AND height_cm <= 300),
    weight_kg DECIMAL(5,1) CHECK (weight_kg >= 20 AND weight_kg <= 500),
    activity_level VARCHAR(20) CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')),
    timezone VARCHAR(50) DEFAULT 'Europe/Rome',
    language VARCHAR(5) DEFAULT 'it-IT',
    country VARCHAR(2) DEFAULT 'IT',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Authentication credentials and security
CREATE TABLE auth_credentials (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    password_hash VARCHAR(255), -- NULL for social-only accounts
    salt VARCHAR(255),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMPTZ,
    account_locked_until TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Social authentication providers
CREATE TABLE social_auth_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('google', 'apple', 'facebook')),
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    provider_name VARCHAR(255),
    provider_avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    UNIQUE(provider, provider_user_id)
);

-- Active sessions tracking
CREATE TABLE auth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID claim
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- GDPR compliance and privacy settings
CREATE TABLE privacy_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    data_processing_consent BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    analytics_consent BOOLEAN DEFAULT TRUE,
    third_party_sharing_consent BOOLEAN DEFAULT FALSE,
    consent_given_at TIMESTAMPTZ,
    consent_ip_address INET,
    data_retention_days INTEGER DEFAULT 2555, -- 7 years
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Service-specific permissions
CREATE TABLE service_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(50) NOT NULL,
    permission_scope JSONB NOT NULL, -- {'read': true, 'write': false, 'admin': false}
    granted_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMPTZ,
    
    UNIQUE(user_id, service_name)
);
```

### Performance Indexes
```sql
-- Core user lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Authentication performance
CREATE INDEX idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX idx_auth_sessions_token_jti ON auth_sessions(token_jti);
CREATE INDEX idx_auth_sessions_expires_at ON auth_sessions(expires_at);

-- Social auth lookups
CREATE INDEX idx_social_auth_provider_user_id ON social_auth_profiles(provider, provider_user_id);
CREATE INDEX idx_social_auth_user_id ON social_auth_profiles(user_id);

-- Service permissions
CREATE INDEX idx_service_permissions_user_service ON service_permissions(user_id, service_name);
```

## 🔄 Migration Strategy from Current Architecture

### Phase 1: User Service Creation (Week 1)
1. **Create User Management Service** con schema centralizzato
2. **Setup Supabase Auth integration** con JWT handling
3. **Basic authentication endpoints** (register, login, logout)
4. **User profile management APIs**

### Phase 2: Data Migration (Week 2)
1. **Migrate existing users** da calorie-balance service
2. **Create user_profiles** per existing users con current data
3. **Update calorie-balance** per rimuovere users table
4. **Implement service integration** APIs per user context

### Phase 3: Service Integration (Week 3)
1. **Update all microservices** per usare centralized user service
2. **Implement JWT validation** in ogni microservice
3. **Remove duplicate user tables** da altri servizi
4. **Add domain-specific profile tables** se necessario

### Phase 4: Advanced Features (Week 4)
1. **Social authentication** (Google, Apple, Facebook)
2. **Multi-factor authentication**
3. **GDPR compliance workflows**
4. **Session management e security features**

## 🔗 External Integrations

### Authentication Providers
- **Supabase Auth**: Primary authentication backend
- **Google OAuth**: Google Sign-In integration
- **Apple Sign-In**: iOS native authentication
- **Facebook Login**: Social authentication option

### Security Services
- **JWT**: Token-based authentication
- **bcrypt**: Password hashing
- **TOTP**: Time-based OTP per MFA
- **Rate Limiting**: Login attempt protection

### Compliance Tools
- **GDPR Automation**: Data export e deletion workflows
- **Audit Logging**: Security event tracking
- **Privacy Compliance**: Consent management

## 🚨 Critical Implementation Notes

### **BLOCKER RESOLUTION**
Questo servizio **DEVE essere implementato PRIMA** di procedere con:
- ❌ Implementazione di altri microservizi
- ❌ Mobile app development
- ❌ Production deployment
- ❌ User onboarding workflows

### **Architectural Impact**
- **calorie-balance**: Rimuovere tabella `users`, mantenere solo domain-specific data
- **meal-tracking**: User context via User Management Service
- **health-monitor**: User authentication delegata al User Service
- **notifications**: User preferences gestite centralmente
- **ai-coach**: User profiling centralizzato

### **Data Migration Required**
1. **Export users** da calorie-balance database
2. **Import into User Management Service**
3. **Update foreign keys** in tutti i servizi
4. **Remove duplicate user tables**

## Development Roadmap

### Phase 1: Foundation (IMMEDIATE - Sprint 1)
- [ ] Setup User Management Service structure
- [ ] Database schema creation con migration scripts
- [ ] Basic authentication endpoints (register, login, logout)
- [ ] JWT token generation e validation
- [ ] Supabase Auth integration

### Phase 2: Core Features (Sprint 2)
- [ ] User profile management
- [ ] Session management
- [ ] Password reset workflows
- [ ] Email verification
- [ ] Basic GDPR endpoints

### Phase 3: Security & Integration (Sprint 3)
- [ ] Social authentication (Google, Apple)
- [ ] Multi-factor authentication
- [ ] Service integration APIs
- [ ] Cross-service user context

### Phase 4: Advanced Features (Sprint 4)
- [ ] Advanced GDPR compliance
- [ ] Security monitoring e alerting
- [ ] Admin user management
- [ ] Analytics e reporting

---

## 🔑 Technology Stack

**Core**: FastAPI + SQLAlchemy + Supabase Auth + PostgreSQL  
**Security**: JWT + bcrypt + TOTP + OAuth 2.0  
**Social Auth**: Google OAuth + Apple Sign-In + Facebook Login  
**Compliance**: GDPR automation + Audit logging  
**Architecture**: Clean Architecture + Single Responsibility + SOLID principles

---

**Status**: 🚨 **CRITICAL PRIORITY** - Must be implemented before other microservices  
**Next Milestone**: Phase 1 foundation + Basic authentication  
**Blocking**: All other microservice implementations until completion
