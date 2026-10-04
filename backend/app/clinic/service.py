from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.clinic.models import ClinicLead
from app.clinic.schemas import ClinicLeadCreate


class ClinicService:
    """
    Handles clinic enquiry creation, retrieval, and follow-up logic.
    """

    ACTIVE_STATUSES = {
        "New",
        "Contacted",
        "Interested",
        "Follow-up Due",
    }

    @staticmethod
    def create_lead(
        db: Session,
        business_uid: str,
        payload: ClinicLeadCreate,
    ) -> ClinicLead:
        lead = ClinicLead(
            business_uid=business_uid,
            patient_name=payload.patient_name.strip(),
            phone=payload.phone.strip(),
            treatment=payload.treatment.strip(),
            source=(payload.source or "WhatsApp").strip(),
            status="New",
            assigned_to="Reception",
            next_followup=datetime.now(timezone.utc) + timedelta(hours=24),
            notes=payload.notes,
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead

    @staticmethod
    def list_leads(
        db: Session,
        business_uid: str,
        limit: int = 100,
    ) -> list[ClinicLead]:
        return (
            db.query(ClinicLead)
            .filter(ClinicLead.business_uid == business_uid)
            .order_by(ClinicLead.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_followups_due(
        db: Session,
        business_uid: str,
    ) -> list[ClinicLead]:
        now = datetime.now(timezone.utc)

        return (
            db.query(ClinicLead)
            .filter(
                ClinicLead.business_uid == business_uid,
                ClinicLead.status.in_(ClinicService.ACTIVE_STATUSES),
                ClinicLead.next_followup.is_not(None),
                ClinicLead.next_followup <= now,
            )
            .order_by(ClinicLead.next_followup.asc())
            .all()
        )

    @staticmethod
    def mark_contacted(
        db: Session,
        business_uid: str,
        lead_id: int,
    ) -> ClinicLead | None:
        lead = (
            db.query(ClinicLead)
            .filter(ClinicLead.id == lead_id, ClinicLead.business_uid == business_uid)
            .first()
        )

        if lead is None:
            return None

        lead.status = "Contacted"
        lead.next_followup = datetime.now(timezone.utc) + timedelta(days=2)

        db.commit()
        db.refresh(lead)

        return lead

    @staticmethod
    def mark_appointment_booked(
        db: Session,
        business_uid: str,
        lead_id: int,
    ) -> ClinicLead | None:
        lead = (
            db.query(ClinicLead)
            .filter(ClinicLead.id == lead_id, ClinicLead.business_uid == business_uid)
            .first()
        )

        if lead is None:
            return None

        lead.status = "Appointment Booked"
        lead.next_followup = None

        db.commit()
        db.refresh(lead)

        return lead