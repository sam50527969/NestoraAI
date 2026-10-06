from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.business.access import get_current_business_uid
from app.database.database import get_db
from sqlalchemy.orm import Session

from app.pipeline_activity.schemas import (
    PipelineActivityResponse,
)
from app.pipeline_activity.service import (
    list_pipeline_activities,
)


router = APIRouter(
    prefix="/pipeline-activities",
    tags=["CRM Pipeline Activities"],
)


@router.get(
    "",
    response_model=list[
        PipelineActivityResponse
    ],
)
def list_activity_history(
    business_uid: str = Depends(get_current_business_uid),
    db: Session = Depends(get_db),
    lead_id: int | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    return list_pipeline_activities(
        db=db,
        business_uid=business_uid,
        lead_id=lead_id,
        limit=limit,
    )