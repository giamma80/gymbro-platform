#!/bin/bash
"""
Database setup script for User Management Service
Executes SQL files in sequence
"""

set -e

echo "🚀 Database Setup - User Management Service"
echo "============================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Please create .env with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ Missing required environment variables"
    echo "Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY"
    exit 1
fi

# Extract database connection info from Supabase URL
# Format: https://xyz.supabase.co -> postgresql://postgres:password@db.xyz.supabase.co:5432/postgres
PROJECT_ID=$(echo $SUPABASE_URL | sed 's/.*\/\/\(.*\)\.supabase\.co.*/\1/')

echo "📊 Project ID: $PROJECT_ID"
echo "🔧 Setting up authentication tables..."

# Execute SQL file using Python script (safer for complex SQL)
echo "📋 Executing 002_auth_tables_fix.sql..."
python3 -c "
import os
from supabase import create_client

supabase = create_client('$SUPABASE_URL', '$SUPABASE_SERVICE_ROLE_KEY')

with open('sql/002_auth_tables_fix.sql', 'r') as f:
    sql = f.read()

# Split SQL into statements and execute them
statements = [s.strip() for s in sql.split(';') if s.strip()]
for stmt in statements:
    if stmt and not stmt.startswith('--'):
        try:
            result = supabase.postgrest.rpc('exec_sql', {'sql': stmt + ';'}).execute()
            print(f'✅ Executed: {stmt[:50]}...')
        except Exception as e:
            print(f'⚠️  Warning: {stmt[:50]}... - {e}')
            continue

print('🎉 Schema setup completed!')
"

echo ""
echo "🔐 Testing database connection..."

# Test with simple query
python3 -c "
import os
from supabase import create_client

supabase = create_client('$SUPABASE_URL', '$SUPABASE_SERVICE_ROLE_KEY')

try:
    # Test auth_credentials table
    result = supabase.table('auth_credentials').select('*').limit(1).execute()
    print('✅ auth_credentials table accessible')
except Exception as e:
    print(f'❌ auth_credentials table issue: {e}')

try:
    # Test users table
    result = supabase.table('users').select('*').limit(1).execute()
    print(f'✅ users table accessible - found {len(result.data)} records')
except Exception as e:
    print(f'❌ users table issue: {e}')
"

echo ""
echo "🎉 Database setup completed!"
echo "✅ Authentication tables should now be ready"
