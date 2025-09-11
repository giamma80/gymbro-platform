"""
Security utilities for authentication
=====================================
JWT token management, password hashing, and verification
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import structlog
from jose import jwt

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


def hash_password(password: str, salt: bytes) -> str:
    """Hash password with salt using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def get_password_hash(password: str) -> str:
    """Generate password hash with random salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str, salt: str = None) -> bool:
    """Verify password against hash."""
    try:
        if salt:
            # Legacy method with separate salt
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        else:
            # Modern method with salt included in hash
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
    except Exception:
        return False


def create_jwt_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT token with payload."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token (alias for create_jwt_token)."""
    return create_jwt_token(data, expires_delta)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode access token (alias for verify_jwt_token)."""
    return verify_jwt_token(token)
