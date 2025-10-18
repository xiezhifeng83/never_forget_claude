"""
Never Forget Claude - Backend API

FastAPI application entry point with CORS middleware.
Per plan.md: Python 3.11+ with FastAPI 0.104+
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os

from backend.src.database import init_db, close_db
from backend.src.api.health import router as health_router
from backend.src.api.tasks import router as tasks_router
from backend.src.api.sync import router as sync_router
from backend.src.middleware.error_handler import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from backend.src.middleware.logging import log_requests

# Initialize FastAPI application
app = FastAPI(
    title="Never Forget Claude API",
    description="Cross-platform todo list synchronization API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
# Per constitution: support cross-platform clients (Android, Windows)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,app://android").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers including Authorization
)

# Add request logging middleware
app.middleware("http")(log_requests)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register routers
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(sync_router)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Initializes database connection pool and creates tables if needed.
    """
    await init_db()
    print("[OK] Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.

    Cleanly closes database connections.
    """
    await close_db()
    print("[OK] Database connections closed")


@app.get("/")
async def root():
    """
    Root endpoint - API welcome message.

    Returns:
        dict: Welcome message with API information
    """
    return {
        "message": "Never Forget Claude API",
        "version": "1.0.0",
        "docs": "/docs",
    }
