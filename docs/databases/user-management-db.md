# User Management Service Database Schema

**Service:** user-management  
**Database:** `nutrifit_user_management`  
**Version:** v1.0.0  
**Last Updated:** 7 settembre 2025  

## 🎯 Database Purpose

**CRITICAL INFRASTRUCTURE**: User Management Service database fornisce l'autenticazione centralizzata per tutta la piattaforma NutriFit, eliminando l'anti-pattern delle tabelle users distribuite nei microservizi.

**Core Responsibilities:**
- 🔐 **Autenticazione centralizzata** con JWT tokens
- 👤 **Gestione profili utente** unificata
- 🔑 **Social authentication** (Google, Apple, Facebook)
- 📱 **Session management** cross-device
- 🛡️ **Multi-factor authentication** e security
- 📋 **GDPR compliance** con data export/deletion
- 🔗 **Service integration** tramite user context API

---

## 📊 Database Schema Overview

### Core Tables Structure

```mermaid
erDiagram
    users ||--|| user_profiles : has
    users ||--o{ auth_credentials : has
    users ||--o{ social_auth_profiles : has
    users ||--o{ auth_sessions : has
    users ||--|| privacy_settings : has
    users ||--o{ audit_logs : generates
    
    users {
        uuid id PK "Primary key"
        string email UK "Unique email"
        string username UK "Unique username"
        enum status "active|inactive|suspended|deleted"
        timestamp email_verified_at "Email verification"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Last update"
        timestamp last_login_at "Last login"
    }
    
    user_profiles {
        uuid id PK "Primary key"
        uuid user_id FK "User reference"
        string first_name "Given name"
        string last_name "Family name"
        string display_name "Public display name"
        string avatar_url "Profile picture URL"
        date date_of_birth "Birth date"
        enum gender "male|female|other|prefer_not_to_say"
        string timezone "User timezone"
        string locale "Language/region"
        jsonb preferences "User preferences"
        timestamp created_at "Profile creation"
        timestamp updated_at "Profile update"
    }
    
    auth_credentials {
        uuid id PK "Primary key"
        uuid user_id FK "User reference"
        string password_hash "Hashed password"
        string salt "Password salt"
        enum status "active|expired|disabled"
        timestamp password_changed_at "Last password change"
        int failed_attempts "Failed login count"
        timestamp locked_until "Account lock expiry"
        timestamp created_at "Credential creation"
        timestamp updated_at "Credential update"
    }
    
    social_auth_profiles {
        uuid id PK "Primary key"
        uuid user_id FK "User reference"
        enum provider "google|apple|facebook"
        string provider_user_id "External user ID"
        string provider_email "Provider email"
        jsonb provider_data "Additional provider data"
        enum status "active|revoked|expired"
        timestamp connected_at "Connection time"
        timestamp last_used_at "Last usage"
        timestamp updated_at "Profile update"
    }
    
    auth_sessions {
        uuid id PK "Primary key"
        uuid user_id FK "User reference"
        string session_token "JWT session token"
        string refresh_token "JWT refresh token"
        string device_id "Device identifier"
        string device_type "mobile|web|desktop"
        string user_agent "Browser/app info"
        string ip_address "Client IP"
        string location "Geographic location"
        enum status "active|expired|revoked"
        timestamp expires_at "Session expiry"
        timestamp last_activity_at "Last activity"
        timestamp created_at "Session creation"
    }
    
    privacy_settings {
        uuid id PK "Primary key"
        uuid user_id FK "User reference"
        boolean data_processing_consent "GDPR consent"
        boolean marketing_consent "Marketing emails"
        boolean analytics_consent "Usage analytics"
        boolean profile_visibility "Public profile"
        boolean health_data_sharing "Health data consent"
        jsonb preferences "Privacy preferences"
        timestamp consent_given_at "Consent timestamp"
        timestamp updated_at "Settings update"
    }
    
    audit_logs {
        uuid id PK "Primary key"
        uuid user_id FK "User reference"
        string action "Action performed"
        string resource "Resource affected"
        jsonb data "Action details"
        string ip_address "Client IP"
        string user_agent "Client info"
        timestamp created_at "Log timestamp"
    }
```

---

## 🗄️ Database Tables Detail

### 1. users - Core User Identity

**Purpose:** Central user identity table for all NutriFit platform authentication.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    status user_status DEFAULT 'active',
    email_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT username_format CHECK (username ~* '^[a-zA-Z0-9_]{3,50}$')
);

-- Custom enum for user status
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

### 2. user_profiles - Extended User Information

**Purpose:** Detailed user profile information for personalization and app functionality.

```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(150),
    avatar_url TEXT,
    date_of_birth DATE,
    gender gender_type,
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en-US',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_profile UNIQUE(user_id),
    CONSTRAINT age_check CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '13 years')
);

-- Custom enum for gender
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');

-- Indexes
CREATE UNIQUE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_display_name ON user_profiles(display_name);
```

### 3. auth_credentials - Password Management

**Purpose:** Secure password storage and authentication attempt tracking.

```sql
CREATE TABLE auth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    status credential_status DEFAULT 'active',
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_credentials UNIQUE(user_id),
    CONSTRAINT failed_attempts_check CHECK (failed_attempts >= 0 AND failed_attempts <= 10)
);

-- Custom enum for credential status
CREATE TYPE credential_status AS ENUM ('active', 'expired', 'disabled');

-- Indexes
CREATE UNIQUE INDEX idx_auth_credentials_user_id ON auth_credentials(user_id);
CREATE INDEX idx_auth_credentials_status ON auth_credentials(status);
```

### 4. social_auth_profiles - OAuth Integration

**Purpose:** Social media authentication integration (Google, Apple, Facebook).

```sql
CREATE TABLE social_auth_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider auth_provider NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    provider_data JSONB DEFAULT '{}',
    status social_auth_status DEFAULT 'active',
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_provider_user UNIQUE(provider, provider_user_id),
    CONSTRAINT unique_user_provider UNIQUE(user_id, provider)
);

-- Custom enums
CREATE TYPE auth_provider AS ENUM ('google', 'apple', 'facebook');
CREATE TYPE social_auth_status AS ENUM ('active', 'revoked', 'expired');

-- Indexes
CREATE INDEX idx_social_auth_user_id ON social_auth_profiles(user_id);
CREATE INDEX idx_social_auth_provider ON social_auth_profiles(provider);
CREATE UNIQUE INDEX idx_social_auth_provider_user ON social_auth_profiles(provider, provider_user_id);
```

### 5. auth_sessions - Session Management

**Purpose:** JWT session tracking and device management for security.

```sql
CREATE TABLE auth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NOT NULL,
    device_id VARCHAR(255),
    device_type device_type_enum,
    user_agent TEXT,
    ip_address INET,
    location VARCHAR(255),
    status session_status DEFAULT 'active',
    expires_at TIMESTAMP NOT NULL,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_session_token UNIQUE(session_token),
    CONSTRAINT unique_refresh_token UNIQUE(refresh_token),
    CONSTRAINT expires_future CHECK (expires_at > created_at)
);

-- Custom enums
CREATE TYPE device_type_enum AS ENUM ('mobile', 'web', 'desktop');
CREATE TYPE session_status AS ENUM ('active', 'expired', 'revoked');

-- Indexes
CREATE INDEX idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX idx_auth_sessions_status ON auth_sessions(status);
CREATE INDEX idx_auth_sessions_expires ON auth_sessions(expires_at);
CREATE UNIQUE INDEX idx_auth_sessions_token ON auth_sessions(session_token);
```

### 6. privacy_settings - GDPR Compliance

**Purpose:** User privacy preferences and GDPR compliance tracking.

```sql
CREATE TABLE privacy_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data_processing_consent BOOLEAN DEFAULT false,
    marketing_consent BOOLEAN DEFAULT false,
    analytics_consent BOOLEAN DEFAULT false,
    profile_visibility BOOLEAN DEFAULT false,
    health_data_sharing BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}',
    consent_given_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_user_privacy UNIQUE(user_id)
);

-- Indexes
CREATE UNIQUE INDEX idx_privacy_settings_user_id ON privacy_settings(user_id);
CREATE INDEX idx_privacy_consent_given ON privacy_settings(consent_given_at);
```

### 7. audit_logs - Security Audit Trail

**Purpose:** Complete audit trail of user actions for security and compliance.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Partitioning preparation
    PARTITION BY RANGE (created_at)
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## 🔗 Cross-Service Integration

### User Context API for Microservices

**Purpose:** Provide user context to other microservices without exposing sensitive data.

```sql
-- View for service integration
CREATE VIEW user_service_context AS
SELECT 
    u.id as user_id,
    u.username,
    u.status as user_status,
    up.display_name,
    up.timezone,
    up.locale,
    up.preferences,
    ps.health_data_sharing,
    ps.analytics_consent
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN privacy_settings ps ON u.id = ps.user_id
WHERE u.status = 'active';
```

### Migration from Distributed User Tables

**Purpose:** Migrate existing user data from calorie-balance service to centralized user management.

```sql
-- Migration script template
-- 1. Export existing users from calorie-balance
-- 2. Import to user-management with proper UUID mapping
-- 3. Update calorie-balance to reference centralized users
-- 4. Remove old users table from calorie-balance

-- Example migration mapping
CREATE TABLE migration_user_mapping (
    old_calorie_balance_user_id UUID,
    new_user_management_user_id UUID,
    migrated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📈 Performance Optimization

### Database Indexes Strategy

```sql
-- Core performance indexes
CREATE INDEX CONCURRENTLY idx_users_composite ON users(status, email_verified_at);
CREATE INDEX CONCURRENTLY idx_sessions_active ON auth_sessions(user_id, status, expires_at);
CREATE INDEX CONCURRENTLY idx_audit_logs_time_user ON audit_logs(created_at, user_id);

-- Partial indexes for common queries
CREATE INDEX CONCURRENTLY idx_users_active ON users(id) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_sessions_valid ON auth_sessions(user_id) WHERE status = 'active' AND expires_at > NOW();
```

### Connection Pool Configuration

```python
# Database connection settings for high performance
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}
```

---

## 🛡️ Security Implementation

### Row Level Security (RLS)

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE privacy_settings ENABLE ROW LEVEL SECURITY;

-- RLS policies for user data access
CREATE POLICY user_access_own_data ON users
    USING (id = auth.uid());

CREATE POLICY user_profile_access ON user_profiles
    USING (user_id = auth.uid());

CREATE POLICY auth_credentials_access ON auth_credentials
    USING (user_id = auth.uid());
```

### Data Encryption

```sql
-- Sensitive data encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: Encrypt sensitive profile data
ALTER TABLE user_profiles 
ADD COLUMN encrypted_personal_data BYTEA;

-- Encryption function
CREATE OR REPLACE FUNCTION encrypt_personal_data(data TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 📊 Analytics & Monitoring

### Key Metrics Tables

```sql
-- User metrics view
CREATE VIEW user_metrics AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as new_users,
    COUNT(*) FILTER (WHERE email_verified_at IS NOT NULL) as verified_users,
    COUNT(*) FILTER (WHERE last_login_at >= NOW() - INTERVAL '30 days') as active_users
FROM users
GROUP BY DATE_TRUNC('day', created_at);

-- Authentication metrics
CREATE VIEW auth_metrics AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as total_sessions,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(EXTRACT(EPOCH FROM (COALESCE(last_activity_at, created_at) - created_at))) as avg_session_duration
FROM auth_sessions
GROUP BY DATE_TRUNC('hour', created_at);
```

---

## 🔄 Database Maintenance

### Automated Cleanup Jobs

```sql
-- Clean up expired sessions
DELETE FROM auth_sessions 
WHERE status = 'expired' 
   OR expires_at < NOW() - INTERVAL '7 days';

-- Archive old audit logs (keep 1 year)
DELETE FROM audit_logs 
WHERE created_at < NOW() - INTERVAL '1 year';

-- Clean up deleted users (after 30 days grace period)
DELETE FROM users 
WHERE status = 'deleted' 
  AND updated_at < NOW() - INTERVAL '30 days';
```

### Backup Strategy

```bash
# Daily backup with rotation
pg_dump nutrifit_user_management > backup_$(date +%Y%m%d).sql

# Weekly full backup to S3
aws s3 cp backup_$(date +%Y%m%d).sql s3://nutrifit-backups/user-management/
```

---

## 🚀 Deployment Configuration

### Supabase Setup

```sql
-- Initial database setup for Supabase
-- Run via Supabase SQL editor or migration files

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Set up database
\i 001_enums.sql
\i 002_tables.sql
\i 003_indexes.sql
\i 004_views.sql
\i 005_rls_policies.sql
```

### Environment Variables

```bash
# User Management Service configuration
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/nutrifit_user_management
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRY=3600
REFRESH_TOKEN_EXPIRY=2592000
BCRYPT_ROUNDS=12

# Social authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
FACEBOOK_APP_ID=your-facebook-app-id
```

---

**Database Status:** 🚨 **FOUNDATION COMPLETE** - Ready for implementation  
**Next Steps:** Phase 1 implementation (Basic Auth + JWT)  
**Critical Priority:** UNBLOCKS all other microservice development  
**Dependencies:** Supabase project setup, JWT secrets, OAuth credentials
