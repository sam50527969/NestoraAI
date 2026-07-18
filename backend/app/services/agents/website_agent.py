from typing import Any, Dict, List, Optional

from app.services.agents.agent_base import BaseAgent
from app.services.mission_filters import has_real_value
from app.services.website_analyzer import analyze_website


class WebsiteAgent(BaseAgent):
    """
    AI agent responsible for website availability checks and analysis.

    Individual website failures are recorded without failing the whole mission.
    """

    AGENT_NAME = "Website Agent"
    TASK_NAME = "website_analysis"

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

        self.available_count = 0
        self.analyzed_count = 0
        self.failed_count = 0
        self.skipped = False
        self.started = False

    async def prepare(
        self,
        leads: List[Dict[str, Any]],
    ) -> int:
        """
        Count usable websites and prepare the persistent task.
        """
        self.available_count = sum(
            1
            for lead in leads
            if has_real_value(lead.get("website"))
        )

        if not self.request.analyze_websites:
            self.skipped = True

            self.task_complete(
                output={
                    "skipped": True,
                    "reason": "Website analysis was disabled",
                    "websites_analyzed": 0,
                    "websites_available": self.available_count,
                    "failed_count": 0,
                }
            )

            self.update_status(
                status="completed",
                progress=100,
                current_task="Website analysis disabled",
            )

            self.log("Website analysis was disabled for this mission.")

            return self.available_count

        if self.available_count == 0:
            self.skipped = True

            self.task_complete(
                output={
                    "skipped": True,
                    "reason": "No websites were available",
                    "websites_analyzed": 0,
                    "websites_available": 0,
                    "failed_count": 0,
                }
            )

            self.update_status(
                status="completed",
                progress=100,
                current_task="No websites to analyze",
            )

            self.log("No usable websites were available for analysis.")

            return 0

        self.task_start()
        self.task_progress(0)
        self.started = True

        self.update_status(
            status="running",
            progress=0,
            current_task="Preparing website analysis",
        )

        self.update_mission(
            current_step="Website Agent is preparing website analysis",
        )

        self.log(
            f"Preparing to analyze {self.available_count} websites."
        )

        return self.available_count

    async def run(
        self,
        lead: Dict[str, Any],
    ) -> Optional[Any]:
        """
        Analyze one lead website.

        Returns the analyzer result, or None when the website is unavailable,
        disabled, or fails analysis.
        """
        if self.skipped or not self.request.analyze_websites:
            return None

        website = lead.get("website")

        if not has_real_value(website):
            return None

        business_name = str(
            lead.get("businessName") or "Unnamed Business"
        ).strip()

        processed_count = (
            self.analyzed_count
            + self.failed_count
            + 1
        )

        progress = (
            int(processed_count / self.available_count * 100)
            if self.available_count > 0
            else 100
        )

        self.task_progress(progress)

        self.update_status(
            status="running",
            progress=progress,
            current_task=f"Analyzing website for {business_name}",
        )

        self.update_mission(
            current_step=(
                f"Website Agent is analyzing {business_name}"
            ),
        )

        try:
            result = analyze_website(website)

            self.analyzed_count += 1

            self.log(
                f"Analyzed website for {business_name}."
            )

            return result

        except Exception as error:
            self.failed_count += 1

            self.log(
                f"Website analysis failed for "
                f"{business_name}: {error}"
            )

            print(
                f"Website analysis failed for "
                f"{business_name}: {error}"
            )

            return None

    async def complete(self) -> None:
        """
        Complete the website-analysis task.
        """
        if self.skipped:
            return

        if not self.started:
            return

        self.task_complete(
            output={
                "websites_analyzed": self.analyzed_count,
                "websites_available": self.available_count,
                "failed_count": self.failed_count,
            }
        )

        self.update_status(
            status="completed",
            progress=100,
            current_task=(
                f"Analyzed {self.analyzed_count} websites"
            ),
        )

        self.log(
            f"Website analysis completed: "
            f"{self.analyzed_count} successful, "
            f"{self.failed_count} failed."
        )

    async def rollback(self) -> None:
        """
        Mark website analysis as failed.

        Completed website checks are preserved because they do not modify
        mission-critical CRM records.
        """
        if self.skipped:
            return

        self.update_status(
            status="failed",
            current_task="Website analysis failed",
        )

        self.log(
            f"Website analysis stopped after "
            f"{self.analyzed_count} successful checks and "
            f"{self.failed_count} failures."
        )