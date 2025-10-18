"""
Error handling middleware for API exceptions.

Provides consistent error responses across all endpoints.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.

    Returns 400 Bad Request with validation error details.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSONResponse: Error response with validation details
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle SQLAlchemy database errors.

    Returns 500 Internal Server Error without exposing database details.

    Args:
        request: FastAPI request
        exc: SQLAlchemy error

    Returns:
        JSONResponse: Generic error response
    """
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.

    Returns 500 Internal Server Error.

    Args:
        request: FastAPI request
        exc: Unexpected exception

    Returns:
        JSONResponse: Generic error response
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
        },
    )
