from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.tools import ToolBase
from app.database.models import Lead
from app.schemas.crm import LeadCreate, LeadUpdate
from app.services.crm_service import (
    create_lead,
    get_lead,
    get_leads,
    update_ai_analysis,
    update_lead,
)


class CRMTool(ToolBase):
    """
    Reusable CRM capability for Nestora executives and workers.

    This tool delegates all database operations to the existing
    CRM service layer so the API and AI workforce share the same
    business logic.
    """

    tool_id = "crm"
    name = "CRM Tool"
    description = "Create, retrieve, update, and analyze CRM leads."

    async def create_lead(
        self,
        *,
        db: Session,
        lead_data: LeadCreate,
    ) -> Lead:
        return create_lead(db, lead_data)

    async def list_leads(
        self,
        *,
        db: Session,
    ) -> list[Lead]:
        return get_leads(db)

    async def get_lead(
        self,
        *,
        db: Session,
        lead_id: int,
    ) -> Lead | None:
        return get_lead(db, lead_id)

    async def update_lead(
        self,
        *,
        db: Session,
        lead_id: int,
        lead_data: LeadUpdate,
    ) -> Lead | None:
        return update_lead(
            db,
            lead_id,
            lead_data,
        )

    async def update_ai_analysis(
        self,
        *,
        db: Session,
        lead: Lead,
        analysis: dict,
    ) -> Lead:
        return update_ai_analysis(
            db,
            lead,
            analysis,
        )