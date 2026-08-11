from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.follow_up_activity.schemas import (
    FollowUpActivityResponse,
    FollowUpOutcomeCreate,
)
from app.follow_up_activity.service import (
    list_follow_up_activities,
    record_follow_up_outcome,
)


router = APIRouter(
    prefix="/follow-up-activities",
    tags=["CRM Follow-up Activities"],
)


@router.get(
    "",
    response_model=list[
        FollowUpActivityResponse
    ],
)
def list_activity_history(
    lead_id: int | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    return list_follow_up_activities(
        lead_id=lead_id,
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