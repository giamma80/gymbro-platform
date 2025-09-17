"""
GraphQL Interceptors for Logging and Monitoring
Service: calorie-balance

Provides comprehensive logging for GraphQL operations including:
- Query/Mutation execution logging
- Resolver execution logging  
- Performance monitoring
- Error tracking
"""

import inspect
import json
import logging
import time
from functools import wraps
from typing import Any, Dict, Optional

import structlog
from graphql import GraphQLError, GraphQLResolveInfo
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionResult
from strawberry.types.info import Info

# Use standard logger to avoid structlog conflicts in interceptors
interceptor_logger = logging.getLogger("graphql_interceptors")
logger = structlog.get_logger()


class GraphQLQueryLoggingExtension(SchemaExtension):
    """Extension to log all GraphQL queries and mutations."""

    def on_operation(self):
        """Called when a GraphQL operation starts."""
        return GraphQLQueryInterceptor()


class GraphQLQueryInterceptor:
    """Intercepts GraphQL operations for logging."""

    def on_request(self, context):
        """Called at the start of request processing."""
        self.start_time = time.time()
        self.context = context
        return self

    def on_parse(self, context):
        """Called after query parsing."""
        query = getattr(context, "query", None)
        variables = getattr(context, "variables", {})
        operation_name = getattr(context, "operation_name", None)

        # Sanitize variables (remove sensitive data)
        sanitized_variables = self._sanitize_variables(variables)

        interceptor_logger.info(
            "GraphQL query parsed",
            query=self._format_query(query),
            variables=sanitized_variables,
            operation_name=operation_name,
            event="graphql_parse",
        )
        return self

    def on_execute(self, context):
        """Called when query execution starts."""
        interceptor_logger.info(
            "GraphQL query execution started", event="graphql_execute_start"
        )
        return self

    def on_end(self, result: ExecutionResult):
        """Called when operation completes."""
        duration = time.time() - self.start_time

        # Check for errors
        has_errors = result.errors is not None and len(result.errors) > 0

        if has_errors:
            error_messages = [str(error) for error in result.errors]
            interceptor_logger.error(
                "GraphQL query completed with errors",
                duration=duration,
                errors=error_messages,
                event="graphql_execute_error",
            )
        else:
            # Log data summary without full data (for privacy)
            data_summary = self._summarize_data(result.data)
            interceptor_logger.info(
                "GraphQL query completed successfully",
                duration=duration,
                data_summary=data_summary,
                event="graphql_execute_success",
            )

        return result

    def _format_query(self, query: str) -> str:
        """Format query for logging (remove extra whitespace)."""
        if not query:
            return ""
        return " ".join(query.split())

    def _sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from variables."""
        if not variables:
            return {}

        sanitized = {}
        sensitive_keys = {"password", "token", "secret", "key", "authorization"}

        for key, value in variables.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value

        return sanitized

    def _summarize_data(self, data: Any) -> Dict[str, Any]:
        """Create a summary of returned data without exposing sensitive info."""
        if data is None:
            return {"type": "null"}

        if isinstance(data, dict):
            summary = {"type": "object", "keys": list(data.keys())}

            # Add counts for arrays
            for key, value in data.items():
                if isinstance(value, list):
                    summary[f"{key}_count"] = len(value)
                elif (
                    isinstance(value, dict)
                    and "data" in value
                    and isinstance(value["data"], list)
                ):
                    summary[f"{key}_data_count"] = len(value["data"])
                    summary[f"{key}_success"] = value.get("success", "unknown")

            return summary
        elif isinstance(data, list):
            return {"type": "array", "count": len(data)}
        else:
            return {"type": type(data).__name__}


def log_resolver_execution(func):
    """Decorator to log resolver execution."""

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        resolver_name = func.__name__
        start_time = time.time()

        # Extract user_id from kwargs if present
        user_id = kwargs.get("user_id", "unknown")

        interceptor_logger.info(
            f"Resolver {resolver_name} started: user={user_id}, "
            f"args={len(args)}, kwargs={list(kwargs.keys())}"
        )

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            # Log success with result summary
            result_summary = _get_result_summary(result)
            interceptor_logger.info(
                f"Resolver {resolver_name} completed: user={user_id}, "
                f"duration={duration:.3f}s, result={result_summary}"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            interceptor_logger.error(
                f"Resolver {resolver_name} failed: user={user_id}, "
                f"duration={duration:.3f}s, error={str(e)}"
            )
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        resolver_name = func.__name__
        start_time = time.time()

        # Extract user_id from kwargs if present
        user_id = kwargs.get("user_id", "unknown")

        interceptor_logger.info(
            f"Resolver {resolver_name} started: user={user_id}, "
            f"args={len(args)}, kwargs={list(kwargs.keys())}"
        )

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            # Log success with result summary
            result_summary = _get_result_summary(result)
            interceptor_logger.info(
                f"Resolver {resolver_name} completed: user={user_id}, "
                f"duration={duration:.3f}s, result={result_summary}"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            interceptor_logger.error(
                f"Resolver {resolver_name} failed: user={user_id}, "
                f"duration={duration:.3f}s, error={str(e)}"
            )
            raise

    # Check if function is async
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def _get_result_summary(result: Any) -> Dict[str, Any]:
    """Get summary of resolver result."""
    if result is None:
        return {"type": "null"}

    if hasattr(result, "success") and hasattr(result, "data"):
        # GraphQL Response objects
        data_count = (
            len(result.data)
            if isinstance(result.data, list)
            else (1 if result.data else 0)
        )
        return {
            "type": "GraphQLResponse",
            "success": result.success,
            "data_count": data_count,
            "has_message": hasattr(result, "message") and result.message is not None,
        }
    elif isinstance(result, list):
        return {"type": "list", "count": len(result)}
    elif isinstance(result, dict):
        return {"type": "dict", "keys": list(result.keys())}
    else:
        return {"type": type(result).__name__}


class DatabaseQueryLoggingInterceptor:
    """Intercepts and logs database queries for monitoring."""

    def __init__(self, original_client):
        """Initialize with the original Supabase client."""
        self.original_client = original_client
        self._wrap_client_methods()

    def _wrap_client_methods(self):
        """Wrap client methods for logging."""
        # Wrap table method to intercept queries
        original_table = self.original_client.table

        def logged_table(table_name: str):
            table_instance = original_table(table_name)
            return DatabaseTableWrapper(table_instance, table_name)

        self.original_client.table = logged_table

    def get_client(self):
        """Get the wrapped client."""
        return self.original_client


class DatabaseTableWrapper:
    """Wrapper for Supabase table to log queries."""

    def __init__(self, table_instance, table_name: str):
        self.table_instance = table_instance
        self.table_name = table_name

    def __getattr__(self, name):
        """Proxy all methods to the original table instance."""
        attr = getattr(self.table_instance, name)

        # If it's a query method, wrap it with logging
        if name in ["select", "insert", "update", "delete", "upsert"]:
            return self._wrap_query_method(attr, name)

        return attr

    def _wrap_query_method(self, method, method_name: str):
        """Wrap query methods with logging."""

        def logged_method(*args, **kwargs):
            start_time = time.time()

            interceptor_logger.info(
                "Database query started",
                table=self.table_name,
                method=method_name,
                args=args,
                kwargs=kwargs,
                event="db_query_start",
            )

            try:
                result = method(*args, **kwargs)

                # If result has execute method, wrap it too
                if hasattr(result, "execute"):
                    original_execute = result.execute

                    async def logged_execute():
                        try:
                            exec_result = await original_execute()
                            duration = time.time() - start_time

                            data_count = (
                                len(exec_result.data) if exec_result.data else 0
                            )
                            interceptor_logger.info(
                                "Database query executed successfully",
                                table=self.table_name,
                                method=method_name,
                                duration=duration,
                                data_count=data_count,
                                event="db_query_success",
                            )

                            return exec_result
                        except Exception as e:
                            duration = time.time() - start_time
                            interceptor_logger.error(
                                "Database query failed",
                                table=self.table_name,
                                method=method_name,
                                duration=duration,
                                error=str(e),
                                event="db_query_error",
                            )
                            raise

                    result.execute = logged_execute

                return result

            except Exception as e:
                duration = time.time() - start_time
                interceptor_logger.error(
                    "Database query failed",
                    table=self.table_name,
                    method=method_name,
                    duration=duration,
                    error=str(e),
                    event="db_query_error",
                )
                raise

        return logged_method
