import json
from typing import Any

from app.ai.marketing_schema import MarketingReport
from app.workforce.runtime.base import BaseExecutive


class MarketingExecutive(BaseExecutive):
    """
    AI-powered Marketing Executive.
    """

    name = "Marketing"

    response_model = MarketingReport

    @property
    def system_instruction(self) -> str:
        return (
            "You are Nestora's senior Marketing Executive. "
            "Create professional marketing campaigns, customer messaging, "
            "budget recommendations, KPIs and implementation plans."
        )

    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:

        return f"""
You are the Marketing Executive for Nestora.

Task:

{title}

Description:

{description or "No description supplied."}

Mission Data:

{json.dumps(input_data, indent=2, ensure_ascii=False)}

Create:

• Executive summary

• Marketing campaign

• Customer messages

• Recommended actions

• Budget

• KPIs

• Risks

Return only professional business recommendations.
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
            "executive_summary":
                "Prepared a fallback marketing strategy.",
            "campaign": {
                "campaign_name": "Fallback Campaign",
                "objective": title,
                "target_audience": "Existing customers",
                "customer_pain_points": [],
                "value_proposition": "Improve customer engagement.",
                "offer": "Limited-time promotion",
                "call_to_action": "Contact us today",
                "channels": [
                    "Email",
                    "WhatsApp",
                ],
                "timeline": [
                    "Week 1",
                    "Week 2",
                ],
            },
            "messages": [],
            "recommended_actions": [
                "Launch campaign",
                "Track KPIs",
            ],
            "budget": {
                "currency": input_data.get("currency"),
                "estimated_total": 0,
                "allocation": [],
            },
            "kpis": [],
            "risks": [],
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }