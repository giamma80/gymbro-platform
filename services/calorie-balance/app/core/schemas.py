from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]


class PaginationResponse(BaseModel):
    """Pagination metadata"""
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    has_next: bool
    has_prev: bool


class BaseResponse(BaseModel):
    """Base response with metadata"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseResponse):
    """Paginated response wrapper"""
    data: List[Any]
    pagination: PaginationResponse


class APIResponse(BaseResponse, BaseModel):
    """Generic API response wrapper"""
    data: Optional[Any] = None
