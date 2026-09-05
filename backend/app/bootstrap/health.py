from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import engine


router = APIRouter(tags=["System"])


@router.get("/health")
def health() -> dict[str, str]:
    """Return process liveness without requiring external dependencies."""

    return {
        "status": "ok",
        "service": "nestora-backend",
    }


@router.get("/ready")
def readiness() -> dict[str, str]:
    """Return readiness only when the configured database is reachable."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable.",
        ) from exc

    return {
        "status": "ready",
        "database": "available",
    }
