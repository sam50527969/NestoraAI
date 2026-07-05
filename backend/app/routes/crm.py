from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Lead

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.post("/leads")
def save_lead(lead: dict, db: Session = Depends(get_db)):
    db_lead = Lead(
        business_name=lead.get("businessName"),
        category=lead.get("category"),
        location=lead.get("location"),
        phone=lead.get("phone"),
        email=lead.get("email"),
        website=lead.get("website"),
        status=lead.get("status", "New"),
    )

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    return {
        "id": db_lead.id,
        "businessName": db_lead.business_name,
        "category": db_lead.category,
        "location": db_lead.location,
        "phone": db_lead.phone,
        "email": db_lead.email,
        "website": db_lead.website,
        "status": db_lead.status,
    }


@router.get("/leads")
def get_saved_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()

    return [
        {
            "id": lead.id,
            "businessName": lead.business_name,
            "category": lead.category,
            "location": lead.location,
            "phone": lead.phone,
            "email": lead.email,
            "website": lead.website,
            "status": lead.status,
        }
        for lead in leads
    ]