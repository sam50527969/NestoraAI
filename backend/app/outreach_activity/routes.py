from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.outreach_activity.schemas import (
    OutreachActivityResponse,
)
from app.outreach_activity.service import (
    get_outreach_activity,
    list_outreach_activities,
)


router = APIRouter(
    prefix="/outreach-activities",
    tags=["Outreach Activities"],
)


@router.get(
    "",
    response_model=list[
        OutreachActivityResponse
    ],
)
def list_activity_history(
    status: str | None = None,
    approval_uid: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    return list_outreach_activities(
        status=status,
        approval_uid=approval_uid,
        limit=limit,
    )


@router.get(
    "/{activity_uid}",
    response_model=OutreachActivityResponse,
)
def get_activity(
    activity_uid: str,
):
    try:
        return get_outreach_activity(
            activity_uid
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error