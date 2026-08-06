from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import time
import logging

logger = logging.getLogger(__name__)

# Engine configuration with robust production pooling parameters
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


def get_db():
    """Dependency to retrieve database session with automatic lifecycle cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection(retries: int = 3, delay: float = 1.0) -> bool:
    """Simple helper to test DB connectivity with a small retry loop.

    Returns True on success, False on failure.
    """
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connectivity test succeeded.")
            return True
        except Exception as exc:
            logger.warning(f"DB connect attempt {attempt}/{retries} failed: {exc}")
            time.sleep(delay)
    logger.error("Database connectivity test failed after retries.")
    return False
