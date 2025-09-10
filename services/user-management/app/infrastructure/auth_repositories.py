"""
Supabase-based repository implementations for authentication system.
All repositories use user_management schema.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from supabase import Client

from app.domain.entities import (
    AuthCredentials, AuthSession, SocialAuthProfile, AuditLog,
    PasswordResetToken, EmailVerificationToken, CredentialStatus
)
from app.domain.repositories import (
    AuthCredentialsRepository, AuthSessionRepository,
    SocialAuthProfileRepository, AuditLogRepository,
    PasswordResetTokenRepository, EmailVerificationTokenRepository
)
from app.core.schema_tables import (
    get_auth_credentials_table, get_auth_sessions_table,
    get_social_auth_profiles_table, get_audit_logs_table,
    get_password_reset_tokens_table, get_email_verification_tokens_table
)


class SupabaseAuthCredentialsRepository(AuthCredentialsRepository):
    """Supabase implementation of AuthCredentials repository."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = get_auth_credentials_table(supabase)

    async def create(self, credentials: AuthCredentials) -> AuthCredentials:
        """Create authentication credentials."""
        data = {
            "user_id": str(credentials.user_id),
            "password_hash": credentials.password_hash,
            "salt": credentials.salt,
            "failed_attempts": credentials.failed_attempts,
            "locked_until": credentials.locked_until.isoformat() if credentials.locked_until else None,
            "last_login": credentials.last_login.isoformat() if credentials.last_login else None,
            "password_changed_at": credentials.password_changed_at.isoformat(),
            "requires_password_change": credentials.requires_password_change,
            "status": credentials.status.value,
            "created_at": credentials.created_at.isoformat(),
            "updated_at": credentials.updated_at.isoformat()
        }
        
        result = (
            self.table
            .insert(data)
            .execute()
        )
        
        # Construct AuthCredentials from database result
        db_data = result.data[0]
        return AuthCredentials(
            id=UUID(db_data["id"]),
            user_id=UUID(db_data["user_id"]),
            password_hash=db_data["password_hash"],
            salt=db_data["salt"],
            status=CredentialStatus(db_data["status"]),
            password_changed_at=datetime.fromisoformat(db_data["password_changed_at"]),
            failed_attempts=db_data["failed_attempts"],
            locked_until=datetime.fromisoformat(db_data["locked_until"]) if db_data["locked_until"] else None,
            last_login=datetime.fromisoformat(db_data["last_login"]) if db_data.get("last_login") else None,
            requires_password_change=db_data.get("requires_password_change", False),
            created_at=datetime.fromisoformat(db_data["created_at"]),
            updated_at=datetime.fromisoformat(db_data["updated_at"])
        )

    async def get_by_user_id(self, user_id: UUID) -> Optional[AuthCredentials]:
        """Get credentials by user ID."""
        result = self.table.select("*").eq("user_id", str(user_id)).execute()
        
        if result.data:
            db_data = result.data[0]
            return AuthCredentials(
                id=UUID(db_data["id"]),
                user_id=UUID(db_data["user_id"]),
                password_hash=db_data["password_hash"],
                salt=db_data["salt"],
                status=CredentialStatus(db_data["status"]),
                password_changed_at=datetime.fromisoformat(db_data["password_changed_at"]),
                failed_attempts=db_data["failed_attempts"],
                locked_until=datetime.fromisoformat(db_data["locked_until"]) if db_data["locked_until"] else None,
                last_login=datetime.fromisoformat(db_data["last_login"]) if db_data.get("last_login") else None,
                requires_password_change=db_data.get("requires_password_change", False),
                created_at=datetime.fromisoformat(db_data["created_at"]),
                updated_at=datetime.fromisoformat(db_data["updated_at"])
            )
        return None

    async def update(self, credentials: AuthCredentials) -> AuthCredentials:
        """Update authentication credentials."""
        data = {
            "password_hash": credentials.password_hash,
            "salt": credentials.salt,
            "failed_attempts": credentials.failed_attempts,
            "locked_until": credentials.locked_until.isoformat() if credentials.locked_until else None,
            "last_login": credentials.last_login.isoformat() if credentials.last_login else None,
            "password_changed_at": credentials.password_changed_at.isoformat(),
            "requires_password_change": credentials.requires_password_change,
            "status": credentials.status.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.table.update(data).eq("user_id", str(credentials.user_id)).execute()
        
        # Construct AuthCredentials from database result
        db_data = result.data[0]
        return AuthCredentials(
            id=UUID(db_data["id"]),
            user_id=UUID(db_data["user_id"]),
            password_hash=db_data["password_hash"],
            salt=db_data["salt"],
            status=CredentialStatus(db_data["status"]),
            password_changed_at=datetime.fromisoformat(db_data["password_changed_at"]),
            failed_attempts=db_data["failed_attempts"],
            locked_until=datetime.fromisoformat(db_data["locked_until"]) if db_data["locked_until"] else None,
            last_login=datetime.fromisoformat(db_data["last_login"]) if db_data.get("last_login") else None,
            requires_password_change=db_data.get("requires_password_change", False),
            created_at=datetime.fromisoformat(db_data["created_at"]),
            updated_at=datetime.fromisoformat(db_data["updated_at"])
        )

    async def delete(self, user_id: UUID) -> bool:
        """Delete authentication credentials."""
        result = self.table.delete().eq("user_id", str(user_id)).execute()
        return len(result.data) > 0

    async def increment_failed_attempts(self, user_id: UUID) -> int:
        """Increment failed login attempts."""
        credentials = await self.get_by_user_id(user_id)
        if not credentials:
            return 0
            
        credentials.failed_attempts += 1
        
        # Lock account after 5 failed attempts for 15 minutes
        if credentials.failed_attempts >= 5:
            credentials.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
        await self.update(credentials)
        return credentials.failed_attempts

    async def reset_failed_attempts(self, user_id: UUID) -> bool:
        """Reset failed login attempts."""
        credentials = await self.get_by_user_id(user_id)
        if not credentials:
            return False
            
        credentials.failed_attempts = 0
        credentials.locked_until = None
        await self.update(credentials)
        return True


class SupabaseAuthSessionRepository(AuthSessionRepository):
    """Supabase implementation of AuthSession repository."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = get_auth_sessions_table(supabase)

    async def create(self, session: AuthSession) -> AuthSession:
        """Create authentication session."""
        data = {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "token": session.token,
            "refresh_token": session.refresh_token,
            "expires_at": session.expires_at.isoformat(),
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_type": session.device_type,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
        
        result = self.table.insert(data).execute()
        return AuthSession(**result.data[0])

    async def get_by_token(self, token: str) -> Optional[AuthSession]:
        """Get session by token."""
        result = self.table.select("*").eq("token", token).execute()
        
        if result.data:
            return AuthSession(**result.data[0])
        return None

    async def get_by_user_id(self, user_id: UUID, active_only: bool = True) -> List[AuthSession]:
        """Get sessions by user ID."""
        query = self.table.select("*").eq("user_id", str(user_id))
        
        if active_only:
            query = query.eq("status", "active")
            
        result = query.execute()
        return [AuthSession(**session) for session in result.data]

    async def update(self, session: AuthSession) -> AuthSession:
        """Update session."""
        data = {
            "token": session.token,
            "refresh_token": session.refresh_token,
            "expires_at": session.expires_at.isoformat(),
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_type": session.device_type,
            "status": session.status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.table.update(data).eq("id", str(session.id)).execute()
        return AuthSession(**result.data[0])

    async def invalidate_session(self, token: str) -> bool:
        """Invalidate session."""
        result = self.table.update({
            "status": "inactive",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("token", token).execute()
        
        return len(result.data) > 0

    async def invalidate_user_sessions(self, user_id: UUID) -> int:
        """Invalidate all user sessions."""
        result = self.table.update({
            "status": "revoked"
        }).eq("user_id", str(user_id)).eq("status", "active").execute()
        
        return len(result.data)

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        cutoff_time = datetime.utcnow().isoformat()
        
        result = self.table.update({
            "status": "expired",
            "updated_at": datetime.utcnow().isoformat()
        }).lt("expires_at", cutoff_time).eq("status", "active").execute()
        
        return len(result.data)


class SupabasePasswordResetTokenRepository(PasswordResetTokenRepository):
    """Supabase implementation of PasswordResetToken repository."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = get_password_reset_tokens_table(supabase)

    async def create(self, token: PasswordResetToken) -> PasswordResetToken:
        """Create password reset token."""
        data = {
            "id": str(token.id),
            "user_id": str(token.user_id),
            "token": token.token,
            "expires_at": token.expires_at.isoformat(),
            "used": token.used,
            "created_at": token.created_at.isoformat()
        }
        
        result = self.table.insert(data).execute()
        return PasswordResetToken(**result.data[0])

    async def get_by_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get token by token string."""
        result = self.table.select("*").eq("token", token).eq("used", False).execute()
        
        if result.data:
            return PasswordResetToken(**result.data[0])
        return None

    async def get_by_user_id(self, user_id: UUID) -> List[PasswordResetToken]:
        """Get active tokens by user ID."""
        result = self.table.select("*").eq("user_id", str(user_id)).eq("used", False).execute()
        return [PasswordResetToken(**token) for token in result.data]

    async def invalidate_token(self, token: str) -> bool:
        """Invalidate token."""
        result = self.table.update({
            "used": True
        }).eq("token", token).execute()
        
        return len(result.data) > 0

    async def invalidate_user_tokens(self, user_id: UUID) -> int:
        """Invalidate all user tokens."""
        result = self.table.update({
            "used": True
        }).eq("user_id", str(user_id)).eq("used", False).execute()
        
        return len(result.data)

    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        cutoff_time = datetime.utcnow().isoformat()
        
        # Mark expired tokens as used
        result = self.table.update({
            "used": True
        }).lt("expires_at", cutoff_time).eq("used", False).execute()
        
        return len(result.data)


class SupabaseEmailVerificationTokenRepository(EmailVerificationTokenRepository):
    """Supabase implementation of EmailVerificationToken repository."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = get_email_verification_tokens_table(supabase)

    async def create(self, token: EmailVerificationToken) -> EmailVerificationToken:
        """Create email verification token."""
        data = {
            "id": str(token.id),
            "user_id": str(token.user_id),
            "email": token.email,
            "token": token.token,
            "expires_at": token.expires_at.isoformat(),
            "verified": token.verified,
            "verified_at": token.verified_at.isoformat() if token.verified_at else None,
            "created_at": token.created_at.isoformat()
        }
        
        result = self.table.insert(data).execute()
        return EmailVerificationToken(**result.data[0])

    async def get_by_token(self, token: str) -> Optional[EmailVerificationToken]:
        """Get token by token string."""
        result = self.table.select("*").eq("token", token).eq("verified", False).execute()
        
        if result.data:
            return EmailVerificationToken(**result.data[0])
        return None

    async def get_by_user_id(self, user_id: UUID) -> List[EmailVerificationToken]:
        """Get active tokens by user ID."""
        result = self.table.select("*").eq("user_id", str(user_id)).eq("verified", False).execute()
        return [EmailVerificationToken(**token) for token in result.data]

    async def invalidate_token(self, token: str) -> bool:
        """Invalidate token."""
        result = self.table.update({
            "verified": True,
            "verified_at": datetime.utcnow().isoformat()
        }).eq("token", token).execute()
        
        return len(result.data) > 0

    async def invalidate_user_tokens(self, user_id: UUID) -> int:
        """Invalidate all user tokens."""
        result = self.table.update({
            "verified": True,
            "verified_at": datetime.utcnow().isoformat()
        }).eq("user_id", str(user_id)).eq("verified", False).execute()
        
        return len(result.data)

    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        cutoff_time = datetime.utcnow().isoformat()
        
        # Mark expired tokens as verified
        result = self.table.update({
            "verified": True,
            "verified_at": datetime.utcnow().isoformat()
        }).lt("expires_at", cutoff_time).eq("verified", False).execute()
        
        return len(result.data)


class SupabaseAuditLogRepository(AuditLogRepository):
    """Supabase implementation of AuditLog repository."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = get_audit_logs_table(supabase)

    async def create(self, log: AuditLog) -> AuditLog:
        """Create audit log entry."""
        data = {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": str(log.resource_id) if log.resource_id else None,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "created_at": log.created_at.isoformat()
        }
        
        result = self.table.insert(data).execute()
        return AuditLog(**result.data[0])

    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs by user ID with pagination and date filters."""
        query = self.table.select("*").eq("user_id", str(user_id))
        
        if start_date:
            query = query.gte("created_at", start_date.isoformat())
        if end_date:
            query = query.lte("created_at", end_date.isoformat())
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        
        result = query.execute()
        return [AuditLog(**log) for log in result.data]

    async def get_by_action(self, action: str, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Get audit logs by action type."""
        result = self.table.select("*").eq("action", action).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return [AuditLog(**log) for log in result.data]

    async def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """Clean up old audit logs."""
        cutoff_date = (datetime.utcnow() - timedelta(days=days_to_keep)).isoformat()
        
        result = self.table.delete().lt("created_at", cutoff_date).execute()
        return len(result.data)


class SupabaseSocialAuthProfileRepository(SocialAuthProfileRepository):
    """Supabase implementation of SocialAuthProfile repository."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = get_social_auth_profiles_table(supabase)

    async def create(self, profile: SocialAuthProfile) -> SocialAuthProfile:
        """Create social auth profile."""
        data = {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "provider": profile.provider,
            "provider_user_id": profile.provider_user_id,
            "email": profile.email,
            "name": profile.name,
            "avatar_url": profile.avatar_url,
            "profile_data": profile.profile_data,
            "access_token": profile.access_token,
            "refresh_token": profile.refresh_token,
            "token_expires_at": profile.token_expires_at.isoformat() if profile.token_expires_at else None,
            "status": profile.status,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat()
        }
        
        result = self.table.insert(data).execute()
        return SocialAuthProfile(**result.data[0])

    async def get_by_provider_id(self, provider: str, provider_user_id: str) -> Optional[SocialAuthProfile]:
        """Get profile by provider and provider user ID."""
        result = self.table.select("*").eq("provider", provider).eq("provider_user_id", provider_user_id).execute()
        
        if result.data:
            return SocialAuthProfile(**result.data[0])
        return None

    async def get_by_user_id(self, user_id: UUID) -> List[SocialAuthProfile]:
        """Get social profiles by user ID."""
        result = self.table.select("*").eq("user_id", str(user_id)).execute()
        return [SocialAuthProfile(**profile) for profile in result.data]

    async def update(self, profile: SocialAuthProfile) -> SocialAuthProfile:
        """Update social auth profile."""
        data = {
            "email": profile.email,
            "name": profile.name,
            "avatar_url": profile.avatar_url,
            "profile_data": profile.profile_data,
            "access_token": profile.access_token,
            "refresh_token": profile.refresh_token,
            "token_expires_at": profile.token_expires_at.isoformat() if profile.token_expires_at else None,
            "status": profile.status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.table.update(data).eq("id", str(profile.id)).execute()
        return SocialAuthProfile(**result.data[0])

    async def delete(self, profile_id: UUID) -> bool:
        """Delete social auth profile."""
        result = self.table.delete().eq("id", str(profile_id)).execute()
        return len(result.data) > 0
