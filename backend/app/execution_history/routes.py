from __future__ import annotations

import json
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.business.access import (
    get_current_business_uid,
)
from app.database.database import get_db
from app.execution_history.models import (
    CEOExecutionRecord,
)
from app.execution_history.schemas import (
    CEOExecutionDetailResponse,
    CEOExecutionListResponse,
    CEOExecutionResponse,
)
from app.execution_history.service import (
    get_execution_record,
    get_execution_record_by_approval,
    list_execution_records,
)


router = APIRouter(
    prefix="/ceo-executions",
    tags=["CEO Execution History"],
)


def _execution_response(
    record: CEOExecutionRecord,
) -> CEOExecutionResponse:
    return CEOExecutionResponse.model_validate(
        record
    )


def _execution_detail_response(
    record: CEOExecutionRecord,
) -> CEOExecutionDetailResponse:
    result: dict[str, Any] | None = None

    if record.result_json:
        try:
            decoded = json.loads(
                record.result_json
            )

            if isinstance(
                decoded,
                dict,
            ):
                result = decoded
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            result = None

    response = (
        CEOExecutionDetailResponse.model_validate(
            record
        )
    )

    return response.model_copy(
        update={
            "result": result,
        }
    )


@router.get(
    "",
    response_model=CEOExecutionListResponse,
)
def get_execution_history(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
) -> CEOExecutionListResponse:
    records = list_execution_records(
        db,
        business_uid=business_uid,
        limit=limit,
        offset=offset,
    )

    executions = [
        _execution_response(record)
        for record in records
    ]

    return CEOExecutionListResponse(
        executions=executions,
        count=len(executions),
        limit=limit,
        offset=offset,
    )


@router.get(
    "/approval/{approval_uid}",
    response_model=CEOExecutionDetailResponse,
)
def get_execution_for_approval(
    approval_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
) -> CEOExecutionDetailResponse:
    record = (
        get_execution_record_by_approval(
            db,
            approval_uid,
            business_uid=business_uid,
        )
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "CEO execution record "
                "not found."
            ),
        )

    return _execution_detail_response(
        record
    )


@router.get(
    "/{execution_uid}",
    response_model=CEOExecutionDetailResponse,
)
def get_execution(
    execution_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
) -> CEOExecutionDetailResponse:
    record = get_execution_record(
        db,
        execution_uid,
        business_uid=business_uid,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "CEO execution record "
                "not found."
            ),
        )

    return _execution_detail_response(
        record
    )