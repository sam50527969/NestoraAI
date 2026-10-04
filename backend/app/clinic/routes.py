from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.business.access import get_current_business_uid

from app.clinic.schemas import ClinicLeadCreate, ClinicLeadResponse
from app.clinic.service import ClinicService
from app.database.database import get_db


router = APIRouter(
    prefix="/clinic",
    tags=["Clinic"],
)


@router.post(
    "/leads",
    response_model=ClinicLeadResponse,
    status_code=201,
)
def create_clinic_lead(
    payload: ClinicLeadCreate,
    business_uid: str = Depends(get_current_business_uid),
    db: Session = Depends(get_db),
) -> ClinicLeadResponse:
    return ClinicService.create_lead(
        db=db,
        business_uid=business_uid,
        payload=payload,
    )


@router.get(
    "/leads",
    response_model=list[ClinicLeadResponse],
)
def list_clinic_leads(
    limit: int = Query(default=100, ge=1, le=500),
    business_uid: str = Depends(get_current_business_uid),
    db: Session = Depends(get_db),
) -> list[ClinicLeadResponse]:
    return ClinicService.list_leads(
        db=db,
        business_uid=business_uid,
        limit=limit,
    )


@router.get(
    "/followups/due",
    response_model=list[ClinicLeadResponse],
)
def list_due_followups(
    business_uid: str = Depends(get_current_business_uid),
    db: Session = Depends(get_db),
) -> list[ClinicLeadResponse]:
    return ClinicService.get_followups_due(db=db, business_uid=business_uid)


@router.patch(
    "/leads/{lead_id}/contacted",
    response_model=ClinicLeadResponse,
)
def mark_lead_contacted(
    lead_id: int,
    business_uid: str = Depends(get_current_business_uid),
    db: Session = Depends(get_db),
) -> ClinicLeadResponse:
    lead = ClinicService.mark_contacted(
        db=db,
        business_uid=business_uid,
        lead_id=lead_id,
    )

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Clinic lead not found.",
        )

    return lead


@router.patch(
    "/leads/{lead_id}/appointment-booked",
    response_model=ClinicLeadResponse,
)
def mark_appointment_booked(
    lead_id: int,
    business_uid: str = Depends(get_current_business_uid),
    db: Session = Depends(get_db),
) -> ClinicLeadResponse:
    lead = ClinicService.mark_appointment_booked(
        db=db,
        business_uid=business_uid,
        lead_id=lead_id,
    )

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Clinic lead not found.",
        )

    return lead