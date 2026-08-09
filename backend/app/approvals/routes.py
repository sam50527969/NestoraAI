from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from app.approvals.schemas import (
    ApprovalCreate,
    ApprovalDecision,
    ApprovalResponse,
)
from app.approvals.service import (
    create_approval,
    decide_approval,
    get_approval,
    list_approvals,
)


router = APIRouter(
    prefix="/ceo-approvals",
    tags=["CEO Approvals"],
)


@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_approval_request(
    data: ApprovalCreate,
):
    return create_approval(data)


@router.get(
    "",
    response_model=list[ApprovalResponse],
)
def get_approval_requests(
    approval_status: str | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):
    return list_approvals(
        status=approval_status,
        limit=limit,
    )


@router.get(
    "/{approval_uid}",
    response_model=ApprovalResponse,
)
def get_approval_request(
    approval_uid: str,
):
    try:
        return get_approval(
            approval_uid
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.post(
    "/{approval_uid}/approve",
    response_model=ApprovalResponse,
)
def approve_request(
    approval_uid: str,
    data: ApprovalDecision,
):
    try:
        return decide_approval(
            approval_uid,
            "approved",
            data,
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


@router.post(
    "/{approval_uid}/reject",
    response_model=ApprovalResponse,
)
def reject_request(
    approval_uid: str,
    data: ApprovalDecision,
):
    try:
        return decide_approval(
            approval_uid,
            "rejected",
            data,
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