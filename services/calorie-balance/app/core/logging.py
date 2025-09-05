import structlog
import sys
import logging
from typing import Any, Dict

def configure_logging(debug: bool = False) -> None:
    """Configure structured logging"""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if debug:
        # Pretty formatting for development
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON formatting for production
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.CRITICAL if not debug else logging.DEBUG
        ),
        logger_factory=structlog.WriteLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a logger instance"""
    return structlog.get_logger(name)


def log_request_context(**kwargs: Any) -> Dict[str, Any]:
    """Add request context to logs"""
    return {
        "request_id": kwargs.get("request_id"),
        "user_id": kwargs.get("user_id"),
        "endpoint": kwargs.get("endpoint"),
        "method": kwargs.get("method"),
    }
