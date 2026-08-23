from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from app.database.database import (
    Base,
    utc_now,
)


def generate_execution_uid() -> str:
    return (
        f"exec_{uuid.uuid4().hex[:12]}"
    )


class CEOExecutionRecord(Base):
    """
    Persistent audit record for a CEO-approved
    executive-plan execution.

    Approval state remains in CEOApproval. This
    model records what happened after execution
    was attempted.
    """

    __tablename__ = "ceo_execution_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    execution_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=generate_execution_uid,
    )

    approval_uid = Column(
        String,
        nullable=False,
        index=True,
    )

    mission_id = Column(
        String,
        nullable=True,
        index=True,
    )

    workflow_id = Column(
        String,
        nullable=True,
        index=True,
    )

    objective = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="completed",
        index=True,
    )

    success = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    completed_task_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    failed_task_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    error = Column(
        Text,
        nullable=True,
    )

    result_json = Column(
        Text,
        nullable=True,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        index=True,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )