"""
Authentication middleware for device token validation.

Per data-model.md: All requests authenticated via Bearer token (UUID v4 device token).
"""

from fastapi import Header, HTTPException, status
from typing import Annotated
import uuid


async def get_device_token(
    authorization: Annotated[str | None, Header()] = None
) -> uuid.UUID:
    """
    Extract and validate device token from Authorization header.

    Per security requirements in data-model.md:
    - Validates Bearer token format
    - Validates UUID v4 format
    - Returns parsed UUID for use in endpoints

    Args:
        authorization: Authorization header value (format: "Bearer <uuid>")

    Returns:
        uuid.UUID: Validated device token

    Raises:
        HTTPException: 401 if token is missing or invalid

    Usage in endpoints:
        @app.get("/tasks")
        async def list_tasks(device_token: UUID = Depends(get_device_token)):
            ...
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing device token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_str = parts[1]

    # Validate UUID format
    try:
        device_token = uuid.UUID(token_str, version=4)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid device token format. Expected UUID v4",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return device_token
