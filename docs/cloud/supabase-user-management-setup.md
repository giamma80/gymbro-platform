# Supabase User Management Database Setup

**Service:** user-management  
**Project:** nutrifit-user-management  
**Priority:** 🚨 CRITICAL - Core Authentication  
**Date:** 7 settembre 2025  

## 🚀 Quick Setup Instructions

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com) 
2. Click "New Project"
3. Organization: Create or select your organization
4. Project name: `nutrifit-user-management`
5. Database password: Generate strong password and save securely
6. Region: Select closest to your users (e.g., `us-east-1` for US)

### Step 2: Enable Authentication
1. Go to Authentication in Supabase dashboard
2. Click "Settings" 
3. Enable Email confirmation: `Yes`
4. Enable Secure email change: `Yes`
5. Configure Site URL: `http://localhost:3000` (development)
6. Configure Redirect URLs: `http://localhost:3000/auth/callback`

### Step 3: Setup Database Schema
Copy and run this SQL in the Supabase SQL Editor:

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Custom enums
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');
CREATE TYPE credential_status AS ENUM ('active', 'expired', 'disabled');
CREATE TYPE auth_provider AS ENUM ('google', 'apple', 'facebook');
CREATE TYPE social_auth_status AS ENUM ('active', 'revoked', 'expired');
CREATE TYPE device_type_enum AS ENUM ('mobile', 'web', 'desktop');
CREATE TYPE session_status AS ENUM ('active', 'expired', 'revoked');

-- 1. Users table (core identity)
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

-- 2. User profiles table (extended info)
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

-- 3. Auth credentials table (password management)
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

-- 4. Social auth profiles table (OAuth)
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

-- 5. Auth sessions table (JWT session tracking)
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

-- 6. Privacy settings table (GDPR compliance)
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

-- 7. Audit logs table (security trail)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_last_login ON users(last_login_at);

CREATE UNIQUE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_display_name ON user_profiles(display_name);

CREATE UNIQUE INDEX idx_auth_credentials_user_id ON auth_credentials(user_id);
CREATE INDEX idx_auth_credentials_status ON auth_credentials(status);

CREATE INDEX idx_social_auth_user_id ON social_auth_profiles(user_id);
CREATE INDEX idx_social_auth_provider ON social_auth_profiles(provider);
CREATE UNIQUE INDEX idx_social_auth_provider_user ON social_auth_profiles(provider, provider_user_id);

CREATE INDEX idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX idx_auth_sessions_status ON auth_sessions(status);
CREATE INDEX idx_auth_sessions_expires ON auth_sessions(expires_at);
CREATE UNIQUE INDEX idx_auth_sessions_token ON auth_sessions(session_token);

CREATE UNIQUE INDEX idx_privacy_settings_user_id ON privacy_settings(user_id);
CREATE INDEX idx_privacy_consent_given ON privacy_settings(consent_given_at);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Service integration view (for other microservices)
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

### Step 4: Enable Row Level Security (RLS)
Run this SQL to enable security policies:

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE privacy_settings ENABLE ROW LEVEL SECURITY;

-- RLS policies for user data access
CREATE POLICY "Users can access own data" ON users
    FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can access own profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own credentials" ON auth_credentials
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own sessions" ON auth_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own privacy settings" ON privacy_settings
    FOR ALL USING (auth.uid() = user_id);

-- Service access policy for other microservices
CREATE POLICY "Service access to user context" ON user_service_context
    FOR SELECT USING (true); -- Accessible to authenticated services
```

### Step 5: Configure Social Authentication
1. Go to Authentication > Settings > Auth Providers
2. Enable and configure:

**Google OAuth:**
- Client ID: (from Google Cloud Console)
- Client Secret: (from Google Cloud Console)
- Redirect URL: `https://[project-id].supabase.co/auth/v1/callback`

**Apple Sign-In:**
- Client ID: (from Apple Developer Console)
- Client Secret: (from Apple Developer Console)
- Redirect URL: `https://[project-id].supabase.co/auth/v1/callback`

**Facebook Login:**
- App ID: (from Facebook Developers)
- App Secret: (from Facebook Developers)
- Redirect URL: `https://[project-id].supabase.co/auth/v1/callback`

### Step 6: Get Connection Details
After setup, save these values for your service configuration:

```bash
# From Supabase Dashboard > Settings > Database
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres"

# From Supabase Dashboard > Settings > API  
SUPABASE_URL="https://[PROJECT-ID].supabase.co"
SUPABASE_ANON_KEY="[ANON_KEY]"
SUPABASE_SERVICE_KEY="[SERVICE_KEY]"
```

### Step 7: Test Connection
Create a simple test to verify everything works:

```python
# test_supabase_connection.py
from supabase import create_client
import os

# Test configuration
supabase_url = "https://[PROJECT-ID].supabase.co"
supabase_key = "[ANON_KEY]"

# Create client
supabase = create_client(supabase_url, supabase_key)

# Test database connection
try:
    result = supabase.table('users').select('*').limit(1).execute()
    print("✅ Database connection successful")
    print(f"Users table exists: {len(result.data) >= 0}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Test authentication
try:
    auth_result = supabase.auth.sign_up({
        "email": "test@nutrifit.com",
        "password": "TestPassword123!"
    })
    print("✅ Authentication system working")
except Exception as e:
    print(f"❌ Authentication test failed: {e}")
```

## 🔐 Security Configuration

### Environment Variables Setup
```bash
# .env for user-management service
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres"
SUPABASE_URL="https://[PROJECT-ID].supabase.co" 
SUPABASE_ANON_KEY="[ANON_KEY]"
SUPABASE_SERVICE_KEY="[SERVICE_KEY]"

# JWT Configuration
JWT_SECRET="[STRONG_RANDOM_SECRET]"
JWT_EXPIRY=3600
REFRESH_TOKEN_EXPIRY=2592000

# Security settings  
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCK_DURATION=3600
```

### Rate Limiting
Configure in Supabase Dashboard > Settings > Database:
- Max connections: 100
- Statement timeout: 30s
- Idle in transaction timeout: 10s

## 📊 Monitoring & Alerts

### Database Metrics to Monitor
- Connection count
- Query response time  
- Error rate
- Storage usage
- Active sessions

### Authentication Metrics
- Sign-up rate
- Login success rate
- Failed authentication attempts
- Session duration
- Social auth usage

## ✅ Verification Checklist

- [ ] Supabase project created with strong password
- [ ] All 7 tables created successfully
- [ ] Indexes created for performance
- [ ] RLS policies enabled and configured
- [ ] Social authentication providers configured
- [ ] Connection tested from Python
- [ ] Environment variables documented
- [ ] Security policies reviewed
- [ ] Monitoring configured
- [ ] Backup strategy confirmed

---

**Next Steps:**
1. Update user-management service to use Supabase
2. Implement authentication endpoints
3. Test social authentication flows
4. Setup other microservice databases
5. Configure cross-service authentication

**Status:** 🚧 Ready for Implementation  
**Estimated Time:** 4-6 hours for complete setup
