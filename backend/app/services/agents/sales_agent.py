from typing import Any, Dict

from app.services.agents.agent_base import BaseAgent
from app.services.crm_service import update_ai_analysis
from app.services.opportunity_engine import analyze_opportunity
from app.services.sales_ai import analyze_lead


class SalesAgent(BaseAgent):
    """
    AI agent responsible for lead scoring and opportunity analysis.
    """

    AGENT_NAME = "Sales Agent"
    TASK_NAME = "lead_analysis"

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

        self.analyzed_count = 0

    async def prepare(self) -> None:
        """
        Prepare Sales AI processing.
        """
        self.task_start()
        self.task_progress(0)

        self.update_status(
            status="running",
            progress=0,
            current_task="Preparing lead analysis",
        )

        self.update_mission(
            progress=45,
            current_step="Sales Agent is preparing lead analysis",
        )

        self.log("Preparing AI lead analysis.")

    async def run(
        self,
        saved_lead,
        lead: Dict[str, Any],
        index: int,
        total: int,
    ):
        """
        Analyze a single CRM lead and enrich it with AI insights.
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
            current_task=f"Analyzing {business_name}",
        )

        mission_progress = 45 + int(
            index / total * 20
        ) if total > 0 else 65

        self.update_mission(
            progress=mission_progress,
            current_step=f"Sales Agent is analyzing {business_name}",
        )

        priority = lead.get("priority") or "Medium"

        analysis_input = {
            "name": business_name,
            "category": lead.get("category"),
            "phone": lead.get("phone"),
            "website": lead.get("website"),
            "priority": priority,
            "notes": lead.get("aiRecommendation"),
        }

        analysis = analyze_lead(analysis_input)

        update_ai_analysis(
            db=self.db,
            lead=saved_lead,
            analysis=analysis,
        )

        opportunity = analyze_opportunity(
            {
                "website": lead.get("website"),
                "phone": lead.get("phone"),
                "email": lead.get("email"),
                "priority": priority,
                "category": lead.get("category"),
                "ai_score": analysis.get("score", 0),
            }
        )

        saved_lead.priority = priority
        saved_lead.opportunity_score = opportunity["opportunity_score"]
        saved_lead.estimated_value = opportunity["estimated_value"]
        saved_lead.closing_probability = opportunity["closing_probability"]
        saved_lead.business_potential = opportunity["business_potential"]
        saved_lead.opportunity_recommendation = opportunity["recommended_service"]

        self.db.commit()
        self.db.refresh(saved_lead)

        self.analyzed_count += 1

        self.log(
            f"Scored {business_name} "
            f"({analysis.get('score', 0)})."
        )

        self.log(
            f"{business_name} → "
            f"{opportunity['business_potential']} Opportunity "
            f"(QAR {opportunity['estimated_value']})"
        )

        return analysis

    async def complete(self) -> None:
        """
        Complete Sales AI processing.
        """
        self.task_complete(
            output={
                "analyzed_count": self.analyzed_count,
            }
        )

        self.update_status(
            status="completed",
            progress=100,
            current_task=f"Analyzed {self.analyzed_count} leads",
        )

        self.log(
            f"Sales analysis completed for "
            f"{self.analyzed_count} leads."
        )

    async def rollback(self) -> None:
        """
        Mark Sales AI processing as failed.

        AI analysis already written to the CRM is intentionally preserved.
        """
        self.update_status(
            status="failed",
            current_task="Lead analysis failed",
        )

        self.log(
            f"Lead analysis failed after "
            f"{self.analyzed_count} processed leads."
        )