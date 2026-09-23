"""Database engine, session factory and declarative base.

One engine/session factory for the whole app. `SessionLocal()` opens a short-lived session;
callers use it as a context manager and commit explicitly. `init_db()` creates the tables from
the ORM models (simple create_all; a real deployment would use Alembic migrations).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import settings

# future=True -> SQLAlchemy 2.0 behavior. pool_pre_ping avoids stale connections after restarts.
engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent of every ORM model; holds the shared metadata (the table registry)."""


def init_db() -> None:
    """Create all tables that don't yet exist."""
    # Import models so they register on Base.metadata before create_all runs.
    from app.db import models  # noqa: F401

    Base.metadata.create_all(engine)
