# User Management Service - Database Deployment Guide

## Deployment Status: ⏳ Ready for Manual Deployment

### 🎯 Database Architecture
- **Approach**: Shared Supabase Database with dedicated schemas
- **Schema**: `user_management` (cost-effective isolation)  
- **Project**: nutrifit-user-management (Supabase Cloud)

### 📋 Deployment Steps

#### 1. Access Supabase Dashboard
1. Open https://supabase.com/dashboard
2. Navigate to project: `nutrifit-user-management`
3. Go to **SQL Editor**

#### 2. Deploy Schema
1. Copy the complete content from: `sql/001_initial_schema.sql`
2. Paste it in the SQL Editor
3. Click **Run** to execute the complete schema

#### 3. Verify Deployment
After running the schema, verify these components exist:

**Schema & Tables:**
```sql
-- Check schema creation
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'user_management';

-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'user_management';
```

**Expected Tables:**
- ✅ `user_management.users` (core identity)
- ✅ `user_management.user_profiles` (extended info)  
- ✅ `user_management.privacy_settings` (GDPR compliance)

**Custom Types:**
- ✅ `user_management.user_status` enum
- ✅ `user_management.gender_type` enum

**Views:**
- ✅ `user_management.user_service_context` (GraphQL Federation)

**Sample Data:**
- ✅ Test user: `test@nutrifit.com` / `testuser`

#### 4. Test Connection
After deployment, test the connection:

```bash
cd /Users/giamma/workspace/gymbro-platform/services/user-management
./.venv/bin/python -c "
from app.core.database import get_supabase
supabase = get_supabase()
result = supabase.table('user_management.users').select('*').execute()
print(f'✅ Found {len(result.data)} users')
"
```

### 🔄 Next Steps After Deployment

1. **Verify Schema**: Run verification queries
2. **Test Sample Data**: Confirm test user exists
3. **Update Service**: Remove items template, implement real user CRUD
4. **GraphQL Federation**: Implement user entity resolution
5. **Apply Pattern**: Extend to other microservices (meal-tracking, health-monitor)

### 💰 Cost Optimization Benefits

- **Single Database**: One Supabase project for all services
- **Schema Isolation**: Clean separation without extra costs
- **Shared Resources**: Efficient resource utilization
- **Scalability**: Easy to add new service schemas

### 🛠 Schema Details

- **Total Lines**: 242 lines of SQL
- **Features**: Full CRUD, RLS, triggers, indexes, views
- **Compliance**: GDPR privacy settings included
- **Federation Ready**: GraphQL Federation v2.3 compatible
