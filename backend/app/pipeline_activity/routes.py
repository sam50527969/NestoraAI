from fastapi import (
    APIRouter,
    Query,
)

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
    lead_id: int | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    return list_pipeline_activities(
        lead_id=lead_id,
        limit=limit,
    )