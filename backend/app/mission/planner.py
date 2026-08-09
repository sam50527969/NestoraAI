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
            objective=objective,
            opportunity=opportunity,
            strategy=strategy,
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

        executives = self._collect_executives(
            analysis=analysis,
            strategy=strategy,
            objective=objective,
        )

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
        *,
        objective: str,
        opportunity: Any,
        strategy: Any,
    ) -> str:
        """
        Build a mission title that represents the whole objective.

        Strategy-level intent is preferred over a single opportunity so a
        coordinated growth mission is not accidentally named after the first
        detected opportunity.
        """

        strategy_title = self._read_text(
            strategy,
            "title",
            "name",
        )

        if strategy_title:
            return self._compact_title(
                strategy_title
            )

        objective_title = self._title_from_objective(
            objective
        )

        if objective_title:
            return objective_title

        opportunity_title = self._read_text(
            opportunity,
            "title",
            "name",
            "opportunity",
        )

        if opportunity_title:
            return self._compact_title(
                opportunity_title
            )

        return "Business Growth Mission"

    def _build_description(
        self,
        *,
        objective: str,
        opportunity: Any,
    ) -> str:
        """
        Keep the persisted mission description aligned with the submitted
        business objective instead of replacing it with one opportunity.
        """

        compact_objective = self._compact_objective(
            objective,
            max_length=360,
        )

        if compact_objective:
            return compact_objective

        opportunity_description = self._read_text(
            opportunity,
            "description",
            "reason",
            "recommendation",
        )

        if opportunity_description:
            return self._compact_objective(
                opportunity_description,
                max_length=360,
            )

        return "Execute the approved business growth mission."

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

    def _collect_executives(
        self,
        *,
        analysis: Any,
        strategy: Any,
        objective: str,
    ) -> list[str]:
        """
        Build one coordinated executive sequence from the full analysis.

        The previous planner used only the first opportunity. That could make
        a broad growth mission behave like a narrow retention or marketing
        mission. This method combines strategy-level executives, executives
        from all opportunities, and conservative objective-based fallbacks.
        """

        collected: list[str] = []

        def add_many(values: Any) -> None:
            if not isinstance(values, list):
                return

            for value in values:
                cleaned = str(value or "").strip()

                if not cleaned:
                    continue

                normalized = self._normalize_executive_name(
                    cleaned
                )

                if any(
                    self._normalize_executive_name(existing)
                    == normalized
                    for existing in collected
                ):
                    continue

                collected.append(cleaned)

        add_many(
            getattr(
                strategy,
                "executives",
                None,
            )
        )

        opportunities = getattr(
            analysis,
            "opportunities",
            None,
        )

        if isinstance(opportunities, list):
            for opportunity in opportunities:
                add_many(
                    getattr(
                        opportunity,
                        "executives",
                        None,
                    )
                )

                add_many(
                    getattr(
                        opportunity,
                        "recommended_executives",
                        None,
                    )
                )

        objective_key = self._normalize_executive_name(
            objective
        )

        objective_defaults: list[str] = []

        if any(
            term in objective_key
            for term in {
                "marketing",
                "seo",
                "advertising",
                "campaign",
                "content",
                "visibility",
                "reputation",
                "acquisition",
            }
        ):
            objective_defaults.append(
                "Marketing"
            )

        if any(
            term in objective_key
            for term in {
                "sales",
                "lead",
                "enquir",
                "conversion",
                "appointment",
                "customer acquisition",
            }
        ):
            objective_defaults.append(
                "Sales"
            )

        if any(
            term in objective_key
            for term in {
                "follow-up",
                "follow up",
                "crm",
                "nurtur",
                "retention",
                "re-engagement",
            }
        ):
            objective_defaults.append(
                "Follow-up"
            )

        if any(
            term in objective_key
            for term in {
                "growth",
                "roi",
                "performance",
                "measure",
                "analytics",
                "optimiz",
            }
        ):
            objective_defaults.append(
                "Analytics"
            )

        add_many(
            objective_defaults
        )

        if not collected:
            collected = [
                "Research",
                "Marketing",
                "Sales",
                "Follow-up",
                "Analytics",
            ]

        return collected

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
        """Build a short, action-oriented title for each executive."""
        executive_key = self._normalize_executive_name(executive)

        titles = {
            "research": "Research Market & Growth Opportunities",
            "customer success": "Build Customer Retention & Experience Plan",
            "customer-success": "Build Customer Retention & Experience Plan",
            "customersuccess": "Build Customer Retention & Experience Plan",
            "marketing": "Launch Customer Acquisition Campaign",
            "sales": "Create Lead Conversion & Sales Plan",
            "follow-up": "Implement Automated Lead Follow-up",
            "followup": "Implement Automated Lead Follow-up",
            "follow up": "Implement Automated Lead Follow-up",
            "reception": "Build Contact & Booking Workflow",
            "analytics": "Track Growth & Conversion Performance",
            "finance": "Review Budget, ROI & Financial Risk",
            "operations": "Prepare Operational Execution Plan",
            "quality control": "Review Mission Quality & Readiness",
            "quality-control": "Review Mission Quality & Readiness",
            "qualitycontrol": "Review Mission Quality & Readiness",
            "quality assurance": "Review Mission Quality & Readiness",
            "quality-assurance": "Review Mission Quality & Readiness",
            "qa": "Review Mission Quality & Readiness",
            "qc": "Review Mission Quality & Readiness",
        }

        if executive_key in titles:
            return titles[executive_key]

        cleaned_executive = " ".join(str(executive or "").split()).strip()
        if cleaned_executive:
            return self._compact_title(
                f"Execute {cleaned_executive} Action Plan",
                max_length=90,
            )

        return "Execute Mission Action Plan"

    def _task_description_for_executive(
        self,
        *,
        executive: str,
        objective: str,
    ) -> str:
        """Build a concise executive-specific instruction."""
        executive_key = self._normalize_executive_name(executive)
        compact_objective = self._compact_objective(
            objective,
            max_length=220,
        )

        descriptions = {
            "research": (
                "Research the market, competitors, customer needs, and growth "
                "opportunities required to support this objective: "
                f"{compact_objective}"
            ),
            "customer success": (
                "Design the customer experience, retention, re-engagement, and "
                "service actions needed to support this objective: "
                f"{compact_objective}"
            ),
            "customer-success": (
                "Design the customer experience, retention, re-engagement, and "
                "service actions needed to support this objective: "
                f"{compact_objective}"
            ),
            "customersuccess": (
                "Design the customer experience, retention, re-engagement, and "
                "service actions needed to support this objective: "
                f"{compact_objective}"
            ),
            "marketing": (
                "Create the campaign message, target audience, channel mix, "
                "offer, content direction, and acquisition actions needed to "
                f"support this objective: {compact_objective}"
            ),
            "sales": (
                "Create the lead qualification, outreach, objection handling, "
                "booking, and conversion process required to support this "
                f"objective: {compact_objective}"
            ),
            "follow-up": (
                "Create the CRM follow-up sequence, response timing, reminders, "
                "lead nurturing, and re-engagement workflow required to support "
                f"this objective: {compact_objective}"
            ),
            "followup": (
                "Create the CRM follow-up sequence, response timing, reminders, "
                "lead nurturing, and re-engagement workflow required to support "
                f"this objective: {compact_objective}"
            ),
            "follow up": (
                "Create the CRM follow-up sequence, response timing, reminders, "
                "lead nurturing, and re-engagement workflow required to support "
                f"this objective: {compact_objective}"
            ),
            "reception": (
                "Design the enquiry response, contact handling, appointment "
                "booking, confirmation, and customer handoff workflow required "
                f"to support this objective: {compact_objective}"
            ),
            "analytics": (
                "Define KPIs for leads, conversion, acquisition cost, revenue, "
                "and ROI. Measure mission performance and identify optimization "
                f"actions for this objective: {compact_objective}"
            ),
            "finance": (
                "Review budget allocation, expected revenue, ROI, profitability, "
                "and financial risk associated with this objective: "
                f"{compact_objective}"
            ),
            "operations": (
                "Define the resources, responsibilities, schedule, dependencies, "
                "and operating controls required to execute this objective: "
                f"{compact_objective}"
            ),
            "quality control": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
            "quality-control": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
            "qualitycontrol": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
            "quality assurance": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
            "quality-assurance": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
            "qa": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
            "qc": (
                "Review all executive outputs for completeness, consistency, "
                "contradictions, risks, and alignment with the objective. "
                "Provide a final quality assessment and determine whether the "
                f"mission is ready for use: {compact_objective}"
            ),
        }

        return descriptions.get(
            executive_key,
            (
                f"Complete the {executive} work required to support the "
                f"mission objective: {compact_objective}"
            ),
        )

    @staticmethod
    def _compact_title(
        value: str,
        max_length: int = 90,
    ) -> str:
        cleaned = " ".join(
            str(value or "").split()
        ).strip()

        if not cleaned:
            return "Business Growth Mission"

        if len(cleaned) <= max_length:
            return cleaned

        shortened = cleaned[
            : max_length - 3
        ].rstrip()

        return f"{shortened}..."

    @classmethod
    def _title_from_objective(
        cls,
        objective: str,
    ) -> str:
        normalized = " ".join(
            str(objective or "").split()
        ).strip()

        lowered = normalized.lower()

        if "seo growth mission" in lowered:
            return "SEO Growth Mission"

        if (
            "paid acquisition mission" in lowered
            or "advertising mission" in lowered
        ):
            return "Paid Acquisition Mission"

        if (
            "crm follow-up mission" in lowered
            or "crm follow up mission" in lowered
        ):
            return "CRM Follow-up Mission"

        if "coordinated growth mission" in lowered:
            return "Business Growth Mission"

        return cls._compact_title(
            normalized,
            max_length=90,
        )

    @staticmethod
    def _compact_objective(
        value: str,
        *,
        max_length: int,
    ) -> str:
        cleaned = " ".join(
            str(value or "").split()
        ).strip()

        if len(cleaned) <= max_length:
            return cleaned

        shortened = cleaned[
            : max_length - 3
        ]

        last_sentence = shortened.rfind(
            "."
        )
        last_separator = max(
            shortened.rfind(";"),
            shortened.rfind(","),
        )

        safe_cut = (
            last_sentence + 1
            if last_sentence >= max_length // 2
            else last_separator
            if last_separator >= max_length // 2
            else len(shortened)
        )

        return (
            shortened[:safe_cut]
            .rstrip(" ,;")
            + "..."
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