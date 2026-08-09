from __future__ import annotations

import json
from typing import Any

from app.ai.customer_success_schema import (
    CustomerSuccessReport,
)
from app.workforce.runtime.base import BaseExecutive


class CustomerSuccessExecutive(BaseExecutive):
    """
    AI-powered Customer Success Executive.

    Responsible for customer retention, engagement,
    reactivation, satisfaction and lifecycle planning.
    """

    name = "Customer Success"

    response_model = CustomerSuccessReport

    @property
    def system_instruction(self) -> str:
        return (
            "You are Nestora's senior Customer Success "
            "Executive. Your responsibility is to improve "
            "customer retention, satisfaction, engagement, "
            "reactivation and lifetime value. Create "
            "practical customer-success plans that can be "
            "executed by a real business."
        )

    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:

        return f"""
You are the Customer Success Executive for Nestora.

TASK

{title}

DESCRIPTION

{description or "No description supplied."}

MISSION DATA

{json.dumps(input_data, indent=2, ensure_ascii=False)}

Create a professional Customer Success execution report.

Your report must include:

1. Executive summary

2. Retention strategy
   - Objective
   - Target customers
   - Engagement plan
   - Retention actions
   - Follow-up plan

3. Recommended actions
   Each action should contain:
   - Title
   - Description
   - Priority
   - Expected impact

4. Customer messages
   Provide practical customer communication examples
   where appropriate.

5. KPIs
   Define measurable customer-success KPIs and targets.

6. Risks
   Identify important retention, satisfaction,
   operational or customer-experience risks.

Focus on practical execution rather than generic advice.

Use the business and mission context supplied above.

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
                "Prepared a fallback customer-success "
                "and retention plan."
            ),
            "retention_strategy": {
                "objective": title,
                "target_customers": (
                    "Existing and inactive customers"
                ),
                "engagement_plan": [
                    "Segment existing customers",
                    "Identify inactive customers",
                    "Create personalized follow-up",
                ],
                "retention_actions": [
                    "Contact high-value customers",
                    "Launch customer reactivation outreach",
                    "Collect customer feedback",
                ],
                "follow_up_plan": [
                    "Follow up after initial contact",
                    "Track customer responses",
                    "Escalate high-value opportunities",
                ],
            },
            "recommended_actions": [
                {
                    "title": "Segment customers",
                    "description": (
                        "Group customers by activity, "
                        "value and engagement."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "Improved targeting and retention."
                    ),
                },
                {
                    "title": "Launch reactivation campaign",
                    "description": (
                        "Contact inactive customers with "
                        "relevant personalized outreach."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "Recover inactive customers."
                    ),
                },
            ],
            "customer_messages": [
                (
                    "We would love to welcome you back. "
                    "Contact us today and our team will "
                    "help you with your next appointment."
                )
            ],
            "kpis": [
                {
                    "name": "Customer retention rate",
                    "target": "Increase",
                    "measurement": (
                        "Percentage of customers retained"
                    ),
                },
                {
                    "name": "Reactivation rate",
                    "target": "Increase",
                    "measurement": (
                        "Inactive customers successfully "
                        "reactivated"
                    ),
                },
            ],
            "risks": [
                "Low customer response rate",
                "Poor follow-up consistency",
            ],
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }