from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class PipelineActivityResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    activity_uid: str
    lead_id: int
    lead_name: str
    previous_status: str
    new_status: str
    changed_by: str
    source: str
    notes: str | None = None
    created_at: datetime