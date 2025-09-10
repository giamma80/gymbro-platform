#!/usr/bin/env python3
"""
Database schema update script - Execute 002_auth_tables_fix.sql
"""

import os
import sys
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def execute_sql_file(sql_file_path: str):
    """Execute SQL file on Supabase database."""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in environment variables")
        print("Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Read SQL file
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        print(f"📊 Executing SQL file: {sql_file_path}")
        print("=" * 60)
        
        # Execute SQL
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        
        if result.data:
            print("✅ SQL executed successfully!")
            print(f"Result: {result.data}")
        else:
            print("✅ SQL executed (no data returned)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error executing SQL: {str(e)}")
        return False

async def main():
    """Main execution function."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, 'sql', '002_auth_tables_fix.sql')
    
    if not os.path.exists(sql_file):
        print(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)
    
    print("🚀 Database Schema Update - 002 Auth Tables Fix")
    print("=" * 60)
    
    success = await execute_sql_file(sql_file)
    
    if success:
        print("\n🎉 Schema update completed successfully!")
        print("🔐 Authentication tables are now ready")
        sys.exit(0)
    else:
        print("\n💥 Schema update failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
