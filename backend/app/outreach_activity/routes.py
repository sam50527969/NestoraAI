from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.business.access import get_current_business_uid

from app.outreach_activity.schemas import (
    OutreachActivityResponse,
)
from app.outreach_activity.service import (
    get_outreach_activity,
    list_outreach_activities,
    mark_outreach_activity_sent,
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
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return list_outreach_activities(
        business_uid=business_uid,
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
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        return get_outreach_activity(
            activity_uid,
            business_uid=business_uid,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.post(
    "/{activity_uid}/mark-sent",
    response_model=OutreachActivityResponse,
)
def mark_activity_sent(
    activity_uid: str,
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        return mark_outreach_activity_sent(
            activity_uid,
            business_uid=business_uid,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error