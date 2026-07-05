from sqlalchemy.orm import Session

from app.database.models import Lead
from app.schemas.crm import LeadCreate, LeadUpdate


VALID_STATUSES = {"New", "Contacted", "Qualified", "Won", "Lost"}
VALID_PRIORITIES = {"Low", "Medium", "High"}


def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_leads(db: Session) -> list[Lead]:
    return db.query(Lead).order_by(Lead.created_at.desc(), Lead.id.desc()).all()


def get_lead(db: Session, lead_id: int) -> Lead | None:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead(db: Session, lead_id: int, lead_data: LeadUpdate) -> Lead | None:
    lead = get_lead(db, lead_id)

    if not lead:
        return None

    update_values = lead_data.model_dump(exclude_unset=True)

    if "status" in update_values and update_values["status"] not in VALID_STATUSES:
        raise ValueError("Invalid lead status")

    if "priority" in update_values and update_values["priority"] not in VALID_PRIORITIES:
        raise ValueError("Invalid lead priority")

    for field, value in update_values.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead
