from __future__ import annotations

import inspect
from typing import Any

from app.schemas.marketing import MarketingDirectorResponse
from app.services.agents.executive_agent import (
    ExecutiveAgent,
    ExecutiveContext,
    ExecutiveRunStatus,
)
from app.services.marketing.analyzer import (
    MarketingAnalyzer,
    get_marketing_analyzer,
)
from app.services.marketing.budget_engine import (
    MarketingBudgetEngine,
    get_marketing_budget_engine,
)
from app.services.marketing.learning import (
    MarketingLearningEngine,
    get_marketing_learning_engine,
)
from app.services.marketing.planner import (
    MarketingCampaignPlanner,
    get_marketing_campaign_planner,
)
from app.services.marketing.predictor import (
    MarketingPredictionEngine,
    get_marketing_prediction_engine,
)
from app.services.marketing.strategist import (
    MarketingStrategist,
    get_marketing_strategist,
)


class MarketingDirectorError(RuntimeError):
    """Raised when the Marketing Director cannot complete its work."""


class MarketingDirector(ExecutiveAgent):
    """
    Nestora executive AI responsible for marketing.

    Workflow:

        Analyze
        Think
        Recommend
        Plan
        Predict
        Learn
    """

    AGENT_NAME = "Marketing Director"

    AGENT_DESCRIPTION = (
        "Analyzes a business, creates a marketing strategy, "
        "allocates budget, prepares campaigns, predicts results, "
        "and stores marketing learning."
    )

    TASK_NAME = "marketing_director"

    CAPABILITIES = {
        "executive_reasoning",
        "marketing_analysis",
        "marketing_strategy",
        "campaign_planning",
        "budget_allocation",
        "performance_prediction",
        "marketing_learning",
    }

    VERSION = "1.0.0"
    ENABLED = True
    STOP_ON_FAILURE = True

    def __init__(
        self,
        db,
        mission_id: str,
        request: Any,
        *,
        analyzer: MarketingAnalyzer | None = None,
        strategist: MarketingStrategist | None = None,
        planner: MarketingCampaignPlanner | None = None,
        budget_engine: MarketingBudgetEngine | None = None,
        prediction_engine: MarketingPredictionEngine | None = None,
        learning_engine: MarketingLearningEngine | None = None,
    ) -> None:
        super().__init__(
            db=db,
            mission_id=mission_id,
            request=request,
        )

        self.analyzer = (
            analyzer
            or get_marketing_analyzer()
        )

        self.strategist = (
            strategist
            or get_marketing_strategist()
        )

        self.planner = (
            planner
            or get_marketing_campaign_planner()
        )

        self.budget_engine = (
            budget_engine
            or get_marketing_budget_engine()
        )

        self.prediction_engine = (
            prediction_engine
            or get_marketing_prediction_engine()
        )

        self.learning_engine = (
            learning_engine
            or get_marketing_learning_engine()
        )

    async def execute(self) -> ExecutiveContext:
        """
        Execute the complete Marketing Director workflow.
        """

        await self.prepare()

        context = self._build_context()

        try:
            context = await super().run(context)

            if context.status in {
                ExecutiveRunStatus.COMPLETED,
                ExecutiveRunStatus.PARTIAL,
            }:
                await self.complete()
            else:
                self.task_failed(
                    self._failure_reason(context)
                )

            return context

        except Exception as exc:
            await self.rollback()

            self.task_failed(str(exc))

            self.update_status(
                status="failed",
                progress=0,
                current_task="Marketing workflow failed",
            )

            self.log(
                f"Marketing Director failed: {exc}"
            )

            raise MarketingDirectorError(
                "Marketing Director failed to complete "
                "the executive workflow."
            ) from exc

    async def prepare(self) -> None:
        """
        Validate the request and initialize mission tracking.
        """

        business = self._business()
        goal = self._goal()

        business_id = self._business_id(
            business
        )

        if not business_id:
            raise MarketingDirectorError(
                "The marketing request must contain a business ID."
            )

        objective = str(
            getattr(
                goal,
                "objective",
                "",
            )
            or ""
        ).strip()

        if not objective:
            raise MarketingDirectorError(
                "The marketing request must contain an objective."
            )

        self.task_start()
        self.task_progress(0)

        self.update_status(
            status="working",
            progress=0,
            current_task="Preparing marketing workflow",
        )

        self.log(
            "Marketing Director started the executive workflow."
        )

    async def complete(self) -> None:
        """
        Finalize tracking after successful execution.
        """

        self.task_progress(100)

        self.update_status(
            status="completed",
            progress=100,
            current_task="Marketing workflow completed",
        )

        self.update_mission(
            current_step="Marketing Director completed",
        )

        self.log(
            "Marketing Director completed the executive workflow."
        )

    async def rollback(self) -> None:
        """
        Record a safe rollback event.

        This workflow does not publish campaigns or spend money.
        """

        self.log(
            "Marketing Director stopped before external execution. "
            "No campaign was published and no advertising spend occurred."
        )

    async def analyze(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Analyze the business and marketing situation.
        """

        self._stage_status(
            progress=10,
            task="Analyzing business and market position",
        )

        analysis = await self.analyzer.analyze(
            business=self._business(),
            goal=self._goal(),
            additional_instructions=(
                self._additional_instructions()
            ),
        )

        self.log(
            "Business and marketing analysis completed."
        )

        return analysis

    async def think(
        self,
        context: ExecutiveContext,
    ) -> dict[str, Any]:
        """
        Convert the analysis into executive reasoning.
        """

        self._require_stage_output(
            context.analysis,
            "Business analysis",
        )

        self._stage_status(
            progress=25,
            task="Interpreting marketing analysis",
        )

        analysis = context.analysis

        thinking = {
            "business_summary": (
                analysis.business_summary
            ),
            "audience_summary": (
                analysis.audience_summary
            ),
            "positioning": (
                analysis.recommended_positioning
            ),
            "strength_count": len(
                analysis.strengths
            ),
            "weakness_count": len(
                analysis.weaknesses
            ),
            "opportunity_count": len(
                analysis.opportunities
            ),
            "risk_count": len(
                analysis.risks
            ),
            "confidence": analysis.confidence,
            "executive_interpretation": (
                self._executive_interpretation(
                    analysis
                )
            ),
        }

        self.log(
            "Marketing analysis interpreted at executive level."
        )

        return thinking

    async def recommend(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Create the recommended marketing strategy.
        """

        self._require_stage_output(
            context.analysis,
            "Business analysis",
        )

        self._stage_status(
            progress=40,
            task="Creating marketing strategy",
        )

        strategy = await self.strategist.create_strategy(
            business=self._business(),
            goal=self._goal(),
            analysis=context.analysis,
            additional_instructions=(
                self._additional_instructions()
            ),
        )

        self.log(
            "Marketing strategy created."
        )

        return strategy

    async def plan(
        self,
        context: ExecutiveContext,
    ) -> dict[str, Any]:
        """
        Create the campaign and budget plans.
        """

        self._require_stage_output(
            context.recommendations,
            "Marketing strategy",
        )

        self._stage_status(
            progress=60,
            task="Building campaign and budget plan",
        )

        strategy = context.recommendations

        budget = await self._call_service(
            service=self.budget_engine,
            method_names=(
                "create_budget_plan",
                "allocate_budget",
                "build_budget",
                "plan_budget",
            ),
            kwargs={
                "business": self._business(),
                "goal": self._goal(),
                "strategy": strategy,
            },
        )

        campaign = await self.planner.create_campaign(
            business=self._business(),
            goal=self._goal(),
            strategy=strategy,
            additional_instructions=(
                self._additional_instructions()
            ),
        )

        self.log(
            "Campaign plan and budget allocation completed."
        )

        return {
            "budget": budget,
            "campaign": campaign,
        }

    async def predict(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Predict expected marketing performance.
        """

        self._require_stage_output(
            context.recommendations,
            "Marketing strategy",
        )

        self._require_stage_output(
            context.plan,
            "Marketing plan",
        )

        self._stage_status(
            progress=78,
            task="Predicting marketing performance",
        )

        strategy = context.recommendations
        budget = context.plan["budget"]
        campaign = context.plan["campaign"]

        prediction = await self._call_service(
            service=self.prediction_engine,
            method_names=(
                "predict",
                "create_prediction",
                "predict_performance",
                "estimate_results",
            ),
            kwargs={
                "business": self._business(),
                "goal": self._goal(),
                "strategy": strategy,
                "budget": budget,
                "campaign": campaign,
            },
        )

        self.log(
            "Marketing performance prediction completed."
        )

        return prediction

    async def learn(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Store marketing insights for future decisions.
        """

        self._require_stage_output(
            context.analysis,
            "Business analysis",
        )

        self._require_stage_output(
            context.recommendations,
            "Marketing strategy",
        )

        self._require_stage_output(
            context.plan,
            "Marketing plan",
        )

        self._require_stage_output(
            context.prediction,
            "Marketing prediction",
        )

        self._stage_status(
            progress=92,
            task="Saving marketing learning",
        )

        learning = await self._call_service(
            service=self.learning_engine,
            method_names=(
                "record_marketing_run",
                "learn",
                "store_learning",
            ),
            kwargs={
                "business": self._business(),
                "goal": self._goal(),
                "analysis": context.analysis,
                "strategy": context.recommendations,
                "budget": context.plan["budget"],
                "campaign": context.plan["campaign"],
                "prediction": context.prediction,
            },
        )

        warnings = self._learning_value(
            learning,
            "warnings",
            [],
        )

        if isinstance(warnings, list):
            for warning in warnings:
                context.add_warning(
                    str(warning)
                )

        self.log(
            "Marketing insights stored in Business Memory."
        )

        return learning

    def build_response(
        self,
        context: ExecutiveContext,
    ) -> MarketingDirectorResponse:
        """
        Convert the completed workflow into the exact API response schema.
        """

        if context.analysis is None:
            raise MarketingDirectorError(
                "Marketing analysis is missing."
            )

        if context.recommendations is None:
            raise MarketingDirectorError(
                "Marketing strategy is missing."
            )

        if not isinstance(
            context.plan,
            dict,
        ):
            raise MarketingDirectorError(
                "Marketing plan is missing."
            )

        budget = context.plan.get(
            "budget"
        )

        campaign = context.plan.get(
            "campaign"
        )

        if budget is None:
            raise MarketingDirectorError(
                "Marketing budget plan is missing."
            )

        if campaign is None:
            raise MarketingDirectorError(
                "Marketing campaign plan is missing."
            )

        if context.prediction is None:
            raise MarketingDirectorError(
                "Marketing prediction is missing."
            )

        memory_entries_created = self._learning_value(
            context.learning,
            "memory_entries_created",
            0,
        )

        try:
            memory_entries_created = max(
                int(memory_entries_created),
                0,
            )
        except (
            TypeError,
            ValueError,
        ):
            memory_entries_created = 0

        return MarketingDirectorResponse(
            business_id=context.business_id,
            analysis=context.analysis,
            strategy=context.recommendations,
            budget=budget,
            campaign=campaign,
            prediction=context.prediction,
            memory_entries_created=(
                memory_entries_created
            ),
            approval_required=(
                campaign.approval_required
            ),
        )

    def _build_context(
        self,
    ) -> ExecutiveContext:
        business = self._business()
        goal = self._goal()

        return ExecutiveContext(
            business_id=self._business_id(
                business
            ),
            objective=str(
                getattr(
                    goal,
                    "objective",
                    "",
                )
            ),
            input_data=self._serialize(
                self.request
            ),
            metadata={
                "executive": self.AGENT_NAME,
                "version": self.VERSION,
                "mission_id": self.mission_id,
            },
        )

    def _business(self) -> Any:
        business = self._request_value(
            "business",
            "business_profile",
        )

        if business is None:
            raise MarketingDirectorError(
                "Marketing request does not contain "
                "a business profile."
            )

        return business

    def _goal(self) -> Any:
        goal = self._request_value(
            "goal",
            "marketing_goal",
        )

        if goal is None:
            raise MarketingDirectorError(
                "Marketing request does not contain "
                "a marketing goal."
            )

        return goal

    def _additional_instructions(
        self,
    ) -> str | None:
        value = self._request_value(
            "additional_instructions",
            "instructions",
        )

        if value is None:
            return None

        cleaned = str(value).strip()

        return cleaned or None

    def _request_value(
        self,
        *names: str,
    ) -> Any:
        for name in names:
            if hasattr(
                self.request,
                name,
            ):
                return getattr(
                    self.request,
                    name,
                )

            if (
                isinstance(
                    self.request,
                    dict,
                )
                and name in self.request
            ):
                return self.request[name]

        return None

    @staticmethod
    def _business_id(
        business: Any,
    ) -> str:
        if isinstance(
            business,
            dict,
        ):
            value = business.get(
                "business_id",
                "",
            )
        else:
            value = getattr(
                business,
                "business_id",
                "",
            )

        return str(
            value or ""
        ).strip()

    async def _call_service(
        self,
        *,
        service: Any,
        method_names: tuple[str, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        """
        Call a compatible method exposed by a marketing service.
        """

        method = None

        for method_name in method_names:
            candidate = getattr(
                service,
                method_name,
                None,
            )

            if callable(candidate):
                method = candidate
                break

        if method is None:
            raise MarketingDirectorError(
                f"{type(service).__name__} does not expose "
                f"a supported method. Expected one of: "
                f"{', '.join(method_names)}."
            )

        signature = inspect.signature(
            method
        )

        accepts_all_kwargs = any(
            parameter.kind
            == inspect.Parameter.VAR_KEYWORD
            for parameter
            in signature.parameters.values()
        )

        if accepts_all_kwargs:
            accepted_kwargs = kwargs
        else:
            accepted_kwargs = {
                name: value
                for name, value
                in kwargs.items()
                if name
                in signature.parameters
            }

        result = method(
            **accepted_kwargs
        )

        if inspect.isawaitable(result):
            return await result

        return result

    def _stage_status(
        self,
        *,
        progress: int,
        task: str,
    ) -> None:
        self.task_progress(
            progress
        )

        self.update_status(
            status="working",
            progress=progress,
            current_task=task,
        )

        self.update_mission(
            current_step=task,
        )

    @staticmethod
    def _require_stage_output(
        output: Any,
        name: str,
    ) -> None:
        if output is None:
            raise MarketingDirectorError(
                f"{name} is required before continuing."
            )

    @staticmethod
    def _executive_interpretation(
        analysis: Any,
    ) -> str:
        if (
            analysis.risks
            and analysis.weaknesses
        ):
            return (
                "The business has viable marketing opportunities, "
                "but execution should begin with controlled testing, "
                "clear measurement, and early risk management."
            )

        if analysis.opportunities:
            return (
                "The business has a usable foundation for growth. "
                "The recommended strategy should focus resources on "
                "the strongest measurable opportunities."
            )

        return (
            "The business requires further marketing validation "
            "before significant budget or execution commitments."
        )

    @staticmethod
    def _learning_value(
        learning: Any,
        key: str,
        default: Any,
    ) -> Any:
        if learning is None:
            return default

        if isinstance(
            learning,
            dict,
        ):
            return learning.get(
                key,
                default,
            )

        return getattr(
            learning,
            key,
            default,
        )

    @staticmethod
    def _serialize(
        value: Any,
    ) -> Any:
        if value is None:
            return None

        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(model_dump):
            return model_dump(
                mode="json"
            )

        to_dict = getattr(
            value,
            "to_dict",
            None,
        )

        if callable(to_dict):
            return to_dict()

        if isinstance(
            value,
            dict,
        ):
            return {
                key: MarketingDirector._serialize(
                    item
                )
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (list, tuple),
        ):
            return [
                MarketingDirector._serialize(
                    item
                )
                for item in value
            ]

        return value

    @staticmethod
    def _failure_reason(
        context: ExecutiveContext,
    ) -> str:
        if context.errors:
            return "; ".join(
                context.errors
            )

        return (
            "Marketing Director workflow did not "
            "complete successfully."
        )