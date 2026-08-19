from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ClinicLeadCreate(
    BaseModel
):
    patient_name: str
    phone: str
    treatment: str
    source: str | None = (
        "WhatsApp"
    )
    notes: str | None = None


class ClinicLeadResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    patient_name: str
    phone: str
    treatment: str
    source: str
    status: str
    assigned_to: str
    next_followup: (
        datetime | None
    )
    notes: str | None