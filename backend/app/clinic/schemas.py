from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ClinicLeadCreate(BaseModel):
    patient_name: str
    phone: str
    treatment: str
    source: Optional[str] = "WhatsApp"
    notes: Optional[str] = None


class ClinicLeadResponse(BaseModel):
    id: int
    patient_name: str
    phone: str
    treatment: str
    source: str
    status: str
    assigned_to: str
    next_followup: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True