from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

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
):
    try:
        return create_lead(
            db,
            lead,
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
):
    return get_leads(db)


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
):
    return get_due_follow_ups(
        db,
        limit=limit,
    )


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse,
)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = get_lead(
        db,
        lead_id,
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
):
    try:
        updated_lead = update_lead(
            db,
            lead_id,
            lead,
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