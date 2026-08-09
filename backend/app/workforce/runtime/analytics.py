from __future__ import annotations

import json
from typing import Any

from app.ai.analytics_schema import AnalyticsReport
from app.workforce.runtime.base import BaseExecutive


class AnalyticsExecutive(BaseExecutive):
    """
    AI-powered Analytics Executive.

    Responsible for measurement strategy, KPIs,
    dashboards, performance analysis and optimization.
    """

    name = "Analytics"

    response_model = AnalyticsReport

    @property
    def system_instruction(self) -> str:
        return (
            "You are Nestora's senior Analytics Executive. "
            "Define measurable KPIs, reporting systems, dashboard metrics, "
            "performance insights, optimization actions and decision-ready "
            "business reporting."
        )

    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:

        return f"""
You are the Analytics Executive for Nestora.

TASK

{title}

DESCRIPTION

{description or "No description supplied."}

MISSION DATA

{json.dumps(input_data, indent=2, ensure_ascii=False)}

Create a professional Analytics execution report.

Your report must include:

1. Executive summary

2. Measurement strategy

3. KPIs
   For each KPI include:
   - Name
   - Target
   - Measurement method
   - Reporting frequency

4. Dashboard metrics
   List the most important metrics that should appear
   on the mission or business dashboard.

5. Insights
   Each insight should contain:
   - Title
   - Description
   - Priority
   - Recommended action

6. Optimization actions
   Provide practical actions based on performance data.

7. Reporting cadence
   Define daily, weekly, monthly or campaign-level reporting
   where appropriate.

8. Risks
   Identify data-quality, attribution, tracking,
   interpretation or reporting risks.

Use previous executive outputs from executive_context when relevant.

Focus on practical measurement and decision support.

Return only the structured professional business report.
"""

    def fallback_output(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
        error_message: str,
    ) -> dict[str, Any]:

        return {
            "executive": self.name,
            "task_title": title,
            "status": "completed",
            "executive_summary": (
                "Prepared a fallback analytics and performance "
                "measurement plan."
            ),
            "measurement_strategy": (
                "Track the full funnel from enquiry through conversion, "
                "revenue and repeat business."
            ),
            "kpis": [
                {
                    "name": "Qualified leads",
                    "target": "Increase",
                    "measurement": "Count qualified enquiries",
                    "frequency": "Weekly",
                },
                {
                    "name": "Lead-to-customer conversion rate",
                    "target": "Increase",
                    "measurement": (
                        "Customers divided by qualified leads"
                    ),
                    "frequency": "Weekly",
                },
                {
                    "name": "Customer acquisition cost",
                    "target": "Reduce",
                    "measurement": (
                        "Acquisition spend divided by new customers"
                    ),
                    "frequency": "Monthly",
                },
                {
                    "name": "Return on investment",
                    "target": "Increase",
                    "measurement": (
                        "Net return divided by campaign investment"
                    ),
                    "frequency": "Monthly",
                },
            ],
            "dashboard_metrics": [
                "Leads",
                "Qualified leads",
                "Bookings",
                "Conversion rate",
                "Revenue",
                "Acquisition cost",
                "ROI",
            ],
            "insights": [
                {
                    "title": "Monitor conversion leakage",
                    "description": (
                        "Identify the stage where the largest number "
                        "of qualified prospects are lost."
                    ),
                    "priority": "high",
                    "recommended_action": (
                        "Review the weakest conversion stage each week."
                    ),
                }
            ],
            "optimization_actions": [
                "Compare channel performance",
                "Review lead response time",
                "Track campaign-to-booking conversion",
                "Reallocate budget toward stronger channels",
            ],
            "reporting_cadence": [
                "Daily lead monitoring",
                "Weekly conversion review",
                "Monthly ROI review",
            ],
            "risks": [
                "Incomplete tracking",
                "Inconsistent data entry",
                "Incorrect attribution",
            ],
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }