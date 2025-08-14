"""
🏋️ GymBro Platform - Database Configuration
===========================================

Configurazione database con SQLAlchemy async e modelli utente.
Supporta PostgreSQL con Supabase e connessioni asincrone.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from config import settings

# ==========================================
# 🗄️ Database Engine Setup
# ==========================================

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DB_ECHO,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1 hour
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# ==========================================
# 🎯 Dependency for FastAPI
# ==========================================


async def get_db() -> AsyncSession:
    """
    Dependency per ottenere una sessione database asincrona.
    Utilizzata negli endpoint FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==========================================
# 👤 User Model
# ==========================================


class User(Base):
    """
    Modello database per utenti.
    Include tutti i dati necessari per autenticazione e profilo.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Profile data
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(20), nullable=False)  # male, female, other

    # Physical attributes
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    activity_level = Column(
        String(30), nullable=False
    )  # sedentary, lightly_active, etc.

    # User role and permissions
    role = Column(String(20), default="user", nullable=False)  # user, premium, admin
    is_premium = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Authentication tracking
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # External integrations
    supabase_id = Column(String(255), unique=True, nullable=True, index=True)
    google_id = Column(String(255), unique=True, nullable=True)
    apple_id = Column(String(255), unique=True, nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def full_name(self) -> str:
        """Nome completo dell'utente"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Età calcolata dalla data di nascita"""
        today = datetime.utcnow().date()
        birth_date = self.date_of_birth.date()
        age = today.year - birth_date.year
        if today < birth_date.replace(year=today.year):
            age -= 1
        return age

    @property
    def bmi(self) -> float:
        """Calcolo BMI (Body Mass Index)"""
        height_m = self.height_cm / 100
        return round(self.weight_kg / (height_m**2), 1)

    def is_locked(self) -> bool:
        """Verifica se l'account è bloccato"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until


# ==========================================
# ⚙️ User Preferences Model
# ==========================================


class UserPreferences(Base):
    """
    Modello per preferenze utente.
    Separato dalla tabella users per flessibilità.
    """

    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Localizzazione
    timezone = Column(String(50), default="Europe/Rome", nullable=False)
    language = Column(String(10), default="it", nullable=False)

    # Notifiche
    push_notifications = Column(Boolean, default=True, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    meal_reminders = Column(Boolean, default=True, nullable=False)
    workout_reminders = Column(Boolean, default=True, nullable=False)

    # Privacy
    profile_public = Column(Boolean, default=False, nullable=False)
    share_achievements = Column(Boolean, default=True, nullable=False)

    # Unità di misura
    weight_unit = Column(String(10), default="kg", nullable=False)  # kg, lbs
    distance_unit = Column(String(10), default="km", nullable=False)  # km, miles
    temperature_unit = Column(
        String(10), default="celsius", nullable=False
    )  # celsius, fahrenheit

    # Preferenze avanzate (JSON)
    notification_schedule = Column(JSON, nullable=True)  # Orari preferiti per notifiche
    dietary_restrictions = Column(JSON, nullable=True)  # Restrizioni alimentari
    fitness_goals = Column(JSON, nullable=True)  # Obiettivi fitness

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<UserPreferences for user {self.user_id}>"


# ==========================================
# 📊 User Stats Model (Cache)
# ==========================================


class UserStatsCache(Base):
    """
    Cache per statistiche utente calcolate.
    Aggiornato periodicamente per performance.
    """

    __tablename__ = "user_stats_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)

    # Statistiche caloriche
    total_calories_burned = Column(Float, default=0, nullable=False)
    total_calories_consumed = Column(Float, default=0, nullable=False)
    avg_daily_calories_burned = Column(Float, default=0, nullable=False)
    avg_daily_calories_consumed = Column(Float, default=0, nullable=False)

    # Statistiche attività
    total_workouts = Column(Integer, default=0, nullable=False)
    total_active_days = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)

    # Statistiche peso
    initial_weight_kg = Column(Float, nullable=True)
    current_weight_kg = Column(Float, nullable=True)
    weight_change_kg = Column(Float, default=0, nullable=False)
    target_weight_kg = Column(Float, nullable=True)

    # Metriche engagement
    total_logins = Column(Integer, default=0, nullable=False)
    avg_session_duration_minutes = Column(Float, default=0, nullable=False)
    features_used = Column(JSON, nullable=True)  # Lista delle feature utilizzate

    # Timestamps
    last_calculated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<UserStatsCache for user {self.user_id}>"


# ==========================================
# 🔑 User Sessions Model
# ==========================================


class UserSession(Base):
    """
    Sessioni utente attive per tracking e sicurezza.
    """

    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Session data
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)

    # Device information
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    device_type = Column(String(50), nullable=True)  # web, mobile, tablet
    device_id = Column(String(255), nullable=True)

    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<UserSession {self.session_token[:8]}...>"

    def is_expired(self) -> bool:
        """Verifica se la sessione è scaduta"""
        return datetime.utcnow() > self.expires_at


# ==========================================
# 📝 Audit Log Model
# ==========================================


class UserAuditLog(Base):
    """
    Log di audit per tracking modifiche importanti.
    Importante per GDPR compliance e sicurezza.
    """

    __tablename__ = "user_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Action details
    action = Column(
        String(100), nullable=False
    )  # login, profile_update, password_change, etc.
    resource = Column(String(100), nullable=False)  # user, preferences, stats
    old_values = Column(JSON, nullable=True)  # Valori precedenti
    new_values = Column(JSON, nullable=True)  # Nuovi valori

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserAuditLog {self.action} for user {self.user_id}>"


# ==========================================
# 🔧 Database Utilities
# ==========================================


async def create_tables():
    """Crea tutte le tabelle nel database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Elimina tutte le tabelle (solo per development!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def check_database_connection():
    """Verifica la connessione al database"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
