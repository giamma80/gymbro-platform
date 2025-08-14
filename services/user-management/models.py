from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Ruoli utente per autorizzazioni"""

    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class Gender(str, Enum):
    """Genere per calcoli metabolici"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    """Livello di attività fisica per calcolo TDEE"""

    SEDENTARY = "sedentary"  # Poco/nessun esercizio
    LIGHTLY_ACTIVE = "lightly_active"  # Esercizio leggero 1-3 giorni/settimana
    MODERATELY_ACTIVE = "moderately_active"  # Esercizio moderato 3-5 giorni/settimana
    VERY_ACTIVE = "very_active"  # Esercizio intenso 6-7 giorni/settimana
    EXTRA_ACTIVE = "extra_active"  # Esercizio molto intenso, lavoro fisico


# =====================================
# 📝 Request Models (Input)
# =====================================


class UserRegistration(BaseModel):
    """Modello per registrazione utente"""

    email: EmailStr = Field(..., description="Email utente")
    password: str = Field(..., min_length=8, description="Password (min 8 caratteri)")
    first_name: str = Field(..., min_length=1, max_length=50, description="Nome")
    last_name: str = Field(..., min_length=1, max_length=50, description="Cognome")
    date_of_birth: datetime = Field(..., description="Data di nascita")
    gender: Gender = Field(..., description="Genere")
    height_cm: float = Field(..., gt=0, le=300, description="Altezza in cm")
    weight_kg: float = Field(..., gt=0, le=500, description="Peso in kg")
    activity_level: ActivityLevel = Field(..., description="Livello di attività fisica")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mario.rossi@example.com",
                "password": "SecurePass123!",
                "first_name": "Mario",
                "last_name": "Rossi",
                "date_of_birth": "1990-01-15T00:00:00Z",
                "gender": "male",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "activity_level": "moderately_active",
            }
        }


class UserLogin(BaseModel):
    """Modello per login utente"""

    email: EmailStr = Field(..., description="Email utente")
    password: str = Field(..., description="Password")


class UserProfileUpdate(BaseModel):
    """Modello per aggiornamento profilo utente"""

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    activity_level: Optional[ActivityLevel] = None

    class Config:
        json_schema_extra = {
            "example": {"weight_kg": 72.5, "activity_level": "very_active"}
        }


class PasswordChange(BaseModel):
    """Modello per cambio password"""

    current_password: str = Field(..., description="Password attuale")
    new_password: str = Field(..., min_length=8, description="Nuova password")


# =====================================
# 📤 Response Models (Output)
# =====================================


class UserProfile(BaseModel):
    """Profilo utente pubblico (senza dati sensibili)"""

    id: str = Field(..., description="ID utente")
    email: EmailStr = Field(..., description="Email utente")
    first_name: str = Field(..., description="Nome")
    last_name: str = Field(..., description="Cognome")
    age: int = Field(..., description="Età calcolata")
    gender: Gender = Field(..., description="Genere")
    height_cm: float = Field(..., description="Altezza in cm")
    weight_kg: float = Field(..., description="Peso in kg")
    activity_level: ActivityLevel = Field(..., description="Livello di attività")
    role: UserRole = Field(..., description="Ruolo utente")
    is_premium: bool = Field(..., description="Utente premium")
    created_at: datetime = Field(..., description="Data registrazione")
    updated_at: datetime = Field(..., description="Ultimo aggiornamento")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Risposta con token di autenticazione"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo di token")
    expires_in: int = Field(..., description="Scadenza in secondi")
    user: UserProfile = Field(..., description="Profilo utente")


class UserStats(BaseModel):
    """Statistiche utente base"""

    total_calories_burned: float = Field(
        default=0, description="Calorie totali bruciate"
    )
    total_calories_consumed: float = Field(
        default=0, description="Calorie totali consumate"
    )
    days_active: int = Field(default=0, description="Giorni di attività")
    current_streak: int = Field(default=0, description="Streak giorni consecutivi")
    weight_change_kg: float = Field(default=0, description="Variazione peso (kg)")
    bmi: float = Field(..., description="Indice di massa corporea")

    class Config:
        json_schema_extra = {
            "example": {
                "total_calories_burned": 15420.5,
                "total_calories_consumed": 18650.0,
                "days_active": 45,
                "current_streak": 7,
                "weight_change_kg": -2.3,
                "bmi": 22.9,
            }
        }


# =====================================
# 🗄️ Database Models
# =====================================


class UserPreferences(BaseModel):
    """Preferenze utente per notifiche e app"""

    timezone: str = Field(default="Europe/Rome", description="Fuso orario")
    language: str = Field(default="it", description="Lingua preferita")

    # Preferenze notifiche
    push_notifications: bool = Field(default=True, description="Notifiche push")
    email_notifications: bool = Field(default=True, description="Notifiche email")
    meal_reminders: bool = Field(default=True, description="Promemoria pasti")
    workout_reminders: bool = Field(default=True, description="Promemoria allenamenti")

    # Preferenze privacy
    profile_public: bool = Field(default=False, description="Profilo pubblico")
    share_achievements: bool = Field(default=True, description="Condividi traguardi")

    # Unità di misura
    weight_unit: str = Field(default="kg", description="Unità peso (kg/lbs)")
    distance_unit: str = Field(default="km", description="Unità distanza (km/miles)")

    class Config:
        json_schema_extra = {
            "example": {
                "timezone": "Europe/Rome",
                "language": "it",
                "push_notifications": True,
                "meal_reminders": True,
                "weight_unit": "kg",
            }
        }


# =====================================
# ⚡ WebSocket Models
# =====================================


class UserStatusUpdate(BaseModel):
    """Aggiornamento status utente in real-time"""

    user_id: str
    status: str  # online, offline, active
    last_activity: datetime
    current_calories: float
    today_steps: int


# =====================================
# 🔍 Query Models
# =====================================


class UserSearchFilters(BaseModel):
    """Filtri per ricerca utenti (admin)"""

    role: Optional[UserRole] = None
    is_premium: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    age_min: Optional[int] = Field(None, ge=13)
    age_max: Optional[int] = Field(None, le=120)


class PaginationParams(BaseModel):
    """Parametri di paginazione"""

    page: int = Field(default=1, ge=1, description="Numero pagina")
    limit: int = Field(default=20, ge=1, le=100, description="Elementi per pagina")


class UserListResponse(BaseModel):
    """Risposta lista utenti paginata"""

    users: List[UserProfile]
    total: int
    page: int
    limit: int
    total_pages: int


# =====================================
# 📊 Analytics Models
# =====================================


class UserEngagementMetrics(BaseModel):
    """Metriche di engagement utente"""

    daily_logins: int = Field(default=0, description="Login giornalieri")
    session_duration_avg: float = Field(
        default=0, description="Durata media sessione (minuti)"
    )
    features_used: List[str] = Field(
        default_factory=list, description="Funzionalità utilizzate"
    )
    last_login: datetime = Field(..., description="Ultimo login")
    device_type: str = Field(default="web", description="Tipo di dispositivo")


# =====================================
# 🚨 Error Models
# =====================================


class ErrorResponse(BaseModel):
    """Modello di risposta errore standardizzato"""

    error: str = Field(..., description="Tipo di errore")
    message: str = Field(..., description="Messaggio di errore")
    details: Optional[dict] = Field(None, description="Dettagli aggiuntivi")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Email già registrata",
                "details": {"field": "email"},
                "timestamp": "2025-01-15T10:30:00Z",
            }
        }
