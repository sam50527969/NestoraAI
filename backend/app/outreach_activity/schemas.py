from datetime import datetime

from pydantic import BaseModel


class OutreachActivityResponse(BaseModel):
    activity_uid: str
    approval_uid: str
    lead_id: int | None = None
    lead_name: str
    status: str
    prepared_by: str | None = None
    phone: str | None = None
    website: str | None = None
    email_subject: str | None = None
    email_body: str | None = None
    whatsapp_message: str | None = None
    cold_call_script: str | None = None
    proposal_summary: str | None = None
    created_at: datetime
    updated_at: datetime
    sent_at: datetime | None = None