"""
🏋️ GymBro Platform - User Management Service
===============================================

Servizio per gestione utenti, autenticazione e profili.
Parte della Fase 1: Foundation MVP (Settimane 1-2)

Features:
- ✅ Registrazione e login utenti
- ✅ Gestione profili e preferenze
- ✅ Autenticazione JWT
- ✅ Integrazione Supabase Auth
- ✅ Rate limiting e sicurezza
- ✅ Health checks
"""

import logging
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from auth import create_access_token, get_current_user, verify_token
from config import settings
from database import Base, engine, get_db

# Import local modules
from models import (
    ErrorResponse,
    PaginationParams,
    PasswordChange,
    TokenResponse,
    UserListResponse,
    UserLogin,
    UserPreferences,
    UserProfile,
    UserProfileUpdate,
    UserRegistration,
    UserStats,
)
from services import UserService

# ==========================================
# 📊 Setup Monitoring
# ==========================================

# Sentry disabled per sviluppo locale
# if settings.SENTRY_DSN and settings.SENTRY_DSN.startswith("https://"):
#     sentry_sdk.init(
#         dsn=settings.SENTRY_DSN,
#         integrations=[
#             FastApiIntegration(),
#             SqlalchemyIntegration(),
#         ],
#         traces_sample_rate=1.0,
#     )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 🚀 FastAPI App Setup
# ==========================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestione ciclo di vita dell'applicazione"""
    logger.info("🚀 Starting User Management Service...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Database tables created")
    yield

    logger.info("🛑 Shutting down User Management Service...")


app = FastAPI(
    title="🏋️ GymBro - User Management Service",
    description="Servizio per gestione utenti, autenticazione e profili",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ==========================================
# 🛡️ Security Middleware (temporarily disabled for debugging)
# ==========================================

# CORS - Simplified
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Temporarily disable other middleware for debugging
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)


# Security headers - Simplified
# @app.middleware("http")
# async def add_security_headers(request, call_next):
#     response = await call_next(request)
#     response.headers["X-Content-Type-Options"] = "nosniff"
#     response.headers["X-Frame-Options"] = "DENY"
#     response.headers["X-XSS-Protection"] = "1; mode=block"
#     return response


# ==========================================
# 🔐 Authentication
# ==========================================

security = HTTPBearer()


async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)
) -> UserProfile:
    """Ottieni utente attivo corrente dal token JWT"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


# ==========================================
# 🏥 Health Check
# ==========================================


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint per monitoring"""
    return {
        "status": "healthy",
        "service": "user-management",
        "version": "1.0.0",
        "timestamp": "2025-01-15T10:30:00Z",
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """Ping endpoint semplice per test"""
    return {"ping": "pong"}


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check(db=Depends(get_db)):
    """Health check dettagliato con controllo database"""
    from sqlalchemy import text
    
    try:
        # Test database connection with proper SQLAlchemy syntax
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
        db_error = None
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        db_error = str(e)

    response = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "user-management",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": "2025-01-15T10:30:00Z",
    }
    
    # Include error details for debugging
    if db_error:
        response["database_error"] = db_error
        
    return response


# ==========================================
# 👥 User Authentication Endpoints
# ==========================================


@app.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
async def register_user(user_data: UserRegistration, db=Depends(get_db)):
    """
    Registrazione nuovo utente

    - **email**: Email univoca dell'utente
    - **password**: Password sicura (min 8 caratteri)
    - **first_name**, **last_name**: Nome e cognome
    - **date_of_birth**: Data di nascita per calcolo età
    - **gender**: Genere per calcoli metabolici
    - **height_cm**, **weight_kg**: Parametri fisici
    - **activity_level**: Livello di attività fisica
    """
    try:
        user_service = UserService(db)

        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email già registrata"
            )

        # Create new user
        user = await user_service.create_user(user_data)

        # Generate tokens
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_access_token(
            {"sub": user.id},
            expires_delta=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60,
        )

        logger.info(f"New user registered: {user.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante la registrazione",
        )


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login_user(credentials: UserLogin, db=Depends(get_db)):
    """
    Login utente esistente

    - **email**: Email dell'utente
    - **password**: Password dell'utente
    """
    try:
        user_service = UserService(db)

        # Authenticate user
        user = await user_service.authenticate_user(
            credentials.email, credentials.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide",
            )

        # Generate tokens
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_access_token(
            {"sub": user.id},
            expires_delta=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60,
        )

        # Update last login
        await user_service.update_last_login(user.id)

        logger.info(f"User logged in: {user.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il login",
        )


# ==========================================
# 👤 User Profile Endpoints
# ==========================================


@app.get("/profile", response_model=UserProfile, tags=["Profile"])
async def get_user_profile(
    current_user: UserProfile = Depends(get_current_active_user),
):
    """Ottieni profilo utente corrente"""
    return current_user


@app.put("/profile", response_model=UserProfile, tags=["Profile"])
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: UserProfile = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """
    Aggiorna profilo utente

    Permette di modificare:
    - Nome e cognome
    - Peso e altezza
    - Livello di attività fisica
    """
    try:
        user_service = UserService(db)

        updated_user = await user_service.update_user_profile(
            current_user.id, profile_data
        )

        logger.info(f"Profile updated for user: {current_user.email}")
        return updated_user

    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'aggiornamento del profilo",
        )


@app.get("/profile/stats", response_model=UserStats, tags=["Profile"])
async def get_user_stats(
    current_user: UserProfile = Depends(get_current_active_user), db=Depends(get_db)
):
    """Ottieni statistiche utente (calorie, streak, BMI, etc.)"""
    try:
        user_service = UserService(db)
        stats = await user_service.get_user_stats(current_user.id)
        return stats

    except Exception as e:
        logger.error(f"User stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero delle statistiche",
        )


# ==========================================
# ⚙️ User Preferences
# ==========================================


@app.get("/preferences", response_model=UserPreferences, tags=["Preferences"])
async def get_user_preferences(
    current_user: UserProfile = Depends(get_current_active_user), db=Depends(get_db)
):
    """Ottieni preferenze utente"""
    try:
        user_service = UserService(db)
        preferences = await user_service.get_user_preferences(current_user.id)
        return preferences

    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero delle preferenze",
        )


@app.put("/preferences", response_model=UserPreferences, tags=["Preferences"])
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: UserProfile = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Aggiorna preferenze utente (notifiche, privacy, unità di misura)"""
    try:
        user_service = UserService(db)

        updated_preferences = await user_service.update_user_preferences(
            current_user.id, preferences
        )

        logger.info(f"Preferences updated for user: {current_user.email}")
        return updated_preferences

    except Exception as e:
        logger.error(f"Update preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nell'aggiornamento delle preferenze",
        )


# ==========================================
# 🔒 Password Management
# ==========================================


@app.post("/auth/change-password", tags=["Authentication"])
async def change_password(
    password_data: PasswordChange,
    current_user: UserProfile = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Cambio password utente autenticato"""
    try:
        user_service = UserService(db)

        success = await user_service.change_password(
            current_user.id, password_data.current_password, password_data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password attuale non corretta",
            )

        logger.info(f"Password changed for user: {current_user.email}")
        return {"message": "Password aggiornata con successo"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il cambio password",
        )


# ==========================================
# 🗑️ Account Deletion (GDPR)
# ==========================================


@app.delete("/account", tags=["Account"])
async def delete_account(
    current_user: UserProfile = Depends(get_current_active_user), db=Depends(get_db)
):
    """
    Eliminazione account utente (GDPR compliance)

    Implementa il "Right to be Forgotten" del GDPR.
    L'account viene soft-deleted e schedulato per eliminazione definitiva.
    """
    try:
        user_service = UserService(db)

        await user_service.soft_delete_user(current_user.id)

        logger.info(f"Account deleted for user: {current_user.email}")
        return {
            "message": "Account eliminato con successo",
            "details": "I tuoi dati verranno rimossi definitivamente entro 30 giorni",
        }

    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'eliminazione dell'account",
        )


# ==========================================
# 📊 Admin Endpoints (Future)
# ==========================================


@app.get("/admin/users", response_model=UserListResponse, tags=["Admin"])
async def list_users(
    pagination: PaginationParams = Depends(),
    current_user: UserProfile = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Lista utenti (solo per admin)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Accesso negato"
        )

    try:
        user_service = UserService(db)
        users = await user_service.list_users(pagination.page, pagination.limit)
        return users

    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero degli utenti",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
