import json
from typing import Any

from app.approvals.models import CEOApproval
from app.approvals.schemas import (
    ApprovalCreate,
    ApprovalDecision,
)
from app.database.database import (
    SessionLocal,
    utc_now,
)


VALID_DECISIONS = {
    "approved",
    "rejected",
}

ACTIVE_APPROVAL_STATUSES = {
    "pending",
    "approved",
}


def normalize_text(
    value: Any,
) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def parse_payload(
    value: str | None,
) -> dict[str, Any] | None:
    if not value:
        return None

    try:
        parsed_value = json.loads(value)
    except (TypeError, ValueError):
        return {
            "value": value,
        }

    if isinstance(parsed_value, dict):
        return parsed_value

    return {
        "value": parsed_value,
    }


def serialize_approval(
    approval: CEOApproval,
) -> dict[str, Any]:
    return {
        "approval_uid": (
            approval.approval_uid
        ),
        "decision_type": (
            approval.decision_type
        ),
        "title": approval.title,
        "description": (
            approval.description
        ),
        "source_type": (
            approval.source_type
        ),
        "source_uid": (
            approval.source_uid
        ),
        "status": approval.status,
        "requested_by": (
            approval.requested_by
        ),
        "reviewed_by": (
            approval.reviewed_by
        ),
        "decision_note": (
            approval.decision_note
        ),
        "payload": parse_payload(
            approval.payload_json
        ),
        "created_at": (
            approval.created_at
        ),
        "updated_at": (
            approval.updated_at
        ),
        "reviewed_at": (
            approval.reviewed_at
        ),
        "executed_at": (
            approval.executed_at
        ),
    }


def find_active_duplicate(
    db,
    data: ApprovalCreate,
) -> CEOApproval | None:
    decision_type = (
        data.decision_type.strip()
        or "executive_action"
    )

    source_type = (
        data.source_type.strip()
        or "executive_report"
    )

    source_uid = (
        data.source_uid.strip()
        if data.source_uid
        else None
    )

    title = data.title.strip()

    description = (
        data.description.strip()
        if data.description
        else None
    )

    query = db.query(
        CEOApproval
    ).filter(
        CEOApproval.status.in_(
            ACTIVE_APPROVAL_STATUSES
        ),
        CEOApproval.decision_type
        == decision_type,
        CEOApproval.source_type
        == source_type,
        CEOApproval.title
        == title,
    )

    if source_uid is None:
        query = query.filter(
            CEOApproval.source_uid.is_(
                None
            )
        )
    else:
        query = query.filter(
            CEOApproval.source_uid
            == source_uid
        )

    candidates = (
        query.order_by(
            CEOApproval.created_at.desc()
        )
        .all()
    )

    normalized_description = (
        normalize_text(description)
    )

    for approval in candidates:
        if (
            normalize_text(
                approval.description
            )
            == normalized_description
        ):
            return approval

    return None


def create_approval(
    data: ApprovalCreate,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        existing_approval = (
            find_active_duplicate(
                db,
                data,
            )
        )

        if existing_approval is not None:
            return serialize_approval(
                existing_approval
            )

        approval = CEOApproval(
            title=data.title.strip(),
            description=(
                data.description.strip()
                if data.description
                else None
            ),
            decision_type=(
                data.decision_type.strip()
                or "executive_action"
            ),
            source_type=(
                data.source_type.strip()
                or "executive_report"
            ),
            source_uid=(
                data.source_uid.strip()
                if data.source_uid
                else None
            ),
            requested_by=(
                data.requested_by.strip()
                or "CEO Agent"
            ),
            status="pending",
            payload_json=(
                json.dumps(
                    data.payload,
                    ensure_ascii=False,
                    default=str,
                )
                if data.payload is not None
                else None
            ),
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        return serialize_approval(
            approval
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def list_approvals(
    status: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    db = SessionLocal()

    try:
        query = db.query(
            CEOApproval
        )

        if status:
            query = query.filter(
                CEOApproval.status
                == status.strip().lower()
            )

        approvals = (
            query.order_by(
                CEOApproval.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return [
            serialize_approval(
                approval
            )
            for approval in approvals
        ]

    finally:
        db.close()


def get_approval(
    approval_uid: str,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        approval = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == approval_uid
            )
            .first()
        )

        if approval is None:
            raise LookupError(
                "Approval request was not found."
            )

        return serialize_approval(
            approval
        )

    finally:
        db.close()


def decide_approval(
    approval_uid: str,
    decision: str,
    data: ApprovalDecision,
) -> dict[str, Any]:
    normalized_decision = (
        decision.strip().lower()
    )

    if (
        normalized_decision
        not in VALID_DECISIONS
    ):
        raise ValueError(
            "Decision must be approved "
            "or rejected."
        )

    db = SessionLocal()

    try:
        approval = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == approval_uid
            )
            .first()
        )

        if approval is None:
            raise LookupError(
                "Approval request was not found."
            )

        if approval.status != "pending":
            raise ValueError(
                "This approval request has "
                "already been reviewed."
            )

        approval.status = (
            normalized_decision
        )

        approval.reviewed_by = (
            data.reviewed_by.strip()
        )

        approval.decision_note = (
            data.decision_note.strip()
            if data.decision_note
            else None
        )

        approval.reviewed_at = utc_now()

        db.commit()
        db.refresh(approval)

        return serialize_approval(
            approval
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()