from sqlalchemy.orm import Session

from app.schemas.crm import LeadCreate
from app.schemas.outreach import OutreachLead, OutreachRequest
from app.services.business_search import search_businesses
from app.services.crm_service import create_lead, update_ai_analysis
from app.services.mission_activity import log_mission_activity
from app.services.mission_filters import filter_leads, has_real_value
from app.services.mission_state import (
    MISSIONS,
    update_agent,
    update_mission,
)
from app.services.mission_task_runtime import (
    complete_mission_task,
    start_mission_task,
    update_mission_task_progress,
)
from app.services.opportunity_engine import analyze_opportunity
from app.services.outreach_service import generate_outreach
from app.services.sales_ai import analyze_lead
from app.services.website_analyzer import analyze_website


class MissionExecutor:
    """
    Executes an already-planned Nestora mission.

    Mission creation, planning, database-session handling, and top-level
    failure handling remain outside this class.
    """

    def __init__(
        self,
        db: Session,
        mission_id: str,
        request,
        business_uid: str,
        business_context=None,
    ):
        self.db = db
        self.mission_id = mission_id
        self.request = request
        self.business_uid = business_uid
        self.business_context = business_context
        self.currency = (
            business_context.currency
            if business_context is not None
            else None
        )
        self.active_task_type = None

        self.raw_result_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.saved_count = 0
        self.analyzed_count = 0
        self.websites_analyzed = 0
        self.websites_to_analyze = 0
        self.outreach_count = 0

    def log(
        self,
        agent_name: str,
        message: str,
    ) -> None:
        mission = MISSIONS.get(self.mission_id)

        if mission is None:
            return

        log_mission_activity(
            mission,
            agent_name,
            message,
        )

    def complete_empty_mission(
        self,
        current_step: str,
    ) -> None:
        complete_mission_task(
            self.db,
            self.mission_id,
            "save_leads",
            output_data={
                "saved_count": 0,
                "reason": "No businesses matched the filters",
            },
        )

        complete_mission_task(
            self.db,
            self.mission_id,
            "lead_analysis",
            output_data={
                "analyzed_count": 0,
                "reason": "No leads were available",
            },
        )

        complete_mission_task(
            self.db,
            self.mission_id,
            "website_analysis",
            output_data={
                "websites_analyzed": 0,
                "skipped": True,
                "reason": "No websites were available",
            },
        )

        complete_mission_task(
            self.db,
            self.mission_id,
            "generate_outreach",
            output_data={
                "outreach_generated": 0,
                "skipped": True,
                "reason": "No leads were available",
            },
        )

        complete_mission_task(
            self.db,
            self.mission_id,
            "proposal_generation",
            output_data={
                "skipped": True,
                "reason": "Proposal generation is not enabled yet",
            },
        )

        update_agent(
            self.mission_id,
            "CRM Agent",
            status="completed",
            progress=100,
            current_task="No businesses matched the filters",
        )

        update_agent(
            self.mission_id,
            "Sales Agent",
            status="completed",
            progress=100,
            current_task="No leads to analyze",
        )

        update_agent(
            self.mission_id,
            "Website Agent",
            status="completed",
            progress=100,
            current_task="No websites to analyze",
        )

        update_agent(
            self.mission_id,
            "Outreach Agent",
            status="completed",
            progress=100,
            current_task="No outreach required",
        )

        update_agent(
            self.mission_id,
            "Proposal Agent",
            status="completed",
            progress=100,
            current_task="Proposal generation skipped",
        )

        self.log(
            "CEO Agent",
            current_step,
        )

        update_mission(
            self.mission_id,
            status="completed",
            progress=100,
            current_step=current_step,
            searched=0,
            analyzed=0,
            outreach_generated=0,
            raw_results=self.raw_result_count,
            rejected=self.rejected_count,
        )

    async def execute_research(self):
        self.active_task_type = "business_search"

        start_mission_task(
            self.db,
            self.mission_id,
            self.active_task_type,
        )

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.active_task_type,
            10,
        )

        update_agent(
            self.mission_id,
            "Research Agent",
            status="running",
            progress=10,
            current_task=(
                f"Searching for {self.request.business_type} "
                f"businesses in {self.request.location}"
            ),
        )

        update_mission(
            self.mission_id,
            progress=8,
            current_step="Research Agent is searching businesses",
        )

        self.log(
            "Research Agent",
            (
                f"Searching for {self.request.business_type} "
                f"businesses in {self.request.location}."
            ),
        )

        search_results = await search_businesses(
            business_type=self.request.business_type,
            location=self.request.location,
            limit=self.request.quantity,
        )

        self.raw_result_count = len(search_results)

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.active_task_type,
            80,
        )

        update_agent(
            self.mission_id,
            "Research Agent",
            status="running",
            progress=80,
            current_task=(
                f"Filtering {self.raw_result_count} search results"
            ),
        )

        leads = filter_leads(
            search_results,
            minimum_quality=self.request.minimum_quality,
            priority_filter=self.request.priority_filter,
        )

        self.accepted_count = len(leads)
        self.rejected_count = (
            self.raw_result_count - self.accepted_count
        )

        complete_mission_task(
            self.db,
            self.mission_id,
            self.active_task_type,
            output_data={
                "raw_result_count": self.raw_result_count,
                "accepted_count": self.accepted_count,
                "rejected_count": self.rejected_count,
                "business_type": self.request.business_type,
                "location": self.request.location,
            },
        )

        self.active_task_type = None

        update_agent(
            self.mission_id,
            "Research Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Accepted {self.accepted_count} businesses "
                f"and rejected {self.rejected_count}"
            ),
        )

        self.log(
            "Research Agent",
            (
                f"Accepted {self.accepted_count} qualified "
                f"businesses and rejected "
                f"{self.rejected_count}."
            ),
        )

        update_mission(
            self.mission_id,
            progress=25,
            current_step=(
                f"Research completed with "
                f"{self.accepted_count} accepted businesses"
            ),
            searched=self.accepted_count,
        )

        return leads

    def prepare_tasks(
        self,
        leads,
    ) -> None:
        self.websites_to_analyze = sum(
            1
            for lead in leads
            if has_real_value(lead.get("website"))
        )

        start_mission_task(
            self.db,
            self.mission_id,
            "save_leads",
        )

        start_mission_task(
            self.db,
            self.mission_id,
            "lead_analysis",
        )

        update_agent(
            self.mission_id,
            "CRM Agent",
            status="running",
            progress=0,
            current_task="Preparing CRM records",
        )

        update_agent(
            self.mission_id,
            "Sales Agent",
            status="running",
            progress=0,
            current_task="Preparing lead analysis",
        )

        if self.request.analyze_websites:
            start_mission_task(
                self.db,
                self.mission_id,
                "website_analysis",
            )

            update_agent(
                self.mission_id,
                "Website Agent",
                status="running",
                progress=0,
                current_task="Preparing website analysis",
            )
        else:
            complete_mission_task(
                self.db,
                self.mission_id,
                "website_analysis",
                output_data={
                    "skipped": True,
                    "reason": "Website analysis was disabled",
                    "websites_analyzed": 0,
                },
            )

            update_agent(
                self.mission_id,
                "Website Agent",
                status="completed",
                progress=100,
                current_task="Website analysis disabled",
            )

        if self.request.generate_outreach:
            update_agent(
                self.mission_id,
                "Outreach Agent",
                status="waiting",
                progress=0,
                current_task="Waiting for lead analysis",
            )
        else:
            complete_mission_task(
                self.db,
                self.mission_id,
                "generate_outreach",
                output_data={
                    "skipped": True,
                    "reason": "Outreach generation was disabled",
                    "outreach_generated": 0,
                },
            )

            update_agent(
                self.mission_id,
                "Outreach Agent",
                status="completed",
                progress=100,
                current_task="Outreach generation disabled",
            )

    def save_lead(
        self,
        lead,
        business_name: str,
        item_progress: int,
    ):
        self.active_task_type = "save_leads"

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.active_task_type,
            item_progress,
        )

        update_mission(
            self.mission_id,
            current_step=(
                f"CRM Agent is saving {business_name}"
            ),
            progress=25 + int(
                (self.saved_count + 1)
                / self.accepted_count
                * 20
            ),
        )

        update_agent(
            self.mission_id,
            "CRM Agent",
            status="running",
            progress=item_progress,
            current_task=f"Saving {business_name}",
        )

        phone = lead.get("phone")
        website = lead.get("website")

        crm_lead = LeadCreate(
            business_uid=self.business_uid,
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

        self.log(
            "CRM Agent",
            f"Saved {business_name}.",
        )

        return saved_lead

    def analyze_saved_lead(
        self,
        lead,
        saved_lead,
        business_name: str,
        item_progress: int,
    ):
        self.active_task_type = "lead_analysis"

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.active_task_type,
            item_progress,
        )

        update_mission(
            self.mission_id,
            current_step=(
                f"Sales Agent is analyzing {business_name}"
            ),
            progress=45 + int(
                (self.analyzed_count + 1)
                / self.accepted_count
                * 20
            ),
        )

        update_agent(
            self.mission_id,
            "Sales Agent",
            status="running",
            progress=item_progress,
            current_task=f"Scoring {business_name}",
        )

        category = lead.get("category")
        phone = lead.get("phone")
        website = lead.get("website")
        priority = lead.get("priority") or "Medium"

        lead_analysis_input = {
            "name": business_name,
            "category": category,
            "phone": phone,
            "website": website,
            "priority": priority,
            "notes": lead.get("aiRecommendation"),
        }

        analysis = analyze_lead(
            lead_analysis_input
        )

        saved_lead.priority = priority

        update_ai_analysis(
            db=self.db,
            lead=saved_lead,
            analysis=analysis,
        )

        opportunity = analyze_opportunity(
            {
                "website": website,
                "phone": phone,
                "email": lead.get("email"),
                "priority": priority,
                "category": category,
                "ai_score": analysis.get("score", 0),
            }
        )

        saved_lead.opportunity_score = (
            opportunity["opportunity_score"]
        )

        saved_lead.estimated_value = (
            opportunity["estimated_value"]
        )

        saved_lead.closing_probability = (
            opportunity["closing_probability"]
        )

        saved_lead.business_potential = (
            opportunity["business_potential"]
        )

        saved_lead.opportunity_recommendation = (
            opportunity["recommended_service"]
        )

        self.db.commit()
        self.db.refresh(saved_lead)

        self.log(
            "Opportunity Agent",
            (
                f"{business_name} → "
                f"{opportunity['business_potential']} "
                f"Opportunity "
                f"({self.currency} {opportunity['estimated_value']})"
            ),
        )

        self.log(
            "Sales Agent",
            (
                f"Scored {business_name} "
                f"({analysis.get('score', 0)})."
            ),
        )

        return analysis

    def analyze_lead_website(
        self,
        lead,
        business_name: str,
    ) -> None:
        website = lead.get("website")

        if not self.request.analyze_websites:
            return

        if not has_real_value(website):
            return

        self.active_task_type = "website_analysis"

        website_progress = (
            int(
                (
                    self.websites_analyzed + 1
                )
                / self.websites_to_analyze
                * 100
            )
            if self.websites_to_analyze
            else 100
        )

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.active_task_type,
            website_progress,
        )

        update_agent(
            self.mission_id,
            "Website Agent",
            status="running",
            progress=website_progress,
            current_task=(
                f"Analyzing {business_name} website"
            ),
        )

        try:
            analyze_website(website)

            self.log(
                "Website Agent",
                (
                    f"Analyzed website for "
                    f"{business_name}."
                ),
            )

        except Exception as website_error:
            print(
                "Website analysis failed for "
                f"{business_name}: {website_error}"
            )

            self.log(
                "Website Agent",
                (
                    f"Website analysis failed for "
                    f"{business_name}."
                ),
            )

        self.websites_analyzed += 1

    def generate_lead_outreach(
        self,
        lead,
        business_name: str,
        analysis,
        item_progress: int,
    ) -> None:
        if not self.request.generate_outreach:
            return

        self.active_task_type = "generate_outreach"

        if self.outreach_count == 0:
            start_mission_task(
                self.db,
                self.mission_id,
                self.active_task_type,
            )

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.active_task_type,
            item_progress,
        )

        update_mission(
            self.mission_id,
            current_step=(
                "Outreach Agent is preparing "
                f"a message for {business_name}"
            ),
            progress=65 + int(
                (
                    self.outreach_count + 1
                )
                / self.accepted_count
                * 30
            ),
        )

        update_agent(
            self.mission_id,
            "Outreach Agent",
            status="running",
            progress=item_progress,
            current_task=(
                f"Writing outreach for "
                f"{business_name}"
            ),
        )

        outreach_request = OutreachRequest(
            lead=OutreachLead(
                name=business_name,
                category=lead.get("category"),
                phone=lead.get("phone"),
                website=lead.get("website"),
                priority=(
                    lead.get("priority")
                    or "Medium"
                ),
                notes=analysis.get(
                    "recommendation"
                ),
            ),
            offer=f"99 {self.currency} starter business package",
        )

        generate_outreach(
            outreach_request
        )

        self.outreach_count += 1

        update_mission(
            self.mission_id,
            outreach_generated=self.outreach_count,
        )

        self.log(
            "Outreach Agent",
            (
                f"Generated outreach for "
                f"{business_name}."
            ),
        )

    def complete_tasks(self) -> None:
        complete_mission_task(
            self.db,
            self.mission_id,
            "save_leads",
            output_data={
                "saved_count": self.saved_count,
            },
        )

        complete_mission_task(
            self.db,
            self.mission_id,
            "lead_analysis",
            output_data={
                "analyzed_count": self.analyzed_count,
            },
        )

        if self.request.analyze_websites:
            complete_mission_task(
                self.db,
                self.mission_id,
                "website_analysis",
                output_data={
                    "websites_analyzed": (
                        self.websites_analyzed
                    ),
                    "websites_available": (
                        self.websites_to_analyze
                    ),
                },
            )

        if self.request.generate_outreach:
            complete_mission_task(
                self.db,
                self.mission_id,
                "generate_outreach",
                output_data={
                    "outreach_generated": (
                        self.outreach_count
                    ),
                },
            )

        complete_mission_task(
            self.db,
            self.mission_id,
            "proposal_generation",
            output_data={
                "skipped": True,
                "reason": (
                    "Proposal generation is planned "
                    "for a future sprint"
                ),
            },
        )

        self.active_task_type = None

    def complete_agents(self) -> None:
        update_agent(
            self.mission_id,
            "CRM Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Saved {self.saved_count} leads"
            ),
        )

        update_agent(
            self.mission_id,
            "Sales Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Analyzed {self.analyzed_count} leads"
            ),
        )

        update_agent(
            self.mission_id,
            "Website Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Analyzed {self.websites_analyzed} websites"
                if self.request.analyze_websites
                else "Website analysis disabled"
            ),
        )

        update_agent(
            self.mission_id,
            "Outreach Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Generated {self.outreach_count} "
                "outreach messages"
                if self.request.generate_outreach
                else "Outreach generation disabled"
            ),
        )

        update_agent(
            self.mission_id,
            "Proposal Agent",
            status="completed",
            progress=100,
            current_task=(
                "Proposal generation skipped "
                "until the feature is implemented"
            ),
        )

    async def execute(self) -> dict:
        leads = await self.execute_research()

        if self.accepted_count == 0:
            self.complete_empty_mission(
                (
                    "Mission completed with no businesses "
                    "matching the selected filters"
                )
            )

            return {
                "searched": 0,
                "analyzed": 0,
                "outreach_generated": 0,
            }

        self.prepare_tasks(leads)

        for index, lead in enumerate(
            leads,
            start=1,
        ):
            business_name = str(
                lead.get("businessName")
                or "Unnamed Business"
            ).strip()

            item_progress = int(
                (
                    index
                    / self.accepted_count
                )
                * 100
            )

            saved_lead = self.save_lead(
                lead,
                business_name,
                item_progress,
            )

            analysis = self.analyze_saved_lead(
                lead,
                saved_lead,
                business_name,
                item_progress,
            )

            self.analyze_lead_website(
                lead,
                business_name,
            )

            self.analyzed_count += 1

            update_mission(
                self.mission_id,
                analyzed=self.analyzed_count,
            )

            self.generate_lead_outreach(
                lead,
                business_name,
                analysis,
                item_progress,
            )

        self.complete_tasks()
        self.complete_agents()

        self.log(
            "CEO Agent",
            "Mission completed successfully.",
        )

        update_mission(
            self.mission_id,
            status="completed",
            progress=100,
            current_step="Mission completed",
            searched=self.accepted_count,
            analyzed=self.analyzed_count,
            outreach_generated=self.outreach_count,
        )

        return {
            "searched": self.accepted_count,
            "analyzed": self.analyzed_count,
            "outreach_generated": self.outreach_count,
        }
