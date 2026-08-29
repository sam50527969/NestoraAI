from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.business.access import (
    get_current_business_uid,
)
from app.database.database import get_db
from app.schemas.crm import (
    LeadCreate,
    LeadResponse,
    LeadUpdate,
)
from app.services.crm_service import (
    create_lead,
    get_due_follow_ups,
    get_lead,
    get_leads,
    get_pipeline_summary,
    update_lead,
)


router = APIRouter(
    prefix="/crm",
    tags=["CRM"],
)


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        scoped_lead = lead.model_copy(
            update={
                "business_uid": business_uid,
            }
        )

        return create_lead(
            db,
            scoped_lead,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.get(
    "/leads",
    response_model=list[LeadResponse],
)
def list_leads(
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return get_leads(
        db,
        business_uid=business_uid,
    )


@router.get(
    "/follow-ups/due",
    response_model=list[LeadResponse],
)
def list_due_follow_ups(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return get_due_follow_ups(
        db,
        limit=limit,
        business_uid=business_uid,
    )


@router.get(
    "/pipeline/summary"
)
def read_pipeline_summary(
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return get_pipeline_summary(
        db,
        business_uid=business_uid,
    )


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse,
)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    lead = get_lead(
        db,
        lead_id,
        business_uid=business_uid,
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return lead


@router.put(
    "/leads/{lead_id}",
    response_model=LeadResponse,
)
def edit_lead(
    lead_id: int,
    lead: LeadUpdate,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    try:
        updated_lead = update_lead(
            db,
            lead_id,
            lead,
            business_uid=business_uid,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if not updated_lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return updated_lead
