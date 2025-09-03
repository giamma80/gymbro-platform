#!/usr/bin/env python3
"""
🔍 Check Test User in Database
=============================
"""

import asyncio
from database import AsyncSessionLocal, User
from sqlalchemy import select, text


async def check_user():
    async with AsyncSessionLocal() as session:
        try:
            # Test database connection
            result = await session.execute(text('SELECT 1'))
            print('✅ Database connection OK')
            
            # Check if user exists
            result = await session.execute(select(User).where(User.email == 'test@gymbro.com'))
            user = result.scalar_one_or_none()
            
            if user:
                print(f'✅ User found: {user.email} - ID: {user.id}')
                print(f'   Active: {user.is_active}, Verified: {user.is_verified}')
                print(f'   Name: {user.first_name} {user.last_name}')
            else:
                print('❌ User not found in database')
                
        except Exception as e:
            print(f'❌ Error: {e}')


if __name__ == "__main__":
    asyncio.run(check_user())
