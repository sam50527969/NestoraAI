from datetime import datetime
from typing import Any

from app.database.database import SessionLocal
from app.database.models import Lead
from app.follow_up_activity.models import (
    FollowUpActivity,
)
from app.follow_up_activity.schemas import (
    FollowUpOutcomeCreate,
)


OUTCOME_STATUS_MAP = {
    "contacted": "Contacted",
    "qualified": "Qualified",
    "won": "Won",
    "lost": "Lost",
    "no_response": "Contacted",
}


def serialize_follow_up_activity(
    activity: FollowUpActivity,
) -> dict[str, Any]:
    return {
        "activity_uid": activity.activity_uid,
        "lead_id": activity.lead_id,
        "lead_name": activity.lead_name,
        "outcome": activity.outcome,
        "notes": activity.notes,
        "previous_status": (
            activity.previous_status
        ),
        "new_status": activity.new_status,
        "previous_follow_up": (
            activity.previous_follow_up
        ),
        "next_follow_up": (
            activity.next_follow_up
        ),
        "completed_by": (
            activity.completed_by
        ),
        "created_at": activity.created_at,
    }


def record_follow_up_outcome(
    lead_id: int,
    data: FollowUpOutcomeCreate,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if lead is None:
            raise LookupError(
                "CRM lead was not found."
            )

        outcome = data.outcome.strip().lower()

        if (
            outcome == "rescheduled"
            and not data.next_follow_up
        ):
            raise ValueError(
                "A new follow-up date is required "
                "when rescheduling."
            )

        previous_status = lead.status
        previous_follow_up = (
            lead.next_follow_up
        )

        new_status = OUTCOME_STATUS_MAP.get(
            outcome,
            lead.status,
        )

        now = datetime.utcnow()

        if outcome != "rescheduled":
            lead.status = new_status
            lead.last_contacted = (
                now.isoformat()
            )

        if outcome in {
            "won",
            "lost",
        }:
            lead.next_follow_up = None
        elif data.next_follow_up:
            lead.next_follow_up = (
                data.next_follow_up.strip()
            )
        else:
            lead.next_follow_up = None

        activity = FollowUpActivity(
            lead_id=lead.id,
            lead_name=str(lead.name).strip(),
            outcome=outcome,
            notes=(
                data.notes.strip()
                if data.notes
                else None
            ),
            previous_status=previous_status,
            new_status=lead.status,
            previous_follow_up=(
                previous_follow_up
            ),
            next_follow_up=(
                lead.next_follow_up
            ),
            completed_by=(
                data.completed_by.strip()
                or "CEO"
            ),
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)

        return serialize_follow_up_activity(
            activity
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def list_follow_up_activities(
    *,
    lead_id: int | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    db = SessionLocal()

    try:
        query = db.query(
            FollowUpActivity
        )

        if lead_id is not None:
            query = query.filter(
                FollowUpActivity.lead_id
                == lead_id
            )

        activities = (
            query.order_by(
                FollowUpActivity
                .created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return [
            serialize_follow_up_activity(
                activity
            )
            for activity in activities
        ]

    finally:
        db.close()