"""
🏋️ GymBro Platform - Authentication Module
==========================================

Gestione autenticazione JWT, password hashing e sicurezza.
Integrato con Supabase Auth per OAuth e autenticazione esterna.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import secrets
import re
from config import (
    settings,
    PASSWORD_MIN_LENGTH,
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
)

# ==========================================
# 🔐 Password Security
# ==========================================

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password usando bcrypt.

    Args:
        password: Password in chiaro

    Returns:
        str: Password hash
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica password contro hash.

    Args:
        plain_password: Password in chiaro
        hashed_password: Password hash dal database

    Returns:
        bool: True se la password è corretta
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Valida la robustezza della password.

    Args:
        password: Password da validare

    Returns:
        dict: Risultato validazione con score e messaggi
    """
    errors = []
    score = 0

    # Lunghezza minima
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password deve essere di almeno {PASSWORD_MIN_LENGTH} caratteri")
    else:
        score += 1

    # Lettere maiuscole
    if not re.search(r"[A-Z]", password):
        errors.append("Password deve contenere almeno una lettera maiuscola")
    else:
        score += 1

    # Lettere minuscole
    if not re.search(r"[a-z]", password):
        errors.append("Password deve contenere almeno una lettera minuscola")
    else:
        score += 1

    # Numeri
    if not re.search(r"\d", password):
        errors.append("Password deve contenere almeno un numero")
    else:
        score += 1

    # Caratteri speciali
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password deve contenere almeno un carattere speciale")
    else:
        score += 1

    # Password comuni (basic check)
    common_passwords = [
        "password",
        "123456",
        "password123",
        "admin",
        "qwerty",
        "letmein",
        "welcome",
        "monkey",
        "1234567890",
    ]
    if password.lower() in common_passwords:
        errors.append("Password troppo comune, scegline una più sicura")
        score = max(0, score - 2)

    # Lunghezza bonus
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    return {
        "is_valid": len(errors) == 0,
        "score": min(score, 5),  # Max score: 5
        "strength": get_password_strength_label(score),
        "errors": errors,
    }


def get_password_strength_label(score: int) -> str:
    """Converte score in label leggibile"""
    if score <= 1:
        return "Molto Debole"
    elif score == 2:
        return "Debole"
    elif score == 3:
        return "Media"
    elif score == 4:
        return "Forte"
    else:
        return "Molto Forte"


# ==========================================
# 🔑 JWT Token Management
# ==========================================


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[int] = None
) -> str:
    """
    Crea JWT access token.

    Args:
        data: Payload del token (user_id, role, etc.)
        expires_delta: Minuti di validità (default da config)

    Returns:
        str: JWT token encoded
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Crea JWT refresh token (lunga durata).

    Args:
        data: Payload del token

    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica e decodifica JWT token.

    Args:
        token: JWT token da verificare

    Returns:
        dict: Payload decodificato

    Raises:
        HTTPException: Se il token non è valido
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

        # Verifica scadenza
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token malformato"
            )

        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token scaduto"
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token non valido: {str(e)}",
        )


def refresh_access_token(refresh_token: str) -> str:
    """
    Rinnova access token usando refresh token.

    Args:
        refresh_token: Refresh token valido

    Returns:
        str: Nuovo access token

    Raises:
        HTTPException: Se refresh token non è valido
    """
    try:
        payload = verify_token(refresh_token)

        # Verifica che sia un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token non è un refresh token",
            )

        # Crea nuovo access token
        new_token_data = {
            "sub": payload.get("sub"),
            "role": payload.get("role", "user"),
        }

        return create_access_token(new_token_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Errore nel refresh del token: {str(e)}",
        )


# ==========================================
# 🛡️ Security Utilities
# ==========================================


def generate_secure_token(length: int = 32) -> str:
    """
    Genera token sicuro per reset password, etc.

    Args:
        length: Lunghezza del token

    Returns:
        str: Token sicuro
    """
    return secrets.token_urlsafe(length)


def is_email_valid(email: str) -> bool:
    """
    Validazione base email.

    Args:
        email: Email da validare

    Returns:
        bool: True se email è valida
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None


def sanitize_user_input(input_string: str) -> str:
    """
    Sanitizza input utente per prevenire XSS.

    Args:
        input_string: String da sanitizzare

    Returns:
        str: String sanitizzata
    """
    if not input_string:
        return ""

    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", input_string)

    # Remove script content
    clean = re.sub(
        r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
        "",
        clean,
        flags=re.IGNORECASE,
    )

    # Strip whitespace
    clean = clean.strip()

    return clean


def check_rate_limit(
    user_id: str, action: str, max_attempts: int, window_minutes: int
) -> bool:
    """
    Implementazione basic rate limiting.
    In produzione usare Redis per stato distribuito.

    Args:
        user_id: ID utente
        action: Tipo di azione (login, register, etc.)
        max_attempts: Tentativi massimi
        window_minutes: Finestra temporale in minuti

    Returns:
        bool: True se sotto il limite
    """
    # TODO: Implementare con Redis in produzione
    # Per ora return True (no rate limiting)
    return True


# ==========================================
# 🔐 Account Security
# ==========================================


def should_lock_account(failed_attempts: int) -> bool:
    """
    Determina se l'account dovrebbe essere bloccato.

    Args:
        failed_attempts: Numero di tentativi falliti

    Returns:
        bool: True se dovrebbe essere bloccato
    """
    return failed_attempts >= MAX_LOGIN_ATTEMPTS


def calculate_lockout_until() -> datetime:
    """
    Calcola quando l'account sarà sbloccato.

    Returns:
        datetime: Timestamp di sblocco
    """
    return datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)


def is_account_locked(locked_until: Optional[datetime]) -> bool:
    """
    Verifica se l'account è attualmente bloccato.

    Args:
        locked_until: Timestamp di sblocco

    Returns:
        bool: True se bloccato
    """
    if locked_until is None:
        return False
    return datetime.utcnow() < locked_until


# ==========================================
# 🌐 OAuth Integration (Supabase)
# ==========================================


def validate_oauth_token(provider: str, token: str) -> Optional[Dict[str, Any]]:
    """
    Valida token OAuth da provider esterno.

    Args:
        provider: Provider OAuth (google, apple, etc.)
        token: Token da validare

    Returns:
        dict: Dati utente dal provider o None se non valido
    """
    # TODO: Implementare validazione specifica per provider
    # Per Supabase, questo sarà gestito dal loro SDK
    return None


def extract_user_info_from_oauth(
    provider: str, user_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Estrae informazioni utente standardizzate da dati OAuth.

    Args:
        provider: Provider OAuth
        user_data: Dati grezzi dal provider

    Returns:
        dict: Dati utente standardizzati
    """
    standardized = {
        "email": "",
        "first_name": "",
        "last_name": "",
        "avatar_url": "",
        "is_verified": False,
    }

    if provider == "google":
        standardized.update(
            {
                "email": user_data.get("email", ""),
                "first_name": user_data.get("given_name", ""),
                "last_name": user_data.get("family_name", ""),
                "avatar_url": user_data.get("picture", ""),
                "is_verified": user_data.get("email_verified", False),
            }
        )
    elif provider == "apple":
        # Apple fornisce dati limitati
        standardized.update(
            {
                "email": user_data.get("email", ""),
                "first_name": user_data.get("name", {}).get("firstName", ""),
                "last_name": user_data.get("name", {}).get("lastName", ""),
                "is_verified": True,  # Apple verifica sempre l'email
            }
        )

    return standardized


# ==========================================
# 🎯 Helper Functions
# ==========================================


def get_current_user():
    """
    Placeholder per dependency injection in FastAPI.
    Implementazione reale in main.py
    """
    pass


async def get_user_permissions(user_role: str) -> list:
    """
    Ottieni permessi basati sul ruolo utente.

    Args:
        user_role: Ruolo utente (user, premium, admin)

    Returns:
        list: Lista di permessi
    """
    permissions = {
        "user": ["read:own_profile", "update:own_profile", "read:own_data"],
        "premium": [
            "read:own_profile",
            "update:own_profile",
            "read:own_data",
            "export:own_data",
            "advanced:analytics",
        ],
        "admin": [
            "read:any_profile",
            "update:any_profile",
            "read:any_data",
            "delete:any_user",
            "admin:dashboard",
        ],
    }

    return permissions.get(user_role, permissions["user"])


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maschera dati sensibili per logging sicuro.

    Args:
        data: Dati originali

    Returns:
        dict: Dati con informazioni sensibili mascherate
    """
    sensitive_fields = ["password", "hashed_password", "token", "secret", "key"]
    masked_data = data.copy()

    for field in sensitive_fields:
        if field in masked_data:
            masked_data[field] = "***MASKED***"

    # Maschera email parzialmente
    if "email" in masked_data:
        email = masked_data["email"]
        if "@" in email:
            local, domain = email.split("@", 1)
            if len(local) > 2:
                masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
                masked_data["email"] = f"{masked_local}@{domain}"

    return masked_data
