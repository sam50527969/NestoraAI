from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.approvals.executor import (
    execute_approval,
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

from app.business.access import (
    get_current_business_uid,
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
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return create_approval(
        data,
        business_uid=business_uid,
    )


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
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return list_approvals(
        business_uid=business_uid,
        status=approval_status,
        limit=limit,
    )


@router.get(
    "/{approval_uid}",
    response_model=ApprovalResponse,
)
def get_approval_request(
    approval_uid: str,
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        return get_approval(
            approval_uid,
            business_uid=business_uid,
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
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        return decide_approval(
            approval_uid,
            "approved",
            data,
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


@router.post(
    "/{approval_uid}/reject",
    response_model=ApprovalResponse,
)
def reject_request(
    approval_uid: str,
    data: ApprovalDecision,
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        return decide_approval(
            approval_uid,
            "rejected",
            data,
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


@router.post(
    "/{approval_uid}/execute",
    response_model=ApprovalResponse,
)
async def execute_approved_request(
    approval_uid: str,
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        return await execute_approval(
            approval_uid,
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