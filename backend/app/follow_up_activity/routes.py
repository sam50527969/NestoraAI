import csv
from datetime import datetime
from io import StringIO

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from fastapi.responses import Response

from app.follow_up_activity.schemas import (
    FollowUpActivityResponse,
    FollowUpOutcomeCreate,
)
from app.follow_up_activity.service import (
    get_follow_up_metrics,
    list_follow_up_activities,
    record_follow_up_outcome,
)


router = APIRouter(
    prefix="/follow-up-activities",
    tags=["CRM Follow-up Activities"],
)


def make_csv_safe(value) -> str:
    text = str(
        value
        if value is not None
        else ""
    )

    if text.startswith(
        ("=", "+", "-", "@")
    ):
        return f"'{text}"

    return text


@router.get("/metrics")
def read_follow_up_metrics(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    return get_follow_up_metrics(
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/export")
def export_follow_up_history(
    lead_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(
        default=500,
        ge=1,
        le=500,
    ),
):
    activities = list_follow_up_activities(
        lead_id=lead_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "Activity UID",
            "Lead ID",
            "Lead Name",
            "Outcome",
            "Previous Status",
            "New Status",
            "Previous Follow-up",
            "Next Follow-up",
            "Notes",
            "Completed By",
            "Created At",
        ]
    )

    for activity in activities:
        writer.writerow(
            [
                make_csv_safe(
                    activity.get(
                        "activity_uid"
                    )
                ),
                activity.get(
                    "lead_id"
                ),
                make_csv_safe(
                    activity.get(
                        "lead_name"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "outcome"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "previous_status"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "new_status"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "previous_follow_up"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "next_follow_up"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "notes"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "completed_by"
                    )
                ),
                make_csv_safe(
                    activity.get(
                        "created_at"
                    )
                ),
            ]
        )

    filename = (
        "nestora-follow-up-history.csv"
    )

    return Response(
        content=output.getvalue(),
        media_type=(
            "text/csv; charset=utf-8"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )


@router.get(
    "",
    response_model=list[
        FollowUpActivityResponse
    ],
)
def list_activity_history(
    lead_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    return list_follow_up_activities(
        lead_id=lead_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.post(
    "/leads/{lead_id}/outcome",
    response_model=FollowUpActivityResponse,
)
def create_follow_up_outcome(
    lead_id: int,
    data: FollowUpOutcomeCreate,
):
    try:
        return record_follow_up_outcome(
            lead_id,
            data,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error