from typing import Any, Dict

from app.schemas.crm import LeadCreate
from app.services.agents.agent_base import BaseAgent
from app.services.crm_service import create_lead
from app.services.mission_filters import has_real_value


class CRMAgent(BaseAgent):
    """
    AI agent responsible for storing qualified businesses in the CRM.
    """

    AGENT_NAME = "CRM Agent"
    TASK_NAME = "save_leads"

    def __init__(
        self,
        db,
        mission_id: str,
        request,
    ) -> None:
        super().__init__(
            db=db,
            mission_id=mission_id,
            request=request,
        )

        self.saved_count = 0

    async def prepare(self) -> None:
        """
        Prepare CRM processing and start the persistent task.
        """
        self.task_start()
        self.task_progress(0)

        self.update_status(
            status="running",
            progress=0,
            current_task="Preparing CRM records",
        )

        self.update_mission(
            progress=25,
            current_step="CRM Agent is preparing lead records",
        )

        self.log("Preparing qualified businesses for CRM storage.")

    async def run(
        self,
        lead: Dict[str, Any],
        index: int,
        total: int,
    ):
        """
        Create one CRM lead and return the saved database record.
        """
        business_name = str(
            lead.get("businessName") or "Unnamed Business"
        ).strip()

        progress = (
            int(index / total * 100)
            if total > 0
            else 100
        )

        self.task_progress(progress)

        self.update_status(
            status="running",
            progress=progress,
            current_task=f"Saving {business_name}",
        )

        mission_progress = 25 + int(
            index / total * 20
        ) if total > 0 else 45

        self.update_mission(
            progress=mission_progress,
            current_step=f"CRM Agent is saving {business_name}",
        )

        phone = lead.get("phone")
        website = lead.get("website")

        crm_lead = LeadCreate(
            name=business_name,
            category=lead.get("category"),
            address=lead.get("location"),
            phone=(
                phone
                if has_real_value(phone)
                else None
            ),
            website=(
                website
                if has_real_value(website)
                else None
            ),
            source="Mission AI",
        )

        saved_lead = create_lead(
            db=self.db,
            lead_data=crm_lead,
        )

        self.saved_count += 1

        self.log(f"Saved {business_name} to the CRM.")

        return saved_lead

    async def complete(self) -> None:
        """
        Complete CRM processing and persist the final saved count.
        """
        self.task_complete(
            output={
                "saved_count": self.saved_count,
            }
        )

        self.update_status(
            status="completed",
            progress=100,
            current_task=f"Saved {self.saved_count} leads",
        )

        self.log(
            f"CRM processing completed with "
            f"{self.saved_count} saved leads."
        )

    async def rollback(self) -> None:
        """
        Mark CRM processing as failed.

        Saved CRM records are not automatically deleted because they may
        already be useful and could have been processed by another agent.
        """
        self.update_status(
            status="failed",
            current_task="CRM processing failed",
        )

        self.log(
            f"CRM processing failed after saving "
            f"{self.saved_count} leads."
        )