"""
Database connection and session management.

Per data-model.md:
- PostgreSQL 15+ backend
- Async SQLAlchemy 2.0
- Connection pooling for performance
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/neverforget"
)

# Create async engine with connection pooling
# SQLite doesn't support pool_size and max_overflow
engine_kwargs = {
    "echo": False,  # Set to True for SQL query logging during development
}

if DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": 10,  # Maximum number of connections in the pool
        "max_overflow": 20,  # Maximum overflow connections
        "pool_pre_ping": True,  # Verify connections before using them
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session for request handling

    Usage in FastAPI endpoints:
        @app.get("/tasks")
        async def list_tasks(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.

    Creates all tables defined in SQLAlchemy models.
    Called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections.

    Called on application shutdown to cleanly close connection pool.
    """
    await engine.dispose()
