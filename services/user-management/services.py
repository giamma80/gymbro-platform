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
    User,
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
    Gender,
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
        Include gestione tentativi falliti e account lock.

        Args:
            email: Email utente
            password: Password in chiaro

        Returns:
            UserProfile: Profilo utente se autenticato, None altrimenti
        """
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

        # Controlla se account è bloccato
        if user.is_locked():
            logger.warning(f"Login attempt for locked account: {email}")
            return None

        # Verifica password
        if not verify_password(password, user.hashed_password):
            # Incrementa tentativi falliti
            await self._increment_failed_login_attempts(user.id)
            logger.warning(f"Failed login attempt for user: {email}")
            return None

        # Reset tentativi falliti se login OK
        await self._reset_failed_login_attempts(user.id)

        # Log successful login
        await self._log_user_action(
            user_id=user.id, action="user_login", resource="session"
        )

        return await self._user_to_profile(user)

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
