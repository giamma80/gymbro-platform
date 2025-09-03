"""
🏋️ GymBro Platform - User Service Layer
=======================================

Business logic per gestione utenti, autenticazione e profili.
Questo layer orchestra le operazioni tra database, cache e servizi esterni.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth import (
    calculate_lockout_until,
    hash_password,
    validate_password_strength,
    verify_password,
)
from config import ACTIVITY_MULTIPLIERS, DEFAULT_PREFERENCES, settings
from database import (
    DailyFitnessData,
    User,
    UserActivity,
    UserAuditLog,
)
from database import UserPreferences as UserPreferencesDB
from database import (
    UserSession,
    UserStatsCache,
)

# Local imports
from models import (
    ActivityLevel,
    FitnessHistoryResponse,
    Gender,
    UserActivityInput,
    UserFitnessDataInput,
    UserListResponse,
    UserPreferences,
    UserProfile,
    UserProfileUpdate,
    UserRegistration,
    UserRole,
    UserStats,
)

logger = logging.getLogger(__name__)


class UserService:
    """
    Servizio per gestione utenti con tutte le operazioni CRUD
    e business logic correlata.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================================
    # 👤 User Management
    # ==========================================

    async def create_user(self, user_data: UserRegistration) -> UserProfile:
        """
        Crea nuovo utente con validazioni complete.

        Args:
            user_data: Dati di registrazione utente

        Returns:
            UserProfile: Profilo utente creato

        Raises:
            ValueError: Se i dati non sono validi
        """
        # Valida password
        password_validation = validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise ValueError(
                f"Password non valida: {'; '.join(password_validation['errors'])}"
            )

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Crea utente nel database
        db_user = User(
            id=uuid.uuid4(),
            email=user_data.email.lower(),
            hashed_password=hashed_password,
            first_name=user_data.first_name.strip(),
            last_name=user_data.last_name.strip(),
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender.value,
            height_cm=user_data.height_cm,
            weight_kg=user_data.weight_kg,
            activity_level=user_data.activity_level.value,
            role=UserRole.USER.value,
            is_premium=False,
            is_active=True,
            is_verified=False,
        )

        self.db.add(db_user)
        await self.db.flush()  # Per ottenere l'ID

        # Crea preferenze default
        await self._create_default_preferences(db_user.id)

        # Crea cache statistiche
        await self._initialize_user_stats(db_user.id, user_data.weight_kg)

        # Log audit
        await self._log_user_action(
            user_id=db_user.id,
            action="user_registered",
            resource="user",
            new_values={"email": user_data.email, "role": "user"},
        )

        await self.db.commit()

        logger.info(f"User created: {user_data.email}")

        return await self._user_to_profile(db_user)

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[UserProfile]:
        """
        Autentica utente con email e password.
        Versione semplificata per risolvere il problema dei metodi helper mancanti.

        Args:
            email: Email utente
            password: Password in chiaro

        Returns:
            UserProfile: Profilo utente se autenticato, None altrimenti
        """
        try:
            # Cerca utente per email
            stmt = select(User).where(
                and_(
                    User.email == email.lower(),
                    User.deleted_at.is_(None),
                    User.is_active == True,
                )
            )
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"Login attempt for non-existent user: {email}")
                return None

            # Verifica password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Failed login attempt for user: {email}")
                return None

            logger.info(f"User authenticated successfully: {email}")
            
            # Creo il profilo prima del commit per evitare problemi greenlet  
            user_profile = UserProfile(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                age=user.age,
                gender=Gender(user.gender),
                height_cm=user.height_cm,
                weight_kg=user.weight_kg,
                activity_level=ActivityLevel(user.activity_level),
                role=UserRole(user.role),
                is_premium=user.is_premium,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

            # Aggiorna last_login
            user.last_login = datetime.utcnow()
            await self.db.commit()

            return user_profile
            
        except Exception as e:
            logger.error(f"Error in authenticate_user: {e}")
            await self.db.rollback()
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """
        Ottieni utente per ID.

        Args:
            user_id: UUID utente

        Returns:
            UserProfile: Profilo utente o None
        """
        stmt = select(User).where(
            and_(User.id == uuid.UUID(user_id), User.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        return await self._user_to_profile(user)

    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """
        Ottieni utente per email.

        Args:
            email: Email utente

        Returns:
            UserProfile: Profilo utente o None
        """
        stmt = select(User).where(
            and_(User.email == email.lower(), User.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        return await self._user_to_profile(user)

    async def update_user_profile(
        self, user_id: str, profile_data: UserProfileUpdate
    ) -> UserProfile:
        """
        Aggiorna profilo utente.

        Args:
            user_id: UUID utente
            profile_data: Nuovi dati profilo

        Returns:
            UserProfile: Profilo aggiornato
        """
        # Ottieni utente corrente
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await self.db.execute(stmt)
        user = result.scalar_one()

        # Prepara dati per audit log
        old_values = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "activity_level": user.activity_level,
        }

        # Aggiorna campi specificati
        update_data = {}
        if profile_data.first_name is not None:
            update_data["first_name"] = profile_data.first_name.strip()
        if profile_data.last_name is not None:
            update_data["last_name"] = profile_data.last_name.strip()
        if profile_data.height_cm is not None:
            update_data["height_cm"] = profile_data.height_cm
        if profile_data.weight_kg is not None:
            update_data["weight_kg"] = profile_data.weight_kg
            # Aggiorna cache stats se peso cambia
            await self._update_weight_in_stats(user_id, profile_data.weight_kg)
        if profile_data.activity_level is not None:
            update_data["activity_level"] = profile_data.activity_level.value

        if update_data:
            update_data["updated_at"] = datetime.utcnow()

            stmt = (
                update(User).where(User.id == uuid.UUID(user_id)).values(**update_data)
            )
            await self.db.execute(stmt)

            # Log audit
            await self._log_user_action(
                user_id=uuid.UUID(user_id),
                action="profile_updated",
                resource="user",
                old_values=old_values,
                new_values=update_data,
            )

            await self.db.commit()

        # Restituisci profilo aggiornato
        return await self.get_user_by_id(user_id)

    # ==========================================
    # 📊 User Statistics
    # ==========================================

    async def get_user_stats(self, user_id: str) -> UserStats:
        """
        Ottieni statistiche utente dal cache.

        Args:
            user_id: UUID utente

        Returns:
            UserStats: Statistiche utente
        """
        stmt = select(UserStatsCache).where(
            UserStatsCache.user_id == uuid.UUID(user_id)
        )
        result = await self.db.execute(stmt)
        stats_cache = result.scalar_one_or_none()

        if not stats_cache:
            # Crea cache se non esiste
            await self._initialize_user_stats(uuid.UUID(user_id), 70.0)  # peso default
            stats_cache = await self.db.execute(stmt)
            stats_cache = stats_cache.scalar_one()

        # Calcola BMI corrente
        user = await self.get_user_by_id(user_id)
        bmi = (
            user.height_cm
            and user.weight_kg
            and (user.weight_kg / ((user.height_cm / 100) ** 2))
            or 0
        )

        return UserStats(
            total_calories_burned=stats_cache.total_calories_burned,
            total_calories_consumed=stats_cache.total_calories_consumed,
            days_active=stats_cache.total_active_days,
            current_streak=stats_cache.current_streak,
            weight_change_kg=stats_cache.weight_change_kg,
            bmi=round(bmi, 1),
        )

    # ==========================================
    # ⚙️ User Preferences
    # ==========================================

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """
        Ottieni preferenze utente.

        Args:
            user_id: UUID utente

        Returns:
            UserPreferences: Preferenze utente
        """
        stmt = select(UserPreferencesDB).where(
            UserPreferencesDB.user_id == uuid.UUID(user_id)
        )
        result = await self.db.execute(stmt)
        prefs_db = result.scalar_one_or_none()

        if not prefs_db:
            # Crea preferenze default se non esistono
            prefs_db = await self._create_default_preferences(uuid.UUID(user_id))

        return UserPreferences(
            timezone=prefs_db.timezone,
            language=prefs_db.language,
            push_notifications=prefs_db.push_notifications,
            email_notifications=prefs_db.email_notifications,
            meal_reminders=prefs_db.meal_reminders,
            workout_reminders=prefs_db.workout_reminders,
            profile_public=prefs_db.profile_public,
            share_achievements=prefs_db.share_achievements,
            weight_unit=prefs_db.weight_unit,
            distance_unit=prefs_db.distance_unit,
        )

    async def update_user_preferences(
        self, user_id: str, preferences: UserPreferences
    ) -> UserPreferences:
        """
        Aggiorna preferenze utente.

        Args:
            user_id: UUID utente
            preferences: Nuove preferenze

        Returns:
            UserPreferences: Preferenze aggiornate
        """
        stmt = (
            update(UserPreferencesDB)
            .where(UserPreferencesDB.user_id == uuid.UUID(user_id))
            .values(
                timezone=preferences.timezone,
                language=preferences.language,
                push_notifications=preferences.push_notifications,
                email_notifications=preferences.email_notifications,
                meal_reminders=preferences.meal_reminders,
                workout_reminders=preferences.workout_reminders,
                profile_public=preferences.profile_public,
                share_achievements=preferences.share_achievements,
                weight_unit=preferences.weight_unit,
                distance_unit=preferences.distance_unit,
                updated_at=datetime.utcnow(),
            )
        )

        await self.db.execute(stmt)

        # Log audit
        await self._log_user_action(
            user_id=uuid.UUID(user_id),
            action="preferences_updated",
            resource="preferences",
            new_values=preferences.dict(),
        )

        await self.db.commit()

        return preferences

    # ==========================================
    # 🔒 Security Functions
    # ==========================================

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """
        Cambia password utente.

        Args:
            user_id: UUID utente
            current_password: Password attuale
            new_password: Nuova password

        Returns:
            bool: True se cambio riuscito
        """
        # Valida nuova password
        password_validation = validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            raise ValueError(
                f"Password non valida: {'; '.join(password_validation['errors'])}"
            )

        # Ottieni utente
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await self.db.execute(stmt)
        user = result.scalar_one()

        # Verifica password attuale
        if not verify_password(current_password, user.hashed_password):
            return False

        # Aggiorna password
        new_hashed = hash_password(new_password)
        stmt = (
            update(User)
            .where(User.id == uuid.UUID(user_id))
            .values(hashed_password=new_hashed, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)

        # Log audit
        await self._log_user_action(
            user_id=uuid.UUID(user_id), action="password_changed", resource="user"
        )

        await self.db.commit()

        logger.info(f"Password changed for user: {user_id}")
        return True

    async def update_last_login(self, user_id: str):
        """
        Aggiorna timestamp ultimo login.

        Args:
            user_id: UUID utente
        """
        stmt = (
            update(User)
            .where(User.id == uuid.UUID(user_id))
            .values(last_login=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def soft_delete_user(self, user_id: str):
        """
        Soft delete utente (GDPR compliance).

        Args:
            user_id: UUID utente
        """
        stmt = (
            update(User)
            .where(User.id == uuid.UUID(user_id))
            .values(deleted_at=datetime.utcnow(), is_active=False)
        )
        await self.db.execute(stmt)

        # Log audit
        await self._log_user_action(
            user_id=uuid.UUID(user_id), action="account_deleted", resource="user"
        )

        await self.db.commit()

        logger.info(f"User soft deleted: {user_id}")

    # ==========================================
    # 📋 Admin Functions
    # ==========================================

    async def list_users(self, page: int = 1, limit: int = 20) -> UserListResponse:
        """
        Lista utenti con paginazione (solo admin).

        Args:
            page: Numero pagina
            limit: Elementi per pagina

        Returns:
            UserListResponse: Lista paginata
        """
        offset = (page - 1) * limit

        # Count totale
        count_stmt = select(User).where(User.deleted_at.is_(None))
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.all())

        # Query con paginazione
        stmt = select(User).where(User.deleted_at.is_(None)).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        profiles = []
        for user in users:
            profiles.append(await self._user_to_profile(user))

        total_pages = (total + limit - 1) // limit

        return UserListResponse(
            users=profiles, total=total, page=page, limit=limit, total_pages=total_pages
        )

    # ==========================================
    # 🔧 Private Helper Methods
    # ==========================================

    async def _user_to_profile(self, user: User) -> UserProfile:
        """Converte User DB model a UserProfile response model"""
        return UserProfile(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            age=user.age,
            gender=Gender(user.gender),
            height_cm=user.height_cm,
            weight_kg=user.weight_kg,
            activity_level=ActivityLevel(user.activity_level),
            role=UserRole(user.role),
            is_premium=user.is_premium,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def _create_default_preferences(
        self, user_id: uuid.UUID
    ) -> UserPreferencesDB:
        """Crea preferenze default per nuovo utente"""
        prefs = UserPreferencesDB(user_id=user_id, **DEFAULT_PREFERENCES)
        self.db.add(prefs)
        await self.db.flush()
        return prefs

    async def _initialize_user_stats(self, user_id: uuid.UUID, initial_weight: float):
        """Inizializza cache statistiche per nuovo utente"""
        stats = UserStatsCache(
            user_id=user_id,
            initial_weight_kg=initial_weight,
            current_weight_kg=initial_weight,
        )
        self.db.add(stats)
        await self.db.flush()

    async def _update_weight_in_stats(self, user_id: str, new_weight: float):
        """Aggiorna peso nelle statistiche"""
        stmt = (
            update(UserStatsCache)
            .where(UserStatsCache.user_id == uuid.UUID(user_id))
            .values(
                current_weight_kg=new_weight,
                weight_change_kg=new_weight - UserStatsCache.initial_weight_kg,
                updated_at=datetime.utcnow(),
            )
        )
        await self.db.execute(stmt)

    async def _increment_failed_login_attempts(self, user_id: uuid.UUID):
        """Incrementa tentativi di login falliti"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one()

        new_attempts = user.failed_login_attempts + 1

        update_data = {"failed_login_attempts": new_attempts}

        # Blocca account se troppi tentativi
        if new_attempts >= 5:  # MAX_LOGIN_ATTEMPTS
            update_data["locked_until"] = calculate_lockout_until()

        stmt = update(User).where(User.id == user_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()

    async def _reset_failed_login_attempts(self, user_id: uuid.UUID):
        """Reset tentativi di login falliti"""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=0, locked_until=None)
        )
        await self.db.execute(stmt)

    async def _log_user_action(
        self,
        user_id: uuid.UUID,
        action: str,
        resource: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
    ):
        """Log azione utente per audit"""
        audit_log = UserAuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            old_values=old_values,
            new_values=new_values,
        )
        self.db.add(audit_log)
        await self.db.flush()

    # ==========================================
    # 🏃‍♀️ Fitness Data Management Methods
    # ==========================================

    async def record_daily_fitness(
        self,
        user_id: str,
        fitness_data: UserFitnessDataInput
    ) -> Dict[str, Any]:
        """Record daily fitness data for a user (HealthKit Enhanced)"""
        try:
            # Check if record exists for this user and date
            query = select(DailyFitnessData).where(
                and_(
                    DailyFitnessData.user_id == user_id,
                    DailyFitnessData.date == fitness_data.date
                )
            )
            existing_record = await self.db.execute(query)
            existing_record = existing_record.scalar_one_or_none()
            
            if existing_record:
                # Update existing record with enhanced fields
                existing_record.steps = fitness_data.steps or existing_record.steps
                existing_record.active_minutes = (
                    fitness_data.active_minutes or existing_record.active_minutes
                )
                existing_record.floors_climbed = (
                    getattr(fitness_data, 'floors_climbed', None) or 
                    existing_record.floors_climbed
                )
                existing_record.distance_km = (
                    getattr(fitness_data, 'distance_km', None) or 
                    existing_record.distance_km
                )
                
                # Enhanced calorie tracking
                existing_record.calories_active = (
                    getattr(fitness_data, 'calories_active', None) or 
                    existing_record.calories_active
                )
                existing_record.calories_basal = (
                    getattr(fitness_data, 'calories_basal', None) or 
                    existing_record.calories_basal
                )
                existing_record.calories_consumed = (
                    fitness_data.calories_consumed or existing_record.calories_consumed
                )
                # Backward compatibility
                existing_record.calories_burned = (
                    fitness_data.calories_burned or existing_record.calories_burned
                )
                
                # Body composition
                existing_record.weight_kg = (
                    fitness_data.weight_kg or existing_record.weight_kg
                )
                existing_record.body_mass_index = (
                    getattr(fitness_data, 'body_mass_index', None) or 
                    existing_record.body_mass_index
                )
                existing_record.body_fat_percentage = (
                    getattr(fitness_data, 'body_fat_percentage', None) or 
                    existing_record.body_fat_percentage
                )
                existing_record.muscle_mass_kg = (
                    getattr(fitness_data, 'muscle_mass_kg', None) or 
                    existing_record.muscle_mass_kg
                )
                
                # Cardiovascular health
                existing_record.resting_heart_rate = (
                    getattr(fitness_data, 'resting_heart_rate', None) or 
                    existing_record.resting_heart_rate
                )
                existing_record.heart_rate_variability = (
                    getattr(fitness_data, 'heart_rate_variability', None) or 
                    existing_record.heart_rate_variability
                )
                
                # Enhanced sleep tracking
                existing_record.sleep_hours_total = (
                    getattr(fitness_data, 'sleep_hours_total', None) or 
                    existing_record.sleep_hours_total
                )
                existing_record.sleep_hours_in_bed = (
                    getattr(fitness_data, 'sleep_hours_in_bed', None) or 
                    existing_record.sleep_hours_in_bed
                )
                # Backward compatibility
                existing_record.sleep_hours = (
                    fitness_data.sleep_hours or existing_record.sleep_hours
                )
                
                # Subjective metrics
                existing_record.stress_level = (
                    getattr(fitness_data, 'stress_level', None) or 
                    existing_record.stress_level
                )
                
                # Metadata
                existing_record.data_source = (
                    getattr(fitness_data, 'data_source', 'manual')
                )
                existing_record.updated_at = datetime.utcnow()
                
                await self.db.commit()
                record_to_return = existing_record
            else:
                # Create new record with enhanced fields
                new_record = DailyFitnessData(
                    user_id=user_id,
                    date=fitness_data.date,
                    steps=fitness_data.steps or 0,
                    active_minutes=fitness_data.active_minutes or 0,
                    floors_climbed=getattr(fitness_data, 'floors_climbed', 0),
                    distance_km=getattr(fitness_data, 'distance_km', 0.0),
                    
                    # Enhanced calorie tracking
                    calories_active=getattr(fitness_data, 'calories_active', 0.0),
                    calories_basal=getattr(fitness_data, 'calories_basal', 0.0),
                    calories_consumed=fitness_data.calories_consumed or 0,
                    # Backward compatibility
                    calories_burned=fitness_data.calories_burned or 0,
                    
                    # Body composition
                    weight_kg=fitness_data.weight_kg,
                    body_mass_index=getattr(fitness_data, 'body_mass_index', None),
                    body_fat_percentage=getattr(fitness_data, 'body_fat_percentage', None),
                    muscle_mass_kg=getattr(fitness_data, 'muscle_mass_kg', None),
                    
                    # Cardiovascular health
                    resting_heart_rate=getattr(fitness_data, 'resting_heart_rate', None),
                    heart_rate_variability=getattr(fitness_data, 'heart_rate_variability', None),
                    
                    # Enhanced sleep tracking
                    sleep_hours_total=getattr(fitness_data, 'sleep_hours_total', None),
                    sleep_hours_in_bed=getattr(fitness_data, 'sleep_hours_in_bed', None),
                    # Backward compatibility
                    sleep_hours=fitness_data.sleep_hours,
                    
                    # Subjective metrics
                    stress_level=getattr(fitness_data, 'stress_level', None),
                    
                    # Metadata
                    data_source=getattr(fitness_data, 'data_source', 'manual')
                )
                self.db.add(new_record)
                await self.db.commit()
                await self.db.refresh(new_record)
                record_to_return = new_record
            
            # Enhanced return data
            return {
                "user_id": str(record_to_return.user_id),
                "date": record_to_return.date,
                "data_recorded": {
                    # Activity metrics
                    "steps": record_to_return.steps,
                    "active_minutes": record_to_return.active_minutes,
                    "floors_climbed": record_to_return.floors_climbed,
                    "distance_km": record_to_return.distance_km,
                    
                    # Enhanced calorie tracking
                    "calories_active": record_to_return.calories_active,
                    "calories_basal": record_to_return.calories_basal,
                    "calories_total": record_to_return.calories_total,
                    "calories_consumed": record_to_return.calories_consumed,
                    # Legacy field
                    "calories_burned": record_to_return.calories_burned,
                    
                    # Body composition
                    "weight_kg": record_to_return.weight_kg,
                    "body_mass_index": record_to_return.body_mass_index,
                    "body_fat_percentage": record_to_return.body_fat_percentage,
                    "muscle_mass_kg": record_to_return.muscle_mass_kg,
                    
                    # Health metrics
                    "resting_heart_rate": record_to_return.resting_heart_rate,
                    "heart_rate_variability": record_to_return.heart_rate_variability,
                    
                    # Sleep analysis
                    "sleep_hours_total": record_to_return.sleep_hours_total,
                    "sleep_hours_in_bed": record_to_return.sleep_hours_in_bed,
                    "sleep_efficiency": record_to_return.sleep_efficiency,
                    # Legacy field
                    "sleep_hours": record_to_return.sleep_hours,
                    
                    # Subjective metrics
                    "energy_level": record_to_return.energy_level,
                    "mood_score": record_to_return.mood_score,
                    "stress_level": record_to_return.stress_level,
                    
                    # Metadata
                    "data_source": record_to_return.data_source,
                    "notes": record_to_return.notes
                },
                "status": "recorded",
                "created_at": record_to_return.created_at
            }
        except Exception as e:
            logger.error(f"Error recording fitness data: {e}")
            raise

    async def get_fitness_history(
        self,
        user_id: str,
        days: int
    ) -> FitnessHistoryResponse:
        """Get fitness history for specified number of days"""
        try:
            from datetime import date
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days - 1)
            
            # Query fitness data for the date range
            fitness_query = select(DailyFitnessData).where(
                and_(
                    DailyFitnessData.user_id == user_id,
                    DailyFitnessData.date >= start_date,
                    DailyFitnessData.date <= end_date
                )
            ).order_by(DailyFitnessData.date)
            
            fitness_result = await self.db.execute(fitness_query)
            fitness_records = fitness_result.scalars().all()
            
            # Query activities for the same date range
            activities_query = select(UserActivity).where(
                and_(
                    UserActivity.user_id == user_id,
                    UserActivity.started_at >= datetime.combine(
                        start_date, datetime.min.time()
                    ),
                    UserActivity.started_at <= datetime.combine(
                        end_date, datetime.max.time()
                    )
                )
            ).order_by(UserActivity.started_at)
            
            activities_result = await self.db.execute(activities_query)
            activities_records = activities_result.scalars().all()
            
            # Convert fitness data to dict format
            fitness_data = []
            for record in fitness_records:
                fitness_data.append({
                    "user_id": str(record.user_id),
                    "date": (record.date.date() if hasattr(record.date, 'date')
                             else record.date),
                    "steps": record.steps,
                    "active_minutes": record.active_minutes,
                    "calories_burned": record.calories_burned,
                    "calories_consumed": record.calories_consumed,
                    "weight_kg": record.weight_kg,
                    "sleep_hours": record.sleep_hours
                })
            
            # Convert activities to dict format
            activities = []
            for activity in activities_records:
                activities.append({
                    "id": str(activity.id),
                    "user_id": str(activity.user_id),
                    "activity_type": activity.activity_type,
                    "activity_name": activity.activity_name,
                    "started_at": activity.started_at,
                    "ended_at": activity.ended_at,
                    "duration_minutes": activity.duration_minutes,
                    "calories_burned": activity.calories_burned,
                    "distance_km": activity.distance_km,
                    "notes": activity.notes
                })
            
            return FitnessHistoryResponse(
                user_id=user_id,
                days_requested=days,
                total_records=len(fitness_data),
                fitness_data=fitness_data,
                activities=activities,
                date_range={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error getting fitness history: {e}")
            raise

    async def record_activity(
        self,
        user_id: str,
        activity: UserActivityInput
    ) -> Dict[str, Any]:
        """Record individual workout/activity (HealthKit Enhanced)"""
        try:
            # Convert date to datetime if needed for started_at
            if hasattr(activity.date, 'date'):
                # activity.date is datetime
                started_at = activity.date
            else:
                # activity.date is date, convert to datetime at start of day
                started_at = datetime.combine(activity.date, datetime.min.time())
            
            # Calculate ended_at based on duration
            ended_at = None
            if activity.duration_minutes:
                ended_at = started_at + timedelta(minutes=activity.duration_minutes)
            
            # Create new activity record with enhanced fields
            new_activity = UserActivity(
                user_id=user_id,
                activity_type=activity.activity_type,
                activity_name=activity.activity_type.capitalize(),  # Basic name
                started_at=started_at,
                ended_at=ended_at,
                duration_minutes=activity.duration_minutes,
                calories_burned=activity.calories_estimate,
                
                # Enhanced HealthKit fields (use getattr for optional fields)
                distance_km=getattr(activity, 'distance_km', None),
                steps=getattr(activity, 'steps', None),
                avg_heart_rate=getattr(activity, 'avg_heart_rate', None),
                max_heart_rate=getattr(activity, 'max_heart_rate', None),
                min_heart_rate=getattr(activity, 'min_heart_rate', None),
                
                # Environmental context
                weather_temperature=getattr(activity, 'weather_temperature', None),
                weather_humidity=getattr(activity, 'weather_humidity', None),
                location_name=getattr(activity, 'location_name', None),
                
                # Elevation data
                elevation_gain_m=getattr(activity, 'elevation_gain_m', None),
                elevation_loss_m=getattr(activity, 'elevation_loss_m', None),
                
                # Heart rate zones
                hr_zone_1_seconds=getattr(activity, 'hr_zone_1_seconds', 0),
                hr_zone_2_seconds=getattr(activity, 'hr_zone_2_seconds', 0),
                hr_zone_3_seconds=getattr(activity, 'hr_zone_3_seconds', 0),
                hr_zone_4_seconds=getattr(activity, 'hr_zone_4_seconds', 0),
                hr_zone_5_seconds=getattr(activity, 'hr_zone_5_seconds', 0),
                
                # Metadata
                data_source=getattr(activity, 'data_source', 'manual'),
                source_bundle=getattr(activity, 'source_bundle', None),
                device_type=getattr(activity, 'device_type', None),
                healthkit_uuid=getattr(activity, 'healthkit_uuid', None),
                
                # Feedback
                notes=activity.notes,
                difficulty_rating=getattr(activity, 'intensity', None),
                perceived_exertion=getattr(activity, 'perceived_exertion', None),
                
                # Structured data (JSON)
                activity_data=getattr(activity, 'activity_data', None)
            )
            
            self.db.add(new_activity)
            await self.db.commit()
            await self.db.refresh(new_activity)
            
            # Enhanced return data
            return {
                "user_id": str(new_activity.user_id),
                "activity_id": str(new_activity.id),
                "date": activity.date,
                
                # Basic activity info
                "activity_type": new_activity.activity_type,
                "activity_name": new_activity.activity_name,
                "duration_minutes": new_activity.duration_minutes,
                "calories_burned": new_activity.calories_burned,
                
                # Enhanced metrics
                "distance_km": new_activity.distance_km,
                "steps": new_activity.steps,
                "avg_heart_rate": new_activity.avg_heart_rate,
                "max_heart_rate": new_activity.max_heart_rate,
                "min_heart_rate": new_activity.min_heart_rate,
                
                # Environmental data
                "weather_temperature": new_activity.weather_temperature,
                "weather_humidity": new_activity.weather_humidity,
                "location_name": new_activity.location_name,
                
                # Elevation
                "elevation_gain_m": new_activity.elevation_gain_m,
                "elevation_loss_m": new_activity.elevation_loss_m,
                
                # Heart rate zones
                "hr_zones": {
                    "zone_1_seconds": new_activity.hr_zone_1_seconds,
                    "zone_2_seconds": new_activity.hr_zone_2_seconds,
                    "zone_3_seconds": new_activity.hr_zone_3_seconds,
                    "zone_4_seconds": new_activity.hr_zone_4_seconds,
                    "zone_5_seconds": new_activity.hr_zone_5_seconds,
                },
                
                # Metadata
                "data_source": new_activity.data_source,
                "source_bundle": new_activity.source_bundle,
                "device_type": new_activity.device_type,
                "healthkit_uuid": new_activity.healthkit_uuid,
                
                # Feedback
                "difficulty_rating": new_activity.difficulty_rating,
                "perceived_exertion": new_activity.perceived_exertion,
                "notes": new_activity.notes,
                
                "status": "recorded",
                "created_at": new_activity.created_at
            }
        except Exception as e:
            logger.error(f"Error recording activity: {e}")
            raise

    async def get_latest_fitness_data(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get latest fitness data for user"""
        try:
            # Query for the most recent fitness data
            query = select(DailyFitnessData).where(
                DailyFitnessData.user_id == user_id
            ).order_by(DailyFitnessData.date.desc()).limit(1)
            
            result = await self.db.execute(query)
            latest_record = result.scalar_one_or_none()
            
            if latest_record:
                return {
                    "user_id": str(latest_record.user_id),
                    "date": (latest_record.date.date()
                             if hasattr(latest_record.date, 'date')
                             else latest_record.date),
                    "steps": latest_record.steps,
                    "active_minutes": latest_record.active_minutes,
                    "calories_burned": latest_record.calories_burned,
                    "calories_consumed": latest_record.calories_consumed,
                    "weight_kg": latest_record.weight_kg,
                    "sleep_hours": latest_record.sleep_hours,
                    "energy_level": latest_record.energy_level,
                    "mood_score": latest_record.mood_score,
                    "notes": latest_record.notes,
                    "last_updated": latest_record.updated_at
                }
            else:
                # No data found, return None
                return None
        except Exception as e:
            logger.error(f"Error getting latest fitness data: {e}")
            raise

    # ==========================================
    # 🍎 HEALTHKIT INTEGRATION METHODS
    # ==========================================

    async def sync_healthkit_data(
        self,
        user_id: str,
        healthkit_export: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sync complete HealthKit export data for a user
        
        Args:
            user_id: User UUID
            healthkit_export: Complete HealthKit JSON export
            
        Returns:
            Sync summary with counts and status
        """
        try:
            from healthkit_mapper import HealthKitDataMapper
            from datetime import date, timedelta
            
            mapper = HealthKitDataMapper()
            
            # Validate HealthKit export
            if not mapper.validate_healthkit_export(healthkit_export):
                raise ValueError("Invalid HealthKit export format")
            
            sync_summary = {
                "user_id": user_id,
                "sync_started_at": datetime.utcnow(),
                "fitness_records_synced": 0,
                "activities_synced": 0,
                "duplicates_skipped": 0,
                "errors": []
            }
            
            # Sync daily fitness data (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            current_date = start_date
            
            while current_date <= end_date:
                try:
                    daily_data = mapper.map_daily_fitness_data(
                        healthkit_export, 
                        current_date
                    )
                    
                    # Only sync if there's meaningful data
                    if daily_data["steps"] > 0 or daily_data["calories_active"] > 0:
                        # Create UserFitnessDataInput-like object
                        fitness_input = type('FitnessInput', (), daily_data)()
                        
                        await self.record_daily_fitness(user_id, fitness_input)
                        sync_summary["fitness_records_synced"] += 1
                        
                except Exception as e:
                    sync_summary["errors"].append(f"Daily data {current_date}: {str(e)}")
                    logger.warning(f"Error syncing daily data for {current_date}: {e}")
                
                current_date += timedelta(days=1)
            
            # Sync workouts
            workouts = healthkit_export.get("workouts", [])
            for workout in workouts:
                try:
                    # Check if workout already exists (by healthkit_uuid)
                    healthkit_uuid = workout.get("uuid")
                    if healthkit_uuid:
                        existing_query = select(UserActivity).where(
                            UserActivity.healthkit_uuid == healthkit_uuid
                        )
                        existing = await self.db.execute(existing_query)
                        if existing.scalar_one_or_none():
                            sync_summary["duplicates_skipped"] += 1
                            continue
                    
                    workout_data = mapper.map_workout_data(workout)
                    
                    # Create UserActivity record
                    new_activity = UserActivity(
                        user_id=user_id,
                        **workout_data
                    )
                    
                    self.db.add(new_activity)
                    await self.db.commit()
                    await self.db.refresh(new_activity)
                    
                    sync_summary["activities_synced"] += 1
                    
                except Exception as e:
                    sync_summary["errors"].append(f"Workout sync: {str(e)}")
                    logger.warning(f"Error syncing workout: {e}")
            
            sync_summary["sync_completed_at"] = datetime.utcnow()
            sync_summary["sync_duration_seconds"] = (
                sync_summary["sync_completed_at"] - 
                sync_summary["sync_started_at"]
            ).total_seconds()
            
            # Log sync summary
            logger.info(
                f"HealthKit sync completed for user {user_id}: "
                f"{sync_summary['fitness_records_synced']} fitness records, "
                f"{sync_summary['activities_synced']} activities, "
                f"{sync_summary['duplicates_skipped']} duplicates skipped, "
                f"{len(sync_summary['errors'])} errors"
            )
            
            return sync_summary
            
        except Exception as e:
            logger.error(f"Error syncing HealthKit data: {e}")
            raise

    async def get_healthkit_sync_status(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get HealthKit sync status and data summary for a user
        
        Args:
            user_id: User UUID
            
        Returns:
            Sync status and data summary
        """
        try:
            # Count HealthKit-sourced records
            fitness_query = select(DailyFitnessData).where(
                and_(
                    DailyFitnessData.user_id == user_id,
                    DailyFitnessData.data_source == "healthkit"
                )
            )
            fitness_records = await self.db.execute(fitness_query)
            healthkit_fitness_count = len(fitness_records.scalars().all())
            
            activities_query = select(UserActivity).where(
                and_(
                    UserActivity.user_id == user_id,
                    UserActivity.data_source == "healthkit"
                )
            )
            activity_records = await self.db.execute(activities_query)
            healthkit_activities_count = len(activity_records.scalars().all())
            
            # Get latest HealthKit sync
            latest_fitness_query = select(DailyFitnessData).where(
                and_(
                    DailyFitnessData.user_id == user_id,
                    DailyFitnessData.data_source == "healthkit"
                )
            ).order_by(DailyFitnessData.created_at.desc()).limit(1)
            
            latest_fitness = await self.db.execute(latest_fitness_query)
            latest_fitness_record = latest_fitness.scalar_one_or_none()
            
            return {
                "user_id": user_id,
                "healthkit_enabled": healthkit_fitness_count > 0 or healthkit_activities_count > 0,
                "data_summary": {
                    "fitness_records_synced": healthkit_fitness_count,
                    "activities_synced": healthkit_activities_count,
                    "total_records": healthkit_fitness_count + healthkit_activities_count
                },
                "last_sync": latest_fitness_record.created_at if latest_fitness_record else None,
                "sync_coverage": {
                    "earliest_date": None,  # Could be calculated from oldest record
                    "latest_date": latest_fitness_record.date if latest_fitness_record else None
                },
                "data_quality": {
                    "has_heart_rate_data": bool(
                        latest_fitness_record and 
                        latest_fitness_record.resting_heart_rate
                    ) if latest_fitness_record else False,
                    "has_body_composition": bool(
                        latest_fitness_record and 
                        latest_fitness_record.body_fat_percentage
                    ) if latest_fitness_record else False,
                    "has_sleep_analysis": bool(
                        latest_fitness_record and 
                        latest_fitness_record.sleep_efficiency
                    ) if latest_fitness_record else False
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting HealthKit sync status: {e}")
            raise
