import json
from typing import Any

from app.ai.gemini_provider import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiProvider,
)
from app.ai.quality_control_schema import QualityControlReport


class QualityControlExecutive:
    """
    AI-powered Quality Control Executive.

    Responsible for:
    - Reviewing the outputs of previous executives
    - Detecting contradictions and missing information
    - Scoring mission quality and consistency
    - Identifying operational and compliance risks
    - Determining whether work is ready for execution
    """

    name = "Quality Control"

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
                response_model=QualityControlReport,
                system_instruction=(
                    "You are Nestora's senior Quality Control Executive. "
                    "Review the work produced by other business executives "
                    "before it is approved for execution. "
                    "Be objective, strict, practical, and evidence-based. "
                    "Detect contradictions, missing information, unsupported "
                    "claims, operational risks, and inconsistent instructions. "
                    "Do not invent facts that were not provided. "
                    "Approve work only when it is sufficiently complete, "
                    "consistent, practical, ethical, and aligned with the "
                    "mission objective."
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

        executive_context = input_data.get(
            "executive_context",
            {},
        )

        serialized_mission_input = json.dumps(
            input_data,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        serialized_executive_context = json.dumps(
            executive_context,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        return f"""
Perform a complete quality-control review of this mission.

Quality-control task title:
{title}

Task description:
{safe_description}

Complete mission and business context:
{serialized_mission_input}

Outputs produced by previous executives:
{serialized_executive_context}

Review requirements:

1. Review every executive output available in executive_context.

2. Give each reviewed executive a score between 0 and 100.

3. Check whether all outputs support the same mission objective.

4. Detect contradictions, including:
   - Different discounts or promotional offers
   - Conflicting timelines
   - Conflicting target audiences
   - Conflicting budgets
   - Conflicting KPIs
   - Conflicting calls to action
   - Inconsistent customer messages
   - Incompatible operational instructions

5. Check completeness, including:
   - Clear objective
   - Target audience
   - Action plan
   - Responsible channel or department
   - Timeline or sequence
   - KPIs
   - Risks
   - Recommended actions
   - Customer-facing communication where applicable

6. Identify unsupported assumptions or claims.

7. Identify legal, ethical, privacy, consent, customer-experience,
   financial, or operational risks where relevant.

8. Do not criticize an executive for information that was not required
   for its role.

9. Do not invent business facts, customer data, financial results,
   permissions, integrations, or completed actions.

10. Set approved_for_execution to true only when:
    - The work is consistent
    - There are no serious contradictions
    - The mission is sufficiently complete
    - The recommendations are practical
    - No critical risk prevents execution

11. Use these approval statuses:
    - Approved
    - Approved with Recommendations
    - Revision Required

12. Use the following general scoring guidance:
    - 90 to 100: Excellent and execution-ready
    - 75 to 89: Good, with minor improvements
    - 60 to 74: Significant improvements required
    - Below 60: Not ready for execution

13. Keep the executive summary concise and business-focused.

14. Do not include explanations about being an AI.
""".strip()

    def _fallback_output(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
        error_message: str,
    ) -> dict[str, Any]:
        executive_context = input_data.get(
            "executive_context",
            {},
        )

        executive_reviews: list[dict[str, Any]] = []

        for executive_name, context_entry in executive_context.items():
            task_title = None

            if isinstance(context_entry, dict):
                task_title = context_entry.get("task_title")

            strengths = [
                "The executive completed and persisted an output."
            ]

            if task_title:
                strengths.append(
                    f"Completed the assigned task: {task_title}."
                )

            executive_reviews.append(
                {
                    "executive_name": executive_name,
                    "score": 70,
                    "strengths": strengths,
                    "issues": [
                        (
                            "Automated AI quality review was unavailable, "
                            "so detailed validation could not be completed."
                        )
                    ],
                    "recommendations": [
                        (
                            "Review this executive output manually before "
                            "performing external business actions."
                        )
                    ],
                }
            )

        if not executive_reviews:
            executive_reviews.append(
                {
                    "executive_name": "Mission",
                    "score": 40,
                    "strengths": [
                        "The quality-control task was created successfully."
                    ],
                    "issues": [
                        "No previous executive outputs were available."
                    ],
                    "recommendations": [
                        (
                            "Complete the required mission tasks before "
                            "requesting final quality approval."
                        )
                    ],
                }
            )

        return {
            "executive": self.name,
            "task_title": title,
            "status": "completed",
            "approval_status": "Revision Required",
            "overall_score": 60,
            "consistency_score": 60,
            "completeness_score": 60,
            "executive_summary": (
                "A limited fallback quality review was completed because "
                "the AI provider was unavailable. Manual review is required "
                "before the mission is approved for execution."
            ),
            "executive_reviews": executive_reviews,
            "contradictions": [],
            "missing_items": [
                (
                    "A complete AI-powered contradiction and completeness "
                    "review could not be performed."
                )
            ],
            "risks": [
                (
                    "Unreviewed inconsistencies may remain in the outputs "
                    "produced by previous executives."
                )
            ],
            "recommendations": [
                (
                    "Manually compare all offers, timelines, KPIs, messages, "
                    "budgets, and operational instructions."
                ),
                (
                    "Repeat the Quality Control task after the AI provider "
                    "becomes available."
                ),
            ],
            "approved_for_execution": False,
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }