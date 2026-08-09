from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database.database import Base


class CollaborationSession(Base):
    __tablename__ = "collaboration_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_uid = Column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: f"col_{uuid.uuid4().hex[:12]}",
    )

    mission_uid = Column(
        String(64),
        index=True,
        nullable=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    objective = Column(
        Text,
        nullable=False,
    )

    owner = Column(
        String(100),
        index=True,
        nullable=False,
        default="CEO",
    )

    status = Column(
        String(30),
        index=True,
        nullable=False,
        default="open",
    )

    participants_json = Column(
        Text,
        nullable=False,
        default="[]",
    )

    shared_context_json = Column(
        Text,
        nullable=False,
        default="{}",
    )

    final_decision = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )


class CollaborationContribution(Base):
    __tablename__ = "collaboration_contributions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    contribution_uid = Column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: f"ctr_{uuid.uuid4().hex[:12]}",
    )

    session_uid = Column(
        String(64),
        index=True,
        nullable=False,
    )

    executive = Column(
        String(100),
        index=True,
        nullable=False,
    )

    contribution_type = Column(
        String(50),
        index=True,
        nullable=False,
        default="recommendation",
    )

    content = Column(
        Text,
        nullable=False,
    )

    metadata_json = Column(
        Text,
        nullable=False,
        default="{}",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
