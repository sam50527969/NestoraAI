import json
from typing import Any

from app.ai.followup_schema import FollowupReport
from app.ai.gemini_provider import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiProvider,
)


class FollowUpExecutive:
    """
    AI-powered Follow-up Executive.

    Responsible for:
    - Customer follow-up
    - Lead nurturing
    - Appointment reminders
    - Customer reactivation
    - WhatsApp and email sequences
    """

    name = "Follow-up"

    def execute(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = self._build_prompt(
            title=title,
            description=description,
            input_data=input_data,
        )

        try:
            provider = GeminiProvider()

            report = provider.generate_structured(
                prompt=prompt,
                response_model=FollowupReport,
                system_instruction=(
                    "You are Nestora's senior Follow-up Executive. "
                    "Design professional customer follow-up strategies "
                    "that increase retention, appointment attendance, "
                    "reactivation, and customer loyalty. "
                    "Provide practical, ethical, and specific business "
                    "actions. Do not invent facts that were not provided."
                ),
            )

            result = report.model_dump()

            result["source_description"] = description
            result["input_data"] = input_data
            result["ai_provider"] = "Gemini"

            return result

        except (
            GeminiConfigurationError,
            GeminiGenerationError,
        ) as exc:
            return self._fallback_output(
                title=title,
                description=description,
                input_data=input_data,
                error_message=str(exc),
            )

    def _build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:
        safe_description = (
            description
            or "No additional task description was provided."
        )

        serialized_input = json.dumps(
            input_data,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        return f"""
Create a complete follow-up execution report for this mission task.

Task title:
{title}

Task description:
{safe_description}

Mission and business context:
{serialized_input}

Requirements:

- Write a concise executive summary.
- Create a practical multi-day follow-up sequence.
- Include WhatsApp and email messages where appropriate.
- Include appointment reminders where relevant.
- Define the purpose of each message.
- Recommend clear operational actions.
- Include measurable KPIs.
- Include risks and safeguards.
- Keep the plan aligned with the mission objective.
- Do not claim access to customer data that was not provided.
- Do not include explanations about being an AI.
""".strip()

    def _fallback_output(
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
                "Prepared a fallback customer follow-up strategy "
                "because the AI provider was unavailable."
            ),
            "strategy": [
                "Segment inactive customers by recency.",
                "Contact customers using approved communication channels.",
                "Track responses, bookings, and reactivations.",
            ],
            "followup_sequence": [
                {
                    "day": 1,
                    "channel": "WhatsApp",
                    "subject": "Welcome Back",
                    "message": (
                        "We would be happy to welcome you back. "
                        "Please let us know how we can assist you."
                    ),
                    "objective": (
                        "Reconnect with inactive customers."
                    ),
                },
                {
                    "day": 3,
                    "channel": "Email",
                    "subject": "A Reason to Return",
                    "message": (
                        "We have prepared a limited-time return offer "
                        "for selected customers. Contact us to learn more."
                    ),
                    "objective": (
                        "Encourage a reply or booking."
                    ),
                },
                {
                    "day": 7,
                    "channel": "WhatsApp",
                    "subject": "Final Reminder",
                    "message": (
                        "This is a friendly reminder that your return "
                        "offer is available for a limited time."
                    ),
                    "objective": (
                        "Create urgency without excessive messaging."
                    ),
                },
            ],
            "recommended_actions": [
                "Confirm customer consent before messaging.",
                "Prioritize customers with recent previous activity.",
                "Assign staff to respond quickly to replies.",
                "Track response and booking rates.",
            ],
            "kpis": [
                {
                    "name": "Response Rate",
                    "target": "15% or higher",
                    "measurement_method": (
                        "Customer replies divided by delivered messages."
                    ),
                },
                {
                    "name": "Booking Rate",
                    "target": "8% or higher",
                    "measurement_method": (
                        "Bookings divided by customers contacted."
                    ),
                },
                {
                    "name": "Reactivation Rate",
                    "target": "5% or higher",
                    "measurement_method": (
                        "Returning customers divided by customers contacted."
                    ),
                },
            ],
            "risks": [
                "Too many messages may frustrate customers.",
                "Unclear consent may create compliance concerns.",
                "Slow staff responses may reduce conversion rates.",
            ],
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }