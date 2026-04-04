"""
데이터베이스 연결 (SQLite 기본, PostgreSQL 옵션)
포트폴리오 환경에서는 SQLite로 충분, 프로덕션에서 PostgreSQL 전환 가능
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# SQLite 기본 (별도 설치 불필요), PostgreSQL은 DATABASE_URL 환경변수로 전환
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{Path(__file__).parent.parent / 'mrag.db'}"
)

# SQLAlchemy 사용 가능 여부 확인
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        _engine = create_async_engine(DATABASE_URL, echo=False)
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
    """테이블 생성"""
    engine = get_engine()
    if engine is None:
        logger.warning("DB engine not available, skipping table creation")
        return
    try:
        from api.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as e:
        logger.warning(f"DB init failed (non-critical): {e}")


async def get_db():
    """FastAPI Depends용 DB 세션"""
    factory = get_session_factory()
    if factory is None:
        yield None
        return
    async with factory() as session:
        yield session
