from __future__ import annotations

import json
from typing import Any

from app.ai.sales_schema import SalesReport
from app.workforce.runtime.base import BaseExecutive


class SalesExecutive(BaseExecutive):
    """
    AI-powered Sales Executive.

    Responsible for lead conversion, qualification,
    outreach, objection handling and revenue execution.
    """

    name = "Sales"

    response_model = SalesReport

    @property
    def system_instruction(self) -> str:
        return (
            "You are Nestora's senior Sales Executive. "
            "Create practical sales strategies, lead qualification systems, "
            "outreach scripts, objection-handling frameworks, conversion "
            "processes, KPIs and implementation actions."
        )

    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:

        return f"""
You are the Sales Executive for Nestora.

TASK

{title}

DESCRIPTION

{description or "No description supplied."}

MISSION DATA

{json.dumps(input_data, indent=2, ensure_ascii=False)}

Create a professional Sales execution report.

Your report must include:

1. Executive summary

2. Sales strategy

3. Target customer profile

4. Sales process
   For each stage include:
   - Stage
   - Objective
   - Actions

5. Objection handling
   Provide practical responses to likely objections.

6. Outreach script
   Provide usable sales conversation or outreach lines.

7. Recommended actions
   Each action should contain:
   - Title
   - Description
   - Priority
   - Expected impact

8. KPIs
   Define measurable sales KPIs and targets.

9. Risks
   Identify conversion, process, staffing, timing or revenue risks.

Focus on practical execution rather than generic advice.

Use previous executive outputs from executive_context when relevant.

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
                "Prepared a fallback sales conversion plan."
            ),
            "sales_strategy": (
                "Prioritize high-intent leads, respond quickly, "
                "qualify consistently and use structured follow-up."
            ),
            "target_customer_profile": (
                "Prospects with a clear need, purchase intent "
                "and ability to act."
            ),
            "sales_process": [
                {
                    "stage": "Qualification",
                    "objective": "Identify high-value prospects",
                    "actions": [
                        "Confirm customer need",
                        "Confirm urgency",
                        "Confirm decision-maker",
                    ],
                },
                {
                    "stage": "Conversion",
                    "objective": "Move qualified prospects to action",
                    "actions": [
                        "Present relevant offer",
                        "Handle objections",
                        "Ask for the booking or next step",
                    ],
                },
                {
                    "stage": "Follow-up",
                    "objective": "Recover undecided prospects",
                    "actions": [
                        "Schedule follow-up",
                        "Record objections",
                        "Re-engage with relevant value",
                    ],
                },
            ],
            "objection_handling": [
                "Price: explain value and expected outcome.",
                "Need time: agree on a specific follow-up time.",
                "Comparing options: reinforce the strongest differentiators.",
            ],
            "outreach_script": [
                "Hello, I am following up regarding your enquiry.",
                "May I ask what you are mainly looking for?",
                "Based on that, I can recommend the most suitable next step.",
                "Would you like me to help you arrange the booking now?",
            ],
            "recommended_actions": [
                {
                    "title": "Implement lead qualification",
                    "description": (
                        "Use a consistent qualification checklist "
                        "for all incoming enquiries."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "Improved conversion focus and sales efficiency."
                    ),
                },
                {
                    "title": "Introduce structured follow-up",
                    "description": (
                        "Assign next actions and follow-up dates "
                        "to every qualified lead."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "Reduced lead leakage and higher conversion."
                    ),
                },
            ],
            "kpis": [
                {
                    "name": "Lead-to-booking conversion rate",
                    "target": "Increase",
                    "measurement": (
                        "Bookings divided by qualified leads"
                    ),
                },
                {
                    "name": "Lead response time",
                    "target": "Reduce",
                    "measurement": (
                        "Average time from enquiry to first response"
                    ),
                },
            ],
            "risks": [
                "Slow lead response",
                "Inconsistent follow-up",
                "Weak objection handling",
            ],
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }