from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from app.database.database import (
    SessionLocal,
    utc_now,
)
from app.database.models import Lead
from app.outreach_activity.models import (
    OutreachActivity,
)
from app.pipeline_activity.service import (
    record_pipeline_activity,
)


DEFAULT_FOLLOW_UP_DAYS = 2

TERMINAL_LEAD_STATUSES = {
    "won",
    "lost",
}


def serialize_outreach_activity(
    activity: OutreachActivity,
) -> dict[str, Any]:
    return {
        "activity_uid": (
            activity.activity_uid
        ),
        "approval_uid": (
            activity.approval_uid
        ),
        "lead_id": activity.lead_id,
        "lead_name": activity.lead_name,
        "status": activity.status,
        "prepared_by": (
            activity.prepared_by
        ),
        "phone": activity.phone,
        "website": activity.website,
        "email_subject": (
            activity.email_subject
        ),
        "email_body": (
            activity.email_body
        ),
        "whatsapp_message": (
            activity.whatsapp_message
        ),
        "cold_call_script": (
            activity.cold_call_script
        ),
        "proposal_summary": (
            activity.proposal_summary
        ),
        "created_at": (
            activity.created_at
        ),
        "updated_at": (
            activity.updated_at
        ),
        "sent_at": activity.sent_at,
    }


def save_prepared_outreach(
    db,
    *,
    approval_uid: str,
    lead,
    outreach,
) -> OutreachActivity:
    existing_activity = (
        db.query(OutreachActivity)
        .filter(
            OutreachActivity.approval_uid
            == approval_uid,
            OutreachActivity.lead_id
            == lead.id,
        )
        .first()
    )

    if existing_activity is not None:
        return existing_activity

    activity = OutreachActivity(
        approval_uid=approval_uid,
        lead_id=lead.id,
        lead_name=str(
            lead.name
        ).strip(),
        status="prepared",
        prepared_by="CEO Agent",
        phone=lead.phone,
        website=lead.website,
        email_subject=(
            outreach.email_subject
        ),
        email_body=(
            outreach.email_body
        ),
        whatsapp_message=(
            outreach.whatsapp_message
        ),
        cold_call_script=(
            outreach.cold_call_script
        ),
        proposal_summary=(
            outreach.proposal_summary
        ),
    )

    db.add(activity)
    db.flush()

    return activity


def list_outreach_activities(
    *,
    status: str | None = None,
    approval_uid: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    db = SessionLocal()

    try:
        query = db.query(
            OutreachActivity
        )

        if status:
            query = query.filter(
                OutreachActivity.status
                == status.strip().lower()
            )

        if approval_uid:
            query = query.filter(
                OutreachActivity.approval_uid
                == approval_uid.strip()
            )

        activities = (
            query.order_by(
                OutreachActivity
                .created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return [
            serialize_outreach_activity(
                activity
            )
            for activity in activities
        ]

    finally:
        db.close()


def get_outreach_activity(
    activity_uid: str,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        activity = (
            db.query(OutreachActivity)
            .filter(
                OutreachActivity.activity_uid
                == activity_uid
            )
            .first()
        )

        if activity is None:
            raise LookupError(
                "Outreach activity was "
                "not found."
            )

        return (
            serialize_outreach_activity(
                activity
            )
        )

    finally:
        db.close()


def synchronize_lead_contact(
    db,
    *,
    activity: OutreachActivity,
    contacted_at: datetime,
) -> None:
    lead = (
        db.query(Lead)
        .filter(
            Lead.id
            == activity.lead_id
        )
        .first()
    )

    if lead is None:
        return

    previous_status = str(
        lead.status or "New"
    ).strip()

    normalized_status = (
        previous_status.lower()
    )

    if normalized_status == "new":
        lead.status = "Contacted"

    lead.last_contacted = (
        contacted_at.isoformat()
    )

    if (
        normalized_status
        not in TERMINAL_LEAD_STATUSES
    ):
        follow_up_at = (
            contacted_at
            + timedelta(
                days=(
                    DEFAULT_FOLLOW_UP_DAYS
                ),
            )
        )

        lead.next_follow_up = (
            follow_up_at.isoformat()
        )

    if lead.status != previous_status:
        record_pipeline_activity(
            db,
            lead_id=lead.id,
            lead_name=lead.name,
            previous_status=(
                previous_status
            ),
            new_status=lead.status,
            changed_by=(
                activity.prepared_by
                or "CEO Agent"
            ),
            source="Sent Outreach",
            notes=(
                "Outreach package "
                f"{activity.activity_uid} "
                "marked as sent."
            ),
        )


def mark_outreach_activity_sent(
    activity_uid: str,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        activity = (
            db.query(OutreachActivity)
            .filter(
                OutreachActivity.activity_uid
                == activity_uid
            )
            .first()
        )

        if activity is None:
            raise LookupError(
                "Outreach activity was "
                "not found."
            )

        if activity.status == "sent":
            return (
                serialize_outreach_activity(
                    activity
                )
            )

        if activity.status != "prepared":
            raise ValueError(
                "Only prepared outreach "
                "can be marked as sent."
            )

        sent_at = utc_now()

        activity.status = "sent"
        activity.sent_at = sent_at

        synchronize_lead_contact(
            db,
            activity=activity,
            contacted_at=sent_at,
        )

        db.commit()
        db.refresh(activity)

        return (
            serialize_outreach_activity(
                activity
            )
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()