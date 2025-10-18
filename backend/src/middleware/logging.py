"""
Request logging middleware.

Logs API requests with masked device tokens for security.
"""

from fastapi import Request
import logging
import time

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)


async def log_requests(request: Request, call_next):
    """
    Log API requests with timing and masked device tokens.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response from next handler
    """
    start_time = time.time()

    # Extract and mask device token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Mask token: show first 8 and last 4 characters
        if len(token) > 12:
            masked_token = f"{token[:8]}...{token[-4:]}"
        else:
            masked_token = "***"
    else:
        masked_token = "none"

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.3f}s "
        f"token={masked_token}"
    )

    return response
