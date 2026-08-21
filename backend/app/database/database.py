from datetime import UTC, datetime

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)

from app.config import DATABASE_URL
from app.database.configuration import create_database_engine

engine = create_database_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def utc_now() -> datetime:
    """
    Return the current UTC time as a
    timezone-naive datetime.

    Existing SQLite DateTime columns use
    naive values, so this preserves database
    compatibility while avoiding the
    deprecated datetime.utcnow().
    """

    return (
        datetime.now(UTC)
        .replace(tzinfo=None)
    )


import app.memory.models  # noqa: E402


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
