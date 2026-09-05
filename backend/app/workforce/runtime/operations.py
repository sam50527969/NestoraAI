from __future__ import annotations

import json
from typing import Any

from app.ai.operations_schema import OperationsReport
from app.workforce.runtime.base import BaseExecutive


class OperationsExecutive(BaseExecutive):
    """
    AI-powered Operations Executive.

    Reviews operational capacity, workload, utilization,
    cancellations, workflow execution and operational risk.
    """

    name = "Operations"

    response_model = OperationsReport

    @property
    def system_instruction(self) -> str:
        return (
            "You are Nestora's senior Operations Executive. "
            "Review supplied operational and mission data carefully. "
            "Identify capacity constraints, workflow improvements, "
            "bottlenecks and operational risks. Never invent operational "
            "figures, performance percentages or KPIs that were not "
            "supplied or clearly derived from supplied values."
        )

    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:
        return f"""
You are the Operations Executive for Nestora.

TASK

{title}

DESCRIPTION

{description or "No description supplied."}

BUSINESS AND MISSION DATA

{json.dumps(input_data, indent=2, ensure_ascii=False)}

Create a professional Operations execution report.

Your report must include:

1. Executive summary

2. Operational assessment
   Review only operational information actually available.

3. Workflow recommendations

4. Capacity actions

5. Process improvements

6. Recommended actions
   Each action should contain:
   - Title
   - Description
   - Priority
   - Expected impact

7. KPIs
   Each KPI should contain:
   - Name
   - Target
   - Measurement

8. Bottlenecks

9. Operational risks

Important rules:

- Do not invent capacity, volume, utilization, cancellation,
  efficiency or performance figures.
- Use supplied operational values when available.
- Clearly distinguish observed data from recommendations.
- If important operational data is missing, recommend what
  should be measured instead of fabricating a value.
- Do not claim a bottleneck exists unless the supplied data
  supports that conclusion.
- Use previous executive outputs and experience_reasoning
  when relevant.

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
        daily_capacity = self._as_number(
            input_data.get("daily_capacity")
        )
        average_daily_volume = self._as_number(
            input_data.get("average_daily_volume")
        )
        cancellation_rate = self._as_number(
            input_data.get("cancellation_rate")
        )
        utilization_rate = self._as_number(
            input_data.get("utilization_rate")
        )
        locations_count = self._as_number(
            input_data.get("locations_count")
        )

        observed = []

        if daily_capacity is not None:
            observed.append(
                f"Daily capacity: "
                f"{self._format_number(daily_capacity)}."
            )

        if average_daily_volume is not None:
            observed.append(
                f"Average daily volume: "
                f"{self._format_number(average_daily_volume)}."
            )

        if utilization_rate is not None:
            observed.append(
                f"Utilization rate: "
                f"{self._format_number(utilization_rate)}%."
            )

        if cancellation_rate is not None:
            observed.append(
                f"Cancellation rate: "
                f"{self._format_number(cancellation_rate)}%."
            )

        if locations_count is not None:
            observed.append(
                f"Locations: "
                f"{self._format_number(locations_count)}."
            )

        if observed:
            operational_assessment = " ".join(observed)
        else:
            operational_assessment = (
                "No verified capacity, workload, utilization or "
                "cancellation figures were supplied. Establish an "
                "operational baseline before making quantified decisions."
            )

        bottlenecks = []

        if (
            daily_capacity is not None
            and average_daily_volume is not None
            and daily_capacity > 0
            and average_daily_volume > daily_capacity
        ):
            bottlenecks.append(
                "Average daily volume exceeds supplied daily capacity."
            )

        risks = []

        if (
            daily_capacity is not None
            and average_daily_volume is not None
            and daily_capacity > 0
            and average_daily_volume > daily_capacity
        ):
            risks.append(
                "Demand above supplied capacity may create delays "
                "or service pressure."
            )

        if not risks:
            risks.append(
                "Operational decisions may be unreliable when capacity, "
                "volume or workflow performance data is incomplete."
            )

        if not bottlenecks:
            bottlenecks.append(
                "No verified operational bottleneck can be concluded "
                "from the supplied data."
            )

        return {
            "executive": self.name,
            "task_title": title,
            "status": "completed",
            "executive_summary": (
                "Prepared an operations review using only verified "
                "values available in the mission context."
            ),
            "operational_assessment": operational_assessment,
            "workflow_recommendations": [
                "Assign clear ownership for operational actions.",
                "Track blocked or delayed work through defined escalation.",
            ],
            "capacity_actions": [
                "Compare actual workload with available operating capacity.",
                "Review capacity before committing to additional demand.",
            ],
            "process_improvements": [
                "Define repeatable steps for recurring operational work.",
                "Track completion, delays and exceptions consistently.",
            ],
            "recommended_actions": [
                {
                    "title": "Establish operational baseline",
                    "description": (
                        "Maintain current capacity, workload, utilization "
                        "and cancellation data for executive analysis."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "More reliable capacity and workflow decisions."
                    ),
                },
                {
                    "title": "Review workflow execution",
                    "description": (
                        "Track ownership, progress, blocked work and "
                        "completion across operational tasks."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "Earlier identification of delays and bottlenecks."
                    ),
                },
            ],
            "kpis": [
                {
                    "name": "Capacity utilization",
                    "target": "Maintain a sustainable operating level",
                    "measurement": (
                        "Actual workload compared with available capacity"
                    ),
                },
                {
                    "name": "Cancellation rate",
                    "target": "Monitor and reduce avoidable cancellations",
                    "measurement": (
                        "Cancelled activity as a share of total activity"
                    ),
                },
            ],
            "bottlenecks": bottlenecks,
            "risks": risks,
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }

    @staticmethod
    def _as_number(value: Any) -> float | None:
        if value is None or isinstance(value, bool):
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_number(value: float) -> str:
        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.2f}"
