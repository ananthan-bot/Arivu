"""
SQLAlchemy engine/session setup.

Repositories depend on `get_db` (a generator dependency), never on the
engine directly — keeps DB wiring swappable and testable.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db() -> Generator:
    """FastAPI dependency yielding a DB session, closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
