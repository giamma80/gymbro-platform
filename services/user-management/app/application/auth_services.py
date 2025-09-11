"""
Application services layer for authentication operations.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.domain.entities import (
    AuditLog,
    AuthCredentials,
    AuthSession,
    CredentialStatus,
    EmailVerificationToken,
    PasswordResetToken,
    User,
    UserProfile,
    UserStatus,
)
from app.domain.repositories import (
    AuditLogRepository,
    AuthCredentialsRepository,
    AuthSessionRepository,
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
    UserProfileRepository,
    UserRepository,
)

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for authentication operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        auth_credentials_repo: AuthCredentialsRepository,
        auth_session_repo: AuthSessionRepository,
        password_reset_repo: PasswordResetTokenRepository,
        email_verification_repo: EmailVerificationTokenRepository,
        audit_log_repo: AuditLogRepository,
        user_profile_repo: UserProfileRepository,
    ):
        self.user_repo = user_repo
        self.auth_credentials_repo = auth_credentials_repo
        self.auth_session_repo = auth_session_repo
        self.password_reset_repo = password_reset_repo
        self.email_verification_repo = email_verification_repo
        self.audit_log_repo = audit_log_repo
        self.user_profile_repo = user_profile_repo

    async def register_user(
        self,
        email: str,
        password: str,
        username: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        request_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = await self.user_repo.get_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")

            existing_username = await self.user_repo.get_by_username(username)
            if existing_username:
                raise ValueError("Username already taken")

            # Create user entity (core identity only)
            user = User(
                id=uuid4(),
                email=email,
                username=username,
                status=UserStatus.ACTIVE,
                email_verified_at=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login_at=None,
            )
            user = await self.user_repo.create(user)

            # Create user profile with first_name and last_name
            if first_name or last_name:
                profile = UserProfile(
                    id=uuid4(),
                    user_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    display_name=f"{first_name or ''} {last_name or ''}".strip(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                await self.user_profile_repo.create(profile)

            # Create authentication credentials
            password_hash = get_password_hash(password)
            credentials = AuthCredentials(
                id=uuid4(),
                user_id=user.id,
                password_hash=password_hash,
                salt=secrets.token_hex(32),
                status=CredentialStatus.ACTIVE,
                password_changed_at=datetime.utcnow(),
            )
            await self.auth_credentials_repo.create(credentials)

            # Create email verification token
            verification_token = EmailVerificationToken(
                user_id=user.id, email=email, token=secrets.token_urlsafe(32)
            )
            await self.email_verification_repo.create(verification_token)

            # Log registration
            await self._log_action(
                user_id=user.id,
                action="user_registered",
                resource_type="user",
                resource_id=user.id,
                details={"email": email, "username": username},
                request_info=request_info,
            )

            return {
                "user": user,
                "verification_token": verification_token.token,
                "message": "User registered successfully. Please verify your email.",
            }

        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise

    async def login_user(
        self, email: str, password: str, request_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Authenticate user and create session."""
        try:
            # Get user
            user = await self.user_repo.get_by_email(email)
            if not user:
                raise ValueError("Invalid email or password")

            # Check if user is active
            if not user.is_active:
                raise ValueError("Account is deactivated")

            # Get credentials
            credentials = await self.auth_credentials_repo.get_by_user_id(user.id)
            if not credentials:
                raise ValueError("Invalid email or password")

            # Check if account is locked
            if credentials.is_locked():
                raise ValueError(
                    "Account is temporarily locked due to failed login attempts"
                )

            # Verify password
            if not verify_password(password, credentials.password_hash):
                # Increment failed attempts
                await self.auth_credentials_repo.increment_failed_attempts(user.id)

                # Log failed attempt
                await self._log_action(
                    user_id=user.id,
                    action="login_failed",
                    resource_type="user",
                    resource_id=user.id,
                    details={"reason": "invalid_password"},
                    request_info=request_info,
                )

                raise ValueError("Invalid email or password")

            # Reset failed attempts on successful login
            await self.auth_credentials_repo.reset_failed_attempts(user.id)

            # Update last login
            credentials.last_login = datetime.utcnow()
            await self.auth_credentials_repo.update(credentials)

            # Create JWT token
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )

            # Create session
            session = AuthSession(
                user_id=user.id,
                token=access_token,
                refresh_token=secrets.token_urlsafe(32),
                device_info=request_info.get("device_info") if request_info else None,
                ip_address=request_info.get("ip_address") if request_info else None,
                user_agent=request_info.get("user_agent") if request_info else None,
            )
            await self.auth_session_repo.create(session)

            # Log successful login
            await self._log_action(
                user_id=user.id,
                action="login_successful",
                resource_type="user",
                resource_id=user.id,
                details={"session_id": str(session.id)},
                request_info=request_info,
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user,
            }

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise

    async def logout_user(
        self, token: str, request_info: Optional[Dict[str, str]] = None
    ) -> bool:
        """Logout user and invalidate session."""
        try:
            # Invalidate session
            session = await self.auth_session_repo.get_by_token(token)
            if session:
                await self.auth_session_repo.invalidate_session(token)

                # Log logout
                await self._log_action(
                    user_id=session.user_id,
                    action="logout",
                    resource_type="user",
                    resource_id=session.user_id,
                    details={"session_id": str(session.id)},
                    request_info=request_info,
                )

                return True

            return False

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise

    async def reset_password_request(
        self, email: str, request_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Request password reset."""
        try:
            user = await self.user_repo.get_by_email(email)
            if not user:
                # Don't reveal if email exists for security
                return {"message": "If the email exists, a reset link has been sent."}

            # Invalidate existing tokens
            await self.password_reset_repo.invalidate_user_tokens(user.id)

            # Create new reset token
            reset_token = PasswordResetToken(
                user_id=user.id, token=secrets.token_urlsafe(32)
            )
            await self.password_reset_repo.create(reset_token)

            # Log password reset request
            await self._log_action(
                user_id=user.id,
                action="password_reset_requested",
                resource_type="user",
                resource_id=user.id,
                details={"token_id": str(reset_token.id)},
                request_info=request_info,
            )

            return {
                "message": "Password reset link has been sent to your email.",
                "reset_token": reset_token.token,  # In production, send via email
            }

        except Exception as e:
            logger.error(f"Password reset request failed: {str(e)}")
            raise

    async def reset_password_confirm(
        self,
        token: str,
        new_password: str,
        request_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Confirm password reset with token."""
        try:
            # Validate token
            reset_token = await self.password_reset_repo.get_by_token(token)
            if not reset_token or reset_token.is_expired():
                raise ValueError("Invalid or expired reset token")

            # Get user
            user = await self.user_repo.get_by_id(reset_token.user_id)
            if not user:
                raise ValueError("User not found")

            # Update password
            credentials = await self.auth_credentials_repo.get_by_user_id(user.id)
            if credentials:
                credentials.password_hash = get_password_hash(new_password)
                credentials.password_changed_at = datetime.utcnow()
                credentials.requires_password_change = False
                await self.auth_credentials_repo.update(credentials)

            # Invalidate token
            await self.password_reset_repo.invalidate_token(token)

            # Invalidate all user sessions
            await self.auth_session_repo.invalidate_user_sessions(user.id)

            # Log password change
            await self._log_action(
                user_id=user.id,
                action="password_changed",
                resource_type="user",
                resource_id=user.id,
                details={"via": "reset_token"},
                request_info=request_info,
            )

            return {"message": "Password has been reset successfully."}

        except Exception as e:
            logger.error(f"Password reset confirmation failed: {str(e)}")
            raise

    async def verify_email(
        self, token: str, request_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Verify email with token."""
        try:
            # Validate token
            verification_token = await self.email_verification_repo.get_by_token(token)
            if not verification_token or verification_token.is_expired():
                raise ValueError("Invalid or expired verification token")

            # Get user
            user = await self.user_repo.get_by_id(verification_token.user_id)
            if not user:
                raise ValueError("User not found")

            # Mark user as verified
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
            await self.user_repo.update(user)

            # Invalidate token
            await self.email_verification_repo.invalidate_token(token)

            # Log email verification
            await self._log_action(
                user_id=user.id,
                action="email_verified",
                resource_type="user",
                resource_id=user.id,
                details={"email": user.email},
                request_info=request_info,
            )

            return {"message": "Email verified successfully."}

        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            raise

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        try:
            # Decode token
            payload = decode_access_token(token)
            if not payload:
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            # Get user
            user = await self.user_repo.get_by_id(UUID(user_id))
            return user

        except Exception as e:
            logger.error(f"Get current user failed: {str(e)}")
            return None

    async def _log_action(
        self,
        user_id: Optional[UUID],
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        request_info: Optional[Dict[str, str]] = None,
    ):
        """Log user action for audit purposes."""
        try:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=request_info.get("ip_address") if request_info else None,
                user_agent=request_info.get("user_agent") if request_info else None,
            )
            await self.audit_log_repo.create(log_entry)
        except Exception as e:
            logger.error(f"Failed to log action: {str(e)}")
            # Don't fail the main operation due to logging failure
