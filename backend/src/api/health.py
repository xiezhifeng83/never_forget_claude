"""
Health check endpoint.

Per contracts/openapi.yaml: /health endpoint for API status monitoring.
No authentication required.
"""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns API status and current server timestamp.
    Used by monitoring systems and clients to verify API availability.

    No authentication required per openapi.yaml specification.

    Returns:
        dict: Health status and timestamp

    Example response:
        {
            "status": "ok",
            "timestamp": "2025-10-17T10:30:05Z"
        }
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
