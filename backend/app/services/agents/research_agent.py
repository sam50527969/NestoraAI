from typing import Any, Dict, List

from app.services.agents.agent_base import BaseAgent
from app.services.business_search import search_businesses
from app.services.mission_filters import filter_leads


class ResearchAgent(BaseAgent):
    """
    AI agent responsible for discovering and qualifying businesses.
    """

    AGENT_NAME = "Research Agent"
    TASK_NAME = "business_search"

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

        self.raw_result_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.qualified_leads: List[Dict[str, Any]] = []

    async def prepare(self) -> None:
        """
        Prepare the Research Agent and start its persistent task.
        """
        self.task_start()

        self.task_progress(5)

        self.update_status(
            status="running",
            progress=5,
            current_task=(
                f"Preparing to search for "
                f"{self.request.business_type} businesses "
                f"in {self.request.location}"
            ),
        )

        self.update_mission(
            progress=5,
            current_step="Research Agent is preparing business search",
        )

        self.log(
            f"Preparing business search for "
            f"{self.request.business_type} businesses "
            f"in {self.request.location}."
        )

    async def run(self) -> List[Dict[str, Any]]:
        """
        Search for businesses, filter the results, and return qualified leads.
        """
        self.task_progress(10)

        self.update_status(
            status="running",
            progress=10,
            current_task=(
                f"Searching for {self.request.business_type} "
                f"businesses in {self.request.location}"
            ),
        )

        self.update_mission(
            progress=8,
            current_step="Research Agent is searching businesses",
        )

        self.log(
            f"Searching for {self.request.business_type} "
            f"businesses in {self.request.location}."
        )

        search_results = await search_businesses(
            business_type=self.request.business_type,
            location=self.request.location,
            limit=self.request.quantity,
        )

        self.raw_result_count = len(search_results)

        self.task_progress(80)

        self.update_status(
            status="running",
            progress=80,
            current_task=(
                f"Filtering {self.raw_result_count} search results"
            ),
        )

        self.qualified_leads = filter_leads(
            search_results,
            minimum_quality=self.request.minimum_quality,
            priority_filter=self.request.priority_filter,
        )

        self.accepted_count = len(self.qualified_leads)
        self.rejected_count = (
            self.raw_result_count - self.accepted_count
        )

        self.update_mission(
            searched=self.accepted_count,
            progress=25,
            current_step=(
                f"Research completed with "
                f"{self.accepted_count} accepted businesses"
            ),
            raw_results=self.raw_result_count,
            rejected=self.rejected_count,
        )

        return self.qualified_leads

    async def complete(self) -> None:
        """
        Complete the Research Agent and persist its final output.
        """
        self.task_complete(
            output={
                "raw_result_count": self.raw_result_count,
                "accepted_count": self.accepted_count,
                "rejected_count": self.rejected_count,
                "business_type": self.request.business_type,
                "location": self.request.location,
            }
        )

        self.update_status(
            status="completed",
            progress=100,
            current_task=(
                f"Accepted {self.accepted_count} businesses "
                f"and rejected {self.rejected_count}"
            ),
        )

        self.log(
            f"Accepted {self.accepted_count} qualified businesses "
            f"and rejected {self.rejected_count}."
        )

    async def rollback(self) -> None:
        """
        Mark the Research Agent as failed if execution cannot complete.

        No database records are created by this agent, so there is currently
        no additional data compensation required.
        """
        self.update_status(
            status="failed",
            current_task="Business research failed",
        )

        self.log("Business research failed and was rolled back.")