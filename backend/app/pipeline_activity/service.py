from typing import Any

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.pipeline_activity.models import (
    PipelineActivity,
)


def serialize_pipeline_activity(
    activity: PipelineActivity,
) -> dict[str, Any]:
    return {
        "activity_uid": activity.activity_uid,
        "lead_id": activity.lead_id,
        "lead_name": activity.lead_name,
        "previous_status": (
            activity.previous_status
        ),
        "new_status": activity.new_status,
        "changed_by": activity.changed_by,
        "source": activity.source,
        "notes": activity.notes,
        "created_at": activity.created_at,
    }


def record_pipeline_activity(
    db: Session,
    *,
    lead_id: int,
    lead_name: str,
    previous_status: str,
    new_status: str,
    changed_by: str = "CRM User",
    source: str = "CRM Pipeline",
    notes: str | None = None,
) -> PipelineActivity:
    activity = PipelineActivity(
        lead_id=lead_id,
        lead_name=str(lead_name).strip(),
        previous_status=previous_status,
        new_status=new_status,
        changed_by=changed_by,
        source=source,
        notes=notes,
    )

    db.add(activity)
    db.flush()

    return activity


def list_pipeline_activities(
    *,
    lead_id: int | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    db = SessionLocal()

    try:
        query = db.query(
            PipelineActivity
        )

        if lead_id is not None:
            query = query.filter(
                PipelineActivity.lead_id
                == lead_id
            )

        activities = (
            query.order_by(
                PipelineActivity
                .created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return [
            serialize_pipeline_activity(
                activity
            )
            for activity in activities
        ]

    finally:
        db.close()