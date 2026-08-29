from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.database.database import utc_now
from app.execution_history.models import (
    CEOExecutionRecord,
)


def save_execution_record(
    db: Session,
    *,
    approval_uid: str,
    objective: str,
    execution_result: dict[str, Any],
) -> CEOExecutionRecord:
    """
    Persist the result of an approved CEO
    executive-plan execution.

    One execution record is allowed for each
    approval request.
    """

    existing = (
        db.query(CEOExecutionRecord)
        .filter(
            CEOExecutionRecord.approval_uid
            == approval_uid
        )
        .first()
    )

    if existing is not None:
        return existing

    success = bool(
        execution_result.get(
            "success",
            False,
        )
    )

    status = str(
        execution_result.get(
            "status",
            (
                "completed"
                if success
                else "failed"
            ),
        )
    )

    now = utc_now()

    record = CEOExecutionRecord(
        approval_uid=approval_uid,
        mission_id=execution_result.get(
            "mission_id"
        ),
        workflow_id=execution_result.get(
            "workflow_id"
        ),
        objective=objective,
        status=status,
        success=success,
        completed_task_count=int(
            execution_result.get(
                "completed_task_count",
                0,
            )
            or 0
        ),
        failed_task_count=int(
            execution_result.get(
                "failed_task_count",
                0,
            )
            or 0
        ),
        error=execution_result.get(
            "error"
        ),
        result_json=json.dumps(
            execution_result,
            ensure_ascii=False,
            default=str,
        ),
        started_at=now,
        completed_at=now,
    )

    db.add(record)
    db.flush()
    db.refresh(record)

    return record


def get_execution_record(
    db: Session,
    execution_uid: str,
) -> CEOExecutionRecord | None:
    """Return one execution record by UID."""

    return (
        db.query(CEOExecutionRecord)
        .filter(
            CEOExecutionRecord.execution_uid
            == execution_uid
        )
        .first()
    )


def get_execution_record_by_approval(
    db: Session,
    approval_uid: str,
) -> CEOExecutionRecord | None:
    """Return the execution for an approval."""

    return (
        db.query(CEOExecutionRecord)
        .filter(
            CEOExecutionRecord.approval_uid
            == approval_uid
        )
        .first()
    )


def list_execution_records(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[CEOExecutionRecord]:
    """Return recent CEO executions."""

    safe_limit = max(
        1,
        min(limit, 100),
    )

    safe_offset = max(
        0,
        offset,
    )

    return (
        db.query(CEOExecutionRecord)
        .order_by(
            CEOExecutionRecord.created_at.desc(),
            CEOExecutionRecord.id.desc(),
        )
        .offset(safe_offset)
        .limit(safe_limit)
        .all()
    )