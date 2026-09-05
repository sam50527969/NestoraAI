from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database.database import Base


class ExecutiveMessage(Base):
    __tablename__ = "executive_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_uid = Column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: f"msg_{uuid.uuid4().hex[:12]}",
    )
    conversation_uid = Column(
        String(64),
        index=True,
        nullable=False,
        default=lambda: f"con_{uuid.uuid4().hex[:12]}",
    )
    mission_uid = Column(String(64), index=True, nullable=True)
    business_uid = Column(String(64), index=True, nullable=True)
    sender = Column(String(100), index=True, nullable=False)
    recipient = Column(String(100), index=True, nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(
        String(50), index=True, nullable=False, default="message"
    )
    priority = Column(
        String(20), index=True, nullable=False, default="normal"
    )
    status = Column(
        String(30), index=True, nullable=False, default="sent"
    )
    is_read = Column(Boolean, nullable=False, default=False)
    parent_message_uid = Column(String(64), index=True, nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    read_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
