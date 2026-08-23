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