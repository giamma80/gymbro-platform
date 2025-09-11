"""
Authentication API endpoints.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from app.api.dependencies import get_auth_service, get_current_user
from app.application.auth_services import AuthenticationService
from app.domain.entities import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Request/Response models
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class MessageResponse(BaseModel):
    message: str


def get_request_info(request: Request) -> Dict[str, str]:
    """Extract request information for logging."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "device_info": request.headers.get("x-device-info"),
    }


@router.post("/register", response_model=MessageResponse)
async def register(
    request: Request,
    user_data: UserRegisterRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Register a new user."""
    try:
        result = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            request_info=get_request_info(request),
        )
        return MessageResponse(message=result["message"])

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    credentials: UserLoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Authenticate user and return access token."""
    try:
        result = await auth_service.login_user(
            email=credentials.email,
            password=credentials.password,
            request_info=get_request_info(request),
        )

        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Logout user and invalidate session."""
    try:
        token = credentials.credentials
        success = await auth_service.logout_user(
            token=token, request_info=get_request_info(request)
        )

        if success:
            return MessageResponse(message="Successfully logged out")
        else:
            return MessageResponse(message="Already logged out")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(
    request: Request,
    reset_request: PasswordResetRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Request password reset."""
    try:
        result = await auth_service.reset_password_request(
            email=reset_request.email, request_info=get_request_info(request)
        )
        return MessageResponse(message=result["message"])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed",
        )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    request: Request,
    reset_confirm: PasswordResetConfirm,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Confirm password reset with token."""
    try:
        result = await auth_service.reset_password_confirm(
            token=reset_confirm.token,
            new_password=reset_confirm.new_password,
            request_info=get_request_info(request),
        )
        return MessageResponse(message=result["message"])

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed",
        )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: Request,
    verification: EmailVerificationRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Verify email with token."""
    try:
        result = await auth_service.verify_email(
            token=verification.token, request_info=get_request_info(request)
        )
        return MessageResponse(message=result["message"])

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Refresh access token (placeholder for future implementation)."""
    # This would be implemented with refresh token logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token functionality not yet implemented",
    )


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_type: Optional[str] = "web"


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    expires_in: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    token: str


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================


@router.post("/auth/register", response_model=LoginResponse)
async def register_user(request: RegisterRequest, http_request: Request):
    """Register a new user account."""
    try:
        # Check if user already exists
        existing_user = await user_repo.get_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        existing_username = await user_repo.get_by_username(request.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Create new user
        user = User(
            id=UUID(int=0),  # Will be generated by database
            email=request.email,
            username=request.username,
            status=UserStatus.ACTIVE,
            email_verified_at=None,  # Requires email verification
        )

        created_user = await user_repo.create(user)

        # Create authentication credentials
        salt = bcrypt.gensalt()
        password_hash = hash_password(request.password, salt)

        credentials = AuthCredentials(
            id=UUID(int=0),
            user_id=created_user.id,
            password_hash=password_hash,
            salt=salt.decode("utf-8"),
            status=CredentialStatus.ACTIVE,
            password_changed_at=datetime.utcnow(),
        )

        await credentials_repo.create(credentials)

        # Create email verification token
        verification_token = secrets.token_urlsafe(32)
        verification = EmailVerificationToken(
            id=UUID(int=0),
            user_id=created_user.id,
            token=verification_token,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        await email_verification_repo.create(verification)

        # Log registration event
        await audit_repo.create(
            AuditLog(
                id=UUID(int=0),
                user_id=created_user.id,
                action="user_registered",
                resource="user",
                data={"email": request.email, "username": request.username},
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
            )
        )

        logger.info(
            "User registered successfully", user_id=created_user.id, email=request.email
        )

        return LoginResponse(
            success=True,
            message="User registered successfully. Please verify your email.",
            user_id=str(created_user.id),
        )

    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/auth/login", response_model=LoginResponse)
async def login_user(request: LoginRequest, http_request: Request):
    """Authenticate user and create session."""
    try:
        # Get user by email
        user = await user_repo.get_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive"
            )

        # Get credentials
        credentials = await credentials_repo.get_by_user_id(user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if account is locked
        if credentials.is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to too many failed attempts",
            )

        # Verify password
        if not verify_password(
            request.password, credentials.password_hash, credentials.salt
        ):
            # Increment failed attempts
            credentials.increment_failed_attempts()
            await credentials_repo.update(credentials)

            await audit_repo.create(
                AuditLog(
                    id=UUID(int=0),
                    user_id=user.id,
                    action="login_failed",
                    resource="auth",
                    data={"reason": "invalid_password"},
                    ip_address=http_request.client.host,
                    user_agent=http_request.headers.get("user-agent"),
                )
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Reset failed attempts on successful login
        credentials.reset_failed_attempts()
        await credentials_repo.update(credentials)

        # Create JWT tokens
        access_token = create_jwt_token({"user_id": str(user.id), "email": user.email})
        refresh_token = create_jwt_token(
            {"user_id": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=30),
        )

        # Create session
        device_type = DeviceType.WEB
        if request.device_type == "mobile":
            device_type = DeviceType.MOBILE
        elif request.device_type == "desktop":
            device_type = DeviceType.DESKTOP

        session = AuthSession(
            id=UUID(int=0),
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            device_type=device_type,
            user_agent=http_request.headers.get("user-agent"),
            ip_address=http_request.client.host,
            status=SessionStatus.ACTIVE,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            last_activity_at=datetime.utcnow(),
        )

        created_session = await session_repo.create(session)

        # Update user last login
        user.last_login_at = datetime.utcnow()
        await user_repo.update(user)

        # Log successful login
        await audit_repo.create(
            AuditLog(
                id=UUID(int=0),
                user_id=user.id,
                action="login_successful",
                resource="auth",
                data={"session_id": str(created_session.id)},
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
            )
        )

        logger.info(
            "User logged in successfully",
            user_id=user.id,
            session_id=created_session.id,
        )

        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            expires_in=3600,  # 1 hour
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/auth/logout")
async def logout_user(refresh_token: str, http_request: Request):
    """Logout user and revoke session."""
    try:
        # Find and revoke session
        session = await session_repo.get_by_refresh_token(refresh_token)
        if session:
            session.revoke()
            await session_repo.update(session)

            # Log logout event
            await audit_repo.create(
                AuditLog(
                    id=UUID(int=0),
                    user_id=session.user_id,
                    action="logout",
                    resource="auth",
                    data={"session_id": str(session.id)},
                    ip_address=http_request.client.host,
                    user_agent=http_request.headers.get("user-agent"),
                )
            )

            logger.info(
                "User logged out successfully",
                user_id=session.user_id,
                session_id=session.id,
            )

        return {"success": True, "message": "Logout successful"}

    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.post("/auth/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = verify_jwt_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user_id = UUID(payload.get("user_id"))

        # Get session
        session = await session_repo.get_by_refresh_token(request.refresh_token)
        if not session or not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Get user
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new access token
        access_token = create_jwt_token({"user_id": str(user.id), "email": user.email})

        # Update session
        session.session_token = access_token
        session.update_activity()
        await session_repo.update(session)

        logger.info("Token refreshed successfully", user_id=user.id)

        return LoginResponse(
            success=True,
            message="Token refreshed successfully",
            access_token=access_token,
            refresh_token=request.refresh_token,
            user_id=str(user.id),
            expires_in=3600,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token refresh failed"
        )


@router.post("/auth/reset-password")
async def request_password_reset(request: PasswordResetRequest, http_request: Request):
    """Request password reset email."""
    try:
        # Get user by email
        user = await user_repo.get_by_email(request.email)
        if not user:
            # Don't reveal if email exists or not
            return {
                "success": True,
                "message": "If the email exists, a reset link has been sent",
            }

        # Create password reset token
        reset_token = secrets.token_urlsafe(32)
        token = PasswordResetToken(
            id=UUID(int=0),
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
        )

        await password_reset_repo.create(token)

        # Log password reset request
        await audit_repo.create(
            AuditLog(
                id=UUID(int=0),
                user_id=user.id,
                action="password_reset_requested",
                resource="auth",
                data={"email": request.email},
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
            )
        )

        # TODO: Send email with reset link
        # For now, just log the token (in production, send email)
        logger.info(
            "Password reset requested",
            user_id=user.id,
            email=request.email,
            token=reset_token,
        )

        return {
            "success": True,
            "message": "If the email exists, a reset link has been sent",
        }

    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed",
        )


@router.post("/auth/reset-password/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest, http_request: Request
):
    """Confirm password reset with token."""
    try:
        # Get and validate token
        token = await password_reset_repo.get_by_token(request.token)
        if not token or not token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Get user
        user = await user_repo.get_by_id(token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update password
        credentials = await credentials_repo.get_by_user_id(user.id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User credentials not found",
            )

        # Hash new password
        salt = bcrypt.gensalt()
        password_hash = hash_password(request.new_password, salt)

        credentials.password_hash = password_hash
        credentials.salt = salt.decode("utf-8")
        credentials.password_changed_at = datetime.utcnow()
        credentials.failed_attempts = 0  # Reset failed attempts
        credentials.locked_until = None  # Unlock account

        await credentials_repo.update(credentials)

        # Mark token as used
        token.use()
        await password_reset_repo.update(token)

        # Revoke all existing sessions for security
        await session_repo.revoke_all_user_sessions(user.id)

        # Log password change
        await audit_repo.create(
            AuditLog(
                id=UUID(int=0),
                user_id=user.id,
                action="password_changed",
                resource="auth",
                data={"method": "reset_token"},
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
            )
        )

        logger.info("Password reset completed", user_id=user.id)

        return {"success": True, "message": "Password reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password reset confirmation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed",
        )


@router.post("/auth/verify-email")
async def verify_email(request: EmailVerificationRequest, http_request: Request):
    """Verify user email with token."""
    try:
        # Get and validate token
        token = await email_verification_repo.get_by_token(request.token)
        if not token or not token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # Get user
        user = await user_repo.get_by_id(token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Verify email
        user.verify_email()
        await user_repo.update(user)

        # Mark token as verified
        token.verify()
        await email_verification_repo.update(token)

        # Log email verification
        await audit_repo.create(
            AuditLog(
                id=UUID(int=0),
                user_id=user.id,
                action="email_verified",
                resource="user",
                data={"email": user.email},
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
            )
        )

        logger.info("Email verified successfully", user_id=user.id, email=user.email)

        return {"success": True, "message": "Email verified successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed",
        )
