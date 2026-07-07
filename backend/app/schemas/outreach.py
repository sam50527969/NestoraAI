from pydantic import BaseModel


class OutreachLead(BaseModel):
    name: str
    category: str | None = None
    phone: str | None = None
    website: str | None = None
    priority: str | None = None
    notes: str | None = None


class OutreachRequest(BaseModel):
    lead: OutreachLead
    offer: str | None = "starter business package"


class OutreachResponse(BaseModel):
    email_subject: str
    email_body: str
    whatsapp_message: str
    cold_call_script: str
    proposal_summary: str