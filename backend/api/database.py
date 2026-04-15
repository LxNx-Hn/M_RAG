"""
Database connection utilities.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{Path(__file__).parent.parent / 'mrag.db'}",
)

_engine = None
_SessionLocal = None


def get_sync_database_url() -> str:
    """Return a sync SQLAlchemy URL for Alembic and ops tooling."""
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        return DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://", 1
        )
    if DATABASE_URL.startswith("sqlite+aiosqlite://"):
        return DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return DATABASE_URL


def get_engine():
    global _engine
    if _engine is not None:
        return _engine
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        engine_kwargs = {"echo": False}
        if not DATABASE_URL.startswith("sqlite"):
            engine_kwargs.update(
                {
                    "pool_size": int(os.environ.get("DB_POOL_SIZE", "20")),
                    "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
                    "pool_pre_ping": True,
                    "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
                }
            )
        _engine = create_async_engine(DATABASE_URL, **engine_kwargs)
        return _engine
    except ImportError:
        logger.warning("SQLAlchemy not installed, DB features disabled")
        return None


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal
    try:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        engine = get_engine()
        if engine is None:
            return None
        _SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
        return _SessionLocal
    except ImportError:
        return None


async def init_db():
    """Create tables when needed."""
    engine = get_engine()
    if engine is None:
        logger.warning("DB engine not available, skipping table creation")
        return
    try:
        from api.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as exc:
        logger.warning("DB init failed (non-critical): %s", exc)


async def get_db():
    """FastAPI dependency for DB session."""
    factory = get_session_factory()
    if factory is None:
        yield None
        return
    async with factory() as session:
        yield session
