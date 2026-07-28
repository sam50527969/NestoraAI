from __future__ import annotations

from typing import Any

from app.mission.models import MissionPlan, MissionTask
from app.objective.engine import ObjectiveEngineResult


class MissionPlanner:
    """
    Converts an Objective Engine result into a structured MissionPlan.

    This class contains planning logic only. It does not write to the
    database and does not execute tasks.

    Every generated mission ends with a Quality Control task so the
    outputs of all previous executives can be reviewed before the
    mission is considered ready for execution.
    """

    QUALITY_CONTROL_NAME = "Quality Control"

    QUALITY_CONTROL_ALIASES = {
        "quality control",
        "quality-control",
        "qualitycontrol",
        "quality assurance",
        "quality-assurance",
        "qa",
        "qc",
    }

    def create_plan(
        self,
        *,
        objective: str,
        engine_result: ObjectiveEngineResult,
    ) -> MissionPlan:
        analysis = engine_result.analysis
        strategy = engine_result.strategy

        opportunity = self._get_primary_opportunity(analysis)
        mission_title = self._build_title(
            opportunity,
            strategy,
        )

        estimated_value = self._read_float(
            opportunity,
            "estimated_value",
        )

        expected_roi = self._read_float(
            strategy,
            "estimated_roi",
        )

        priority = self._determine_priority(
            opportunity=opportunity,
            estimated_value=estimated_value,
        )

        executives = self._read_executives(opportunity)

        executives = self._ensure_quality_control(
            executives
        )

        tasks = self._build_tasks(
            objective=objective,
            executives=executives,
            priority=priority,
            estimated_value=estimated_value,
        )

        return MissionPlan(
            title=mission_title,
            objective=objective,
            description=self._build_description(
                objective=objective,
                opportunity=opportunity,
            ),
            priority=priority,
            estimated_value=estimated_value,
            expected_roi=expected_roi,
            strategy_data=self._to_dict(strategy),
            metadata={
                "source": "objective_engine",
                "opportunity": self._to_dict(
                    opportunity
                ),
                "quality_control_enabled": True,
            },
            tasks=tasks,
        )

    def _get_primary_opportunity(
        self,
        analysis: Any,
    ) -> Any:
        opportunities = getattr(
            analysis,
            "opportunities",
            None,
        )

        if isinstance(opportunities, list) and opportunities:
            return opportunities[0]

        opportunity = getattr(
            analysis,
            "opportunity",
            None,
        )

        if opportunity is not None:
            return opportunity

        return analysis

    def _build_title(
        self,
        opportunity: Any,
        strategy: Any,
    ) -> str:
        opportunity_title = self._read_text(
            opportunity,
            "title",
            "name",
            "opportunity",
        )

        if opportunity_title:
            return opportunity_title

        strategy_title = self._read_text(
            strategy,
            "title",
            "name",
        )

        if strategy_title:
            return strategy_title

        return "Business Growth Mission"

    def _build_description(
        self,
        *,
        objective: str,
        opportunity: Any,
    ) -> str:
        opportunity_description = self._read_text(
            opportunity,
            "description",
            "reason",
            "recommendation",
        )

        if opportunity_description:
            return opportunity_description

        return (
            "Execute a coordinated business mission to achieve the "
            f"following objective: {objective}"
        )

    def _determine_priority(
        self,
        *,
        opportunity: Any,
        estimated_value: float | None,
    ) -> str:
        explicit_priority = self._read_text(
            opportunity,
            "priority",
        )

        if explicit_priority:
            normalized = explicit_priority.lower()

            if normalized in {
                "low",
                "medium",
                "high",
                "critical",
            }:
                return normalized

        confidence = self._read_float(
            opportunity,
            "confidence",
        )

        if confidence is not None and confidence >= 0.85:
            return "high"

        if (
            estimated_value is not None
            and estimated_value >= 10000
        ):
            return "high"

        return "medium"

    def _read_executives(
        self,
        opportunity: Any,
    ) -> list[str]:
        value = getattr(
            opportunity,
            "executives",
            None,
        )

        if value is None:
            value = getattr(
                opportunity,
                "recommended_executives",
                None,
            )

        if isinstance(value, list):
            executives = [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

            if executives:
                return executives

        return [
            "Research",
            "Marketing",
            "Sales",
            "Follow-up",
            "Analytics",
        ]

    def _ensure_quality_control(
        self,
        executives: list[str],
    ) -> list[str]:
        """
        Return a clean executive sequence with Quality Control last.

        Any existing Quality Control alias is removed first, preventing
        duplicate QC tasks and guaranteeing that the review happens only
        after every operational executive has completed its work.
        """

        cleaned_executives: list[str] = []

        for executive in executives:
            normalized = self._normalize_executive_name(
                executive
            )

            if normalized in self.QUALITY_CONTROL_ALIASES:
                continue

            cleaned_executives.append(
                executive.strip()
            )

        cleaned_executives.append(
            self.QUALITY_CONTROL_NAME
        )

        return cleaned_executives

    def _build_tasks(
        self,
        *,
        objective: str,
        executives: list[str],
        priority: str,
        estimated_value: float | None,
    ) -> list[MissionTask]:
        tasks: list[MissionTask] = []
        previous_task_title: str | None = None

        for executive in executives:
            normalized = executive.strip()

            task_title = self._task_title_for_executive(
                executive=normalized,
                objective=objective,
            )

            task = MissionTask(
                title=task_title,
                description=(
                    self._task_description_for_executive(
                        executive=normalized,
                        objective=objective,
                    )
                ),
                executive=normalized,
                priority=priority,
                estimated_value=estimated_value,
                depends_on=previous_task_title,
            )

            tasks.append(task)
            previous_task_title = task_title

        return tasks

    def _task_title_for_executive(
        self,
        *,
        executive: str,
        objective: str,
    ) -> str:
        executive_key = self._normalize_executive_name(
            executive
        )

        titles = {
            "research": (
                "Research the business opportunity"
            ),
            "marketing": (
                "Prepare the marketing campaign"
            ),
            "sales": (
                "Prepare the sales conversion plan"
            ),
            "follow-up": (
                "Create the customer follow-up workflow"
            ),
            "followup": (
                "Create the customer follow-up workflow"
            ),
            "follow up": (
                "Create the customer follow-up workflow"
            ),
            "reception": (
                "Prepare customer contact and booking workflow"
            ),
            "analytics": (
                "Measure mission performance"
            ),
            "finance": (
                "Review mission budget and expected return"
            ),
            "operations": (
                "Prepare operational execution plan"
            ),
            "quality control": (
                "Review and approve mission quality"
            ),
            "quality-control": (
                "Review and approve mission quality"
            ),
            "qualitycontrol": (
                "Review and approve mission quality"
            ),
            "quality assurance": (
                "Review and approve mission quality"
            ),
            "quality-assurance": (
                "Review and approve mission quality"
            ),
            "qa": (
                "Review and approve mission quality"
            ),
            "qc": (
                "Review and approve mission quality"
            ),
        }

        return titles.get(
            executive_key,
            f"{executive} task for: {objective}",
        )

    def _task_description_for_executive(
        self,
        *,
        executive: str,
        objective: str,
    ) -> str:
        executive_key = self._normalize_executive_name(
            executive
        )

        descriptions = {
            "research": (
                "Collect and organize the business information required "
                f"to support the objective: {objective}"
            ),
            "marketing": (
                "Create the campaign message, audience, channel plan, "
                f"and offer required to support: {objective}"
            ),
            "sales": (
                "Create the sales outreach, qualification, objection "
                f"handling, and conversion process for: {objective}"
            ),
            "follow-up": (
                "Create a structured follow-up schedule and customer "
                f"re-engagement workflow for: {objective}"
            ),
            "followup": (
                "Create a structured follow-up schedule and customer "
                f"re-engagement workflow for: {objective}"
            ),
            "follow up": (
                "Create a structured follow-up schedule and customer "
                f"re-engagement workflow for: {objective}"
            ),
            "reception": (
                "Prepare the contact, response, appointment-booking, "
                f"and customer-handling workflow for: {objective}"
            ),
            "analytics": (
                "Define metrics, monitor results, and report whether the "
                f"mission achieved: {objective}"
            ),
            "finance": (
                "Review costs, expected revenue, profitability, and "
                f"financial risk related to: {objective}"
            ),
            "operations": (
                "Prepare the operational resources, schedule, and "
                f"execution controls required for: {objective}"
            ),
            "quality control": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
            "quality-control": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
            "qualitycontrol": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
            "quality assurance": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
            "quality-assurance": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
            "qa": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
            "qc": (
                "Review all previous executive outputs for consistency, "
                "completeness, contradictions, risks, and alignment with "
                f"the mission objective: {objective}. Provide a final "
                "quality score and determine whether the mission is ready "
                "for execution."
            ),
        }

        return descriptions.get(
            executive_key,
            (
                "Complete the assigned executive work required for: "
                f"{objective}"
            ),
        )

    @staticmethod
    def _normalize_executive_name(
        executive: str,
    ) -> str:
        return " ".join(
            executive.strip().lower().split()
        )

    @staticmethod
    def _read_text(
        source: Any,
        *field_names: str,
    ) -> str | None:
        for field_name in field_names:
            value = getattr(
                source,
                field_name,
                None,
            )

            if value is not None:
                text = str(value).strip()

                if text:
                    return text

        return None

    @staticmethod
    def _read_float(
        source: Any,
        field_name: str,
    ) -> float | None:
        value = getattr(
            source,
            field_name,
            None,
        )

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_dict(
        source: Any,
    ) -> dict[str, Any]:
        if source is None:
            return {}

        if hasattr(source, "__dict__"):
            return {
                key: value
                for key, value in vars(source).items()
                if not key.startswith("_")
            }

        return {
            "value": str(source)
        }