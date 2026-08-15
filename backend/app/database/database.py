from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)


DATABASE_URL = "sqlite:///./nestora.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)

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