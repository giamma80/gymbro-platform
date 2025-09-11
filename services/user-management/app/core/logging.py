"""
Logging Configuration - Supabase Client Template
Service: user-management
"""

import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

from app.core.config import get_settings

# Context variables for request tracing
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def add_correlation_id(
    logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add correlation ID to log entries."""
    correlation_id = correlation_id_var.get()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def add_user_context(
    logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add user context to log entries."""
    user_id = user_id_var.get()
    if user_id:
        event_dict["user_id"] = user_id
    return event_dict


def add_service_context(
    logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add service context to log entries."""
    settings = get_settings()
    event_dict["service"] = settings.service_name
    event_dict["environment"] = settings.environment
    return event_dict


def add_timestamp(
    logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add ISO timestamp to log entries."""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict


def configure_logging():
    """Configure structured logging for the application."""
    settings = get_settings()

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Processors chain
    processors: list[Processor] = [
        add_timestamp,
        add_service_context,
        add_correlation_id,
        add_user_context,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.structured_logging:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable output for development
        processors.extend(
            [
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.dev.ConsoleRenderer(),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
