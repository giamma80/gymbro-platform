#!/usr/bin/env python3
"""
Direct asyncpg table creation for Supabase
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def create_tables_direct():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    # Convert SQLAlchemy URL to asyncpg URL
    db_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"🔗 Connecting to: {db_url[:60]}...")
    
    # Connect with statement_cache_size=0 to avoid prepared statement issues
    conn = await asyncpg.connect(db_url, statement_cache_size=0)
    
    try:
        print("🚀 Creating Calorie Balance Service tables...")
        
        # Drop existing tables if they exist (CASCADE to handle foreign keys)
        print("🗑️  Dropping existing tables...")
        await conn.execute('DROP TABLE IF EXISTS metabolic_profiles CASCADE')
        await conn.execute('DROP TABLE IF EXISTS daily_balances CASCADE') 
        await conn.execute('DROP TABLE IF EXISTS calorie_goals CASCADE')
        await conn.execute('DROP TABLE IF EXISTS users CASCADE')
        
        # Create users table (new structure with id as primary key)
        print("👤 Creating users table...")
        await conn.execute('''
            CREATE TABLE users (
                id VARCHAR(255) PRIMARY KEY,  -- Supabase user ID as primary key
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255),
                age INTEGER,
                gender VARCHAR(20),
                height_cm DECIMAL(5, 1),
                weight_kg DECIMAL(5, 1),
                activity_level VARCHAR(30),
                created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                
                CONSTRAINT chk_age CHECK (age >= 10 AND age <= 120),
                CONSTRAINT chk_height CHECK (height_cm >= 50 AND height_cm <= 300),
                CONSTRAINT chk_weight CHECK (weight_kg >= 20 AND weight_kg <= 500),
                CONSTRAINT chk_gender CHECK (gender IN ('male', 'female', 'other')),
                CONSTRAINT chk_activity CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'))
            )
        ''')
        
        # Create indexes for users
        await conn.execute('CREATE INDEX idx_users_email ON users(email)')
        await conn.execute('CREATE INDEX idx_users_active ON users(is_active)')
        
        # Create calorie_goals table
        print("🎯 Creating calorie_goals table...")
        await conn.execute('''
            CREATE TABLE calorie_goals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                goal_type VARCHAR(30) NOT NULL,
                target_calories DECIMAL(6, 1) NOT NULL,
                target_weight_kg DECIMAL(5, 1),
                weekly_weight_change_kg DECIMAL(3, 1) DEFAULT 0.0 NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                
                CONSTRAINT chk_target_calories CHECK (target_calories >= 800 AND target_calories <= 5000),
                CONSTRAINT chk_target_weight CHECK (target_weight_kg >= 20 AND target_weight_kg <= 500),
                CONSTRAINT chk_weekly_change CHECK (weekly_weight_change_kg >= -2 AND weekly_weight_change_kg <= 2),
                CONSTRAINT chk_goal_type CHECK (goal_type IN ('weight_loss', 'weight_gain', 'maintenance'))
            )
        ''')
        
        # Create indexes for calorie_goals
        await conn.execute('CREATE INDEX idx_calorie_goals_user_id ON calorie_goals(user_id)')
        await conn.execute('CREATE INDEX idx_calorie_goals_active ON calorie_goals(is_active)')
        await conn.execute('CREATE INDEX idx_calorie_goals_start_date ON calorie_goals(start_date)')
        
        # Create daily_balances table
        print("📊 Creating daily_balances table...")
        await conn.execute('''
            CREATE TABLE daily_balances (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                calories_consumed DECIMAL(6, 1) DEFAULT 0.0 NOT NULL,
                calories_burned_exercise DECIMAL(6, 1) DEFAULT 0.0 NOT NULL,
                calories_burned_bmr DECIMAL(6, 1),
                net_calories DECIMAL(6, 1) DEFAULT 0.0 NOT NULL,
                weight_kg DECIMAL(5, 1),
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                
                CONSTRAINT chk_calories_consumed CHECK (calories_consumed >= 0 AND calories_consumed <= 10000),
                CONSTRAINT chk_calories_burned_exercise CHECK (calories_burned_exercise >= 0 AND calories_burned_exercise <= 5000),
                CONSTRAINT chk_calories_burned_bmr CHECK (calories_burned_bmr >= 0 AND calories_burned_bmr <= 5000),
                CONSTRAINT chk_daily_weight CHECK (weight_kg >= 20 AND weight_kg <= 500),
                UNIQUE(user_id, date)
            )
        ''')
        
        # Create indexes for daily_balances
        await conn.execute('CREATE INDEX idx_daily_balances_user_id ON daily_balances(user_id)')
        await conn.execute('CREATE INDEX idx_daily_balances_date ON daily_balances(date)')
        await conn.execute('CREATE INDEX idx_daily_balances_user_date ON daily_balances(user_id, date)')
        
        # Create metabolic_profiles table
        print("🧮 Creating metabolic_profiles table...")
        await conn.execute('''
            CREATE TABLE metabolic_profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                bmr DECIMAL(6, 1) NOT NULL,
                tdee DECIMAL(6, 1) NOT NULL,
                calculated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                valid_until TIMESTAMPTZ NOT NULL,
                
                CONSTRAINT chk_bmr CHECK (bmr >= 800 AND bmr <= 5000),
                CONSTRAINT chk_tdee CHECK (tdee >= 800 AND tdee <= 6000)
            )
        ''')
        
        # Create indexes for metabolic_profiles
        await conn.execute('CREATE INDEX idx_metabolic_profiles_user_id ON metabolic_profiles(user_id)')
        await conn.execute('CREATE INDEX idx_metabolic_profiles_valid_until ON metabolic_profiles(valid_until)')
        
        print("✅ All tables created successfully!")
        
        # Verify tables exist
        tables = await conn.fetch('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'calorie_goals', 'daily_balances', 'metabolic_profiles')
            ORDER BY table_name
        ''')
        
        print(f"✅ Created tables: {[table['table_name'] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    
    finally:
        await conn.close()
        print("🔗 Connection closed")

if __name__ == "__main__":
    asyncio.run(create_tables_direct())
