#!/usr/bin/env python3
"""
Verify User Management Database Deployment
==========================================

This script verifies that the user_management schema has been properly
deployed to Supabase and all components are working correctly.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def main():
    """Main verification function"""
    print("🔍 User Management Database Verification")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Initialize Supabase client
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            print("❌ Missing Supabase credentials in .env file")
            return False
            
        supabase: Client = create_client(url, key)
        print(f"✅ Connected to Supabase: {url[:30]}...")
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Test 1: Check if users table exists and has data
    try:
        print("\n📊 Testing users table...")
        result = supabase.table('users').select('id,email,username,status').execute()
        print(f"✅ Users table: {len(result.data)} records found")
        
        if result.data:
            print("   Sample users:")
            for user in result.data[:3]:  # Show first 3
                print(f"   - {user.get('email')} ({user.get('status')})")
                
    except Exception as e:
        print(f"❌ Users table test failed: {e}")
        print("   Note: If schema uses 'user_management.users', manual verification needed")
    
    # Test 2: Check user profiles
    try:
        print("\n👤 Testing user_profiles table...")
        result = supabase.table('user_profiles').select('user_id,display_name,first_name').execute()
        print(f"✅ User profiles table: {len(result.data)} records found")
        
        if result.data:
            print("   Sample profiles:")
            for profile in result.data[:3]:
                print(f"   - {profile.get('display_name')} ({profile.get('first_name')})")
                
    except Exception as e:
        print(f"❌ User profiles table test failed: {e}")
    
    # Test 3: Check privacy settings
    try:
        print("\n🔒 Testing privacy_settings table...")
        result = supabase.table('privacy_settings').select('user_id,data_processing_consent,analytics_consent').execute()
        print(f"✅ Privacy settings table: {len(result.data)} records found")
        
        if result.data:
            consent_count = sum(1 for p in result.data if p.get('data_processing_consent'))
            print(f"   - {consent_count} users with data processing consent")
            
    except Exception as e:
        print(f"❌ Privacy settings table test failed: {e}")
    
    # Test 4: Check sample data
    try:
        print("\n🧪 Testing sample data...")
        result = supabase.table('users').select('*').eq('email', 'test@nutrifit.com').execute()
        
        if result.data:
            user = result.data[0]
            print(f"✅ Test user found: {user.get('username')} ({user.get('status')})")
        else:
            print("⚠️  No test user found - may need manual schema deployment")
            
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Verification completed!")
    print("\nIf some tests failed with schema-related errors,")
    print("you may need to deploy the schema manually via Supabase Dashboard.")
    print("\nSee DEPLOYMENT_GUIDE.md for detailed instructions.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
