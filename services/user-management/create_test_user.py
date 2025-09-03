#!/usr/bin/env python3
"""
🧪 Create Test User for GymBro Platform
=======================================

Crea un utente di test per l'autenticazione nella dashboard web.
"""

import asyncio
import uuid
from datetime import datetime

from auth import hash_password
from database import AsyncSessionLocal, User


async def create_test_user():
    """Crea un utente di test nel database."""
    
    test_email = "test@gymbro.com"
    test_password = "testpass123"
    
    async with AsyncSessionLocal() as session:
        try:
            # Controlla se l'utente esiste già
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == test_email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ Test user già esistente: {test_email}")
                return existing_user
            
            # Crea nuovo utente di test
            hashed_password = hash_password(test_password)
            
            test_user = User(
                id=uuid.uuid4(),
                email=test_email,
                first_name="Test",
                last_name="User", 
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,  # Pre-verificato per i test
                date_of_birth=datetime(1990, 1, 1),  # Data di nascita fissa
                gender="male",
                height_cm=175.0,
                weight_kg=70.0,
                activity_level="moderately_active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            
            print("🚀 Test user creato con successo!")
            print(f"   📧 Email: {test_email}")
            print(f"   🔐 Password: {test_password}")
            print(f"   🆔 User ID: {test_user.id}")
            
            return test_user
            
        except Exception as e:
            print(f"❌ Errore nella creazione del test user: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    print("🏋️ Creazione test user per GymBro Platform...")
    asyncio.run(create_test_user())
    print("✅ Completato!")
