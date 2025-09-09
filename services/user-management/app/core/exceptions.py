"""
Exception Handling - Supabase Client Template
Service: user-management
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError
import structlog

logger = structlog.get_logger()

# Domain Exceptions
class ServiceException(Exception):
    """Base exception for service domain."""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

class ValidationError(ServiceException):
    """Domain validation error."""
    pass

class NotFoundError(ServiceException):
    """Resource not found error."""
    pass

class AuthenticationError(ServiceException):
    """Authentication error."""
    pass

class AuthorizationError(ServiceException):
    """Authorization error."""
    pass

# Supabase specific exceptions
class SupabaseError(ServiceException):
    """Supabase operation error."""
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code

# API Exceptions
class APIError(HTTPException):
    """Base API error with structured response."""
    def __init__(
        self, 
        status_code: int, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or "API_ERROR"
        self.details = details or {}
        
        super().__init__(
            status_code=status_code,
            detail={
                "message": self.message,
                "error_code": self.error_code,
                "details": self.details
            }
        )

def setup_exception_handlers(app):
    """Setup FastAPI exception handlers."""
    
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        """Handle domain exceptions."""
        logger.error(
            "Service exception occurred",
            error_type=exc.__class__.__name__,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            path=request.url.path,
            method=request.method
        )
        
        # Map domain exceptions to HTTP status codes
        status_code_map = {
            ValidationError: status.HTTP_400_BAD_REQUEST,
            NotFoundError: status.HTTP_404_NOT_FOUND,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            SupabaseError: status.HTTP_502_BAD_GATEWAY,
        }
        
        status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details
            },
            headers={"X-Error-Code": exc.error_code}
        )
    
    @app.exception_handler(APIError)
    async def api_exception_handler(request: Request, exc: APIError):
        """Handle API exceptions."""
        logger.error(
            "API exception occurred",
            error_type=exc.__class__.__name__,
            message=exc.message,
            error_code=exc.error_code,
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers={"X-Error-Code": exc.error_code}
        )
    
    @app.exception_handler(APIError)
    async def supabase_api_error_handler(request: Request, exc: APIError):
        """Handle Supabase API errors."""
        logger.error(
            "Supabase API error occurred",
            error=str(exc),
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "message": "Database operation failed",
                "error_code": "SUPABASE_ERROR",
                "details": {"supabase_error": str(exc)}
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "Unexpected exception occurred",
            error_type=exc.__class__.__name__,
            message=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
                "details": {}
            },
            headers={"X-Error-Code": "INTERNAL_ERROR"}
        )
