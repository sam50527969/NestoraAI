from typing import Any, Dict, Optional

from app.schemas.outreach import OutreachLead, OutreachRequest
from app.services.agents.agent_base import BaseAgent
from app.services.outreach_service import generate_outreach


class OutreachAgent(BaseAgent):
    """
    AI agent responsible for generating outreach messages for analyzed leads.
    """

    AGENT_NAME = "Outreach Agent"
    TASK_NAME = "generate_outreach"

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

        self.generated_count = 0
        self.skipped = False
        self.started = False

    async def prepare(self) -> bool:
        """
        Prepare outreach generation.

        Returns True when outreach generation is enabled.
        """
        if not self.request.generate_outreach:
            self.skipped = True

            self.task_complete(
                output={
                    "skipped": True,
                    "reason": "Outreach generation was disabled",
                    "outreach_generated": 0,
                }
            )

            self.update_status(
                status="completed",
                progress=100,
                current_task="Outreach generation disabled",
            )

            self.log("Outreach generation was disabled for this mission.")

            return False

        self.task_start()
        self.task_progress(0)
        self.started = True

        self.update_status(
            status="waiting",
            progress=0,
            current_task="Waiting for lead analysis",
        )

        self.log("Outreach Agent is ready and waiting for analyzed leads.")

        return True

    async def run(
        self,
        lead: Dict[str, Any],
        analysis: Dict[str, Any],
        index: int,
        total: int,
    ) -> Optional[Any]:
        """
        Generate outreach for one analyzed lead.
        """
        if self.skipped or not self.request.generate_outreach:
            return None

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
            current_task=f"Generating outreach for {business_name}",
        )

        mission_progress = (
            65 + int(index / total * 30)
            if total > 0
            else 95
        )

        self.update_mission(
            progress=mission_progress,
            current_step=(
                f"Outreach Agent is preparing "
                f"a message for {business_name}"
            ),
        )

        outreach_request = OutreachRequest(
            lead=OutreachLead(
                name=business_name,
                category=lead.get("category"),
                phone=lead.get("phone"),
                website=lead.get("website"),
                priority=lead.get("priority") or "Medium",
                notes=analysis.get("recommendation"),
            ),
        )

        result = generate_outreach(outreach_request)

        self.generated_count += 1

        self.update_mission(
            outreach_generated=self.generated_count,
        )

        self.log(
            f"Generated outreach for {business_name}."
        )

        return result

    async def complete(self) -> None:
        """
        Complete outreach generation and persist the final count.
        """
        if self.skipped or not self.started:
            return

        self.task_complete(
            output={
                "outreach_generated": self.generated_count,
            }
        )

        self.update_status(
            status="completed",
            progress=100,
            current_task=(
                f"Generated {self.generated_count} outreach messages"
            ),
        )

        self.log(
            f"Outreach generation completed with "
            f"{self.generated_count} messages."
        )

    async def rollback(self) -> None:
        """
        Mark outreach generation as failed.

        Already generated messages are preserved.
        """
        if self.skipped:
            return

        self.update_status(
            status="failed",
            current_task="Outreach generation failed",
        )

        self.log(
            f"Outreach generation failed after "
            f"{self.generated_count} completed messages."
        )