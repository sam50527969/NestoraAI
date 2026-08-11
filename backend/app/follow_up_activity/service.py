from datetime import datetime
from typing import Any

from app.database.database import (
    SessionLocal,
)
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
        "activity_uid": (
            activity.activity_uid
        ),
        "lead_id": activity.lead_id,
        "lead_name": activity.lead_name,
        "outcome": activity.outcome,
        "notes": activity.notes,
        "previous_status": (
            activity.previous_status
        ),
        "new_status": (
            activity.new_status
        ),
        "previous_follow_up": (
            activity.previous_follow_up
        ),
        "next_follow_up": (
            activity.next_follow_up
        ),
        "completed_by": (
            activity.completed_by
        ),
        "created_at": (
            activity.created_at
        ),
    }


def apply_activity_date_filters(
    query,
    *,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    if start_date is not None:
        query = query.filter(
            FollowUpActivity.created_at
            >= start_date
        )

    if end_date is not None:
        query = query.filter(
            FollowUpActivity.created_at
            <= end_date
        )

    return query


def record_follow_up_outcome(
    lead_id: int,
    data: FollowUpOutcomeCreate,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        lead = (
            db.query(Lead)
            .filter(
                Lead.id == lead_id
            )
            .first()
        )

        if lead is None:
            raise LookupError(
                "CRM lead was not found."
            )

        outcome = (
            data.outcome
            .strip()
            .lower()
        )

        if (
            outcome == "rescheduled"
            and not data.next_follow_up
        ):
            raise ValueError(
                "A new follow-up date is "
                "required when rescheduling."
            )

        previous_status = lead.status

        previous_follow_up = (
            lead.next_follow_up
        )

        new_status = (
            OUTCOME_STATUS_MAP.get(
                outcome,
                lead.status,
            )
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
            lead_name=str(
                lead.name
            ).strip(),
            outcome=outcome,
            notes=(
                data.notes.strip()
                if data.notes
                else None
            ),
            previous_status=(
                previous_status
            ),
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

        return (
            serialize_follow_up_activity(
                activity
            )
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def list_follow_up_activities(
    *,
    lead_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
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

        query = apply_activity_date_filters(
            query,
            start_date=start_date,
            end_date=end_date,
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


def get_follow_up_metrics(
    *,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        query = db.query(
            FollowUpActivity
        )

        query = apply_activity_date_filters(
            query,
            start_date=start_date,
            end_date=end_date,
        )

        activities = (
            query.order_by(
                FollowUpActivity
                .created_at.desc()
            )
            .all()
        )

        outcome_counts = {
            "contacted": 0,
            "qualified": 0,
            "won": 0,
            "lost": 0,
            "no_response": 0,
            "rescheduled": 0,
        }

        unique_lead_ids = set()

        for activity in activities:
            outcome = str(
                activity.outcome or ""
            ).strip().lower()

            if outcome in outcome_counts:
                outcome_counts[
                    outcome
                ] += 1

            unique_lead_ids.add(
                activity.lead_id
            )

        actionable_count = sum(
            outcome_counts[outcome]
            for outcome in (
                "contacted",
                "qualified",
                "won",
                "lost",
                "no_response",
            )
        )

        response_count = sum(
            outcome_counts[outcome]
            for outcome in (
                "contacted",
                "qualified",
                "won",
                "lost",
            )
        )

        response_rate = (
            round(
                response_count
                / actionable_count
                * 100
            )
            if actionable_count
            else 0
        )

        win_rate = (
            round(
                outcome_counts["won"]
                / actionable_count
                * 100
            )
            if actionable_count
            else 0
        )

        return {
            "total_activities": len(
                activities
            ),
            "unique_leads": len(
                unique_lead_ids
            ),
            "response_count": (
                response_count
            ),
            "response_rate": (
                response_rate
            ),
            "win_rate": win_rate,
            "outcomes": outcome_counts,
        }

    finally:
        db.close()