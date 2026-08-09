import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
)

from app.database.database import Base


class CEOApproval(Base):
    __tablename__ = "ceo_approvals"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    approval_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: (
            f"apr_{uuid.uuid4().hex[:12]}"
        ),
    )

    decision_type = Column(
        String,
        nullable=False,
        default="executive_action",
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    source_type = Column(
        String,
        nullable=False,
        default="executive_report",
        index=True,
    )

    source_uid = Column(
        String,
        nullable=True,
        index=True,
    )

    status = Column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )

    requested_by = Column(
        String,
        nullable=False,
        default="CEO Agent",
    )

    reviewed_by = Column(
        String,
        nullable=True,
    )

    decision_note = Column(
        Text,
        nullable=True,
    )

    payload_json = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    reviewed_at = Column(
        DateTime,
        nullable=True,
    )

    executed_at = Column(
        DateTime,
        nullable=True,
    )