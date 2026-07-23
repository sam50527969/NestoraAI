from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from app.services.agents.agent_base import BaseAgent


class ExecutiveStage(str, Enum):
    ANALYZE = "analyze"
    THINK = "think"
    RECOMMEND = "recommend"
    PLAN = "plan"
    PREDICT = "predict"
    LEARN = "learn"


class ExecutiveRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class ExecutiveStageResult:
    stage: ExecutiveStage
    success: bool
    output: Any = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at is None or self.completed_at is None:
            return None

        return round(
            (
                self.completed_at
                - self.started_at
            ).total_seconds(),
            4,
        )


@dataclass
class ExecutiveContext:
    business_id: str
    objective: str

    run_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    input_data: dict[str, Any] = field(
        default_factory=dict
    )

    analysis: Any = None
    thinking: Any = None
    recommendations: Any = None
    plan: Any = None
    prediction: Any = None
    learning: Any = None

    stage_results: dict[
        ExecutiveStage,
        ExecutiveStageResult,
    ] = field(default_factory=dict)

    warnings: list[str] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    status: ExecutiveRunStatus = (
        ExecutiveRunStatus.PENDING
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    completed_at: datetime | None = None

    def set_stage_result(
        self,
        result: ExecutiveStageResult,
    ) -> None:
        self.stage_results[result.stage] = result

    def add_warning(
        self,
        message: str,
    ) -> None:
        cleaned = message.strip()

        if cleaned and cleaned not in self.warnings:
            self.warnings.append(cleaned)

    def add_error(
        self,
        message: str,
    ) -> None:
        cleaned = message.strip()

        if cleaned and cleaned not in self.errors:
            self.errors.append(cleaned)

    def stage_succeeded(
        self,
        stage: ExecutiveStage,
    ) -> bool:
        result = self.stage_results.get(stage)

        return bool(
            result
            and result.success
        )

    def summary(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "business_id": self.business_id,
            "objective": self.objective,
            "status": self.status.value,
            "analysis": self.analysis,
            "thinking": self.thinking,
            "recommendations": self.recommendations,
            "plan": self.plan,
            "prediction": self.prediction,
            "learning": self.learning,
            "warnings": self.warnings,
            "errors": self.errors,
            "stages": {
                stage.value: {
                    "success": result.success,
                    "error": result.error,
                    "duration_seconds": (
                        result.duration_seconds
                    ),
                    "metadata": result.metadata,
                }
                for stage, result
                in self.stage_results.items()
            },
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
        }


class ExecutiveAgent(BaseAgent, ABC):
    """
    Shared lifecycle for Nestora executive AI agents.

    Executive agents follow this sequence:

        Analyze
        Think
        Recommend
        Plan
        Predict
        Learn

    Individual executives may override any stage or disable
    optional stages.
    """

    AGENT_DESCRIPTION = (
        "Base framework for Nestora executive AI agents."
    )

    VERSION = "1.0.0"

    ENABLED = True

    CAPABILITIES = {
        "executive_reasoning",
        "business_analysis",
        "recommendations",
        "planning",
        "prediction",
        "learning",
    }

    REQUIRED_STAGES: tuple[
        ExecutiveStage,
        ...,
    ] = (
        ExecutiveStage.ANALYZE,
        ExecutiveStage.THINK,
        ExecutiveStage.RECOMMEND,
        ExecutiveStage.PLAN,
        ExecutiveStage.PREDICT,
        ExecutiveStage.LEARN,
    )

    STOP_ON_FAILURE = True

    async def run(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveContext:
        """
        Execute the complete executive lifecycle.
        """

        context.status = ExecutiveRunStatus.RUNNING

        await self._update_progress(
            task_id=context.run_id,
            progress=0,
            message="Executive workflow started.",
        )

        stages = list(self.REQUIRED_STAGES)
        total_stages = max(len(stages), 1)

        for index, stage in enumerate(
            stages,
            start=1,
        ):
            result = await self._run_stage(
                stage=stage,
                context=context,
            )

            context.set_stage_result(result)

            if not result.success:
                context.add_error(
                    result.error
                    or f"{stage.value} stage failed."
                )

                if self.STOP_ON_FAILURE:
                    break

            progress = int(
                index
                / total_stages
                * 100
            )

            await self._update_progress(
                task_id=context.run_id,
                progress=progress,
                message=(
                    f"Executive stage completed: "
                    f"{stage.value}"
                ),
            )

        self._finalize_context(context)

        return context

    async def _run_stage(
        self,
        stage: ExecutiveStage,
        context: ExecutiveContext,
    ) -> ExecutiveStageResult:
        started_at = datetime.now(
            timezone.utc
        )

        try:
            output = await self._dispatch_stage(
                stage=stage,
                context=context,
            )

            self._store_stage_output(
                stage=stage,
                context=context,
                output=output,
            )

            return ExecutiveStageResult(
                stage=stage,
                success=True,
                output=output,
                started_at=started_at,
                completed_at=datetime.now(
                    timezone.utc
                ),
            )

        except Exception as exc:
            return ExecutiveStageResult(
                stage=stage,
                success=False,
                error=str(exc),
                started_at=started_at,
                completed_at=datetime.now(
                    timezone.utc
                ),
                metadata={
                    "exception_type": (
                        type(exc).__name__
                    ),
                },
            )

    async def _dispatch_stage(
        self,
        stage: ExecutiveStage,
        context: ExecutiveContext,
    ) -> Any:
        if stage == ExecutiveStage.ANALYZE:
            return await self.analyze(context)

        if stage == ExecutiveStage.THINK:
            return await self.think(context)

        if stage == ExecutiveStage.RECOMMEND:
            return await self.recommend(context)

        if stage == ExecutiveStage.PLAN:
            return await self.plan(context)

        if stage == ExecutiveStage.PREDICT:
            return await self.predict(context)

        if stage == ExecutiveStage.LEARN:
            return await self.learn(context)

        raise ValueError(
            f"Unsupported executive stage: {stage}"
        )

    @staticmethod
    def _store_stage_output(
        stage: ExecutiveStage,
        context: ExecutiveContext,
        output: Any,
    ) -> None:
        if stage == ExecutiveStage.ANALYZE:
            context.analysis = output

        elif stage == ExecutiveStage.THINK:
            context.thinking = output

        elif stage == ExecutiveStage.RECOMMEND:
            context.recommendations = output

        elif stage == ExecutiveStage.PLAN:
            context.plan = output

        elif stage == ExecutiveStage.PREDICT:
            context.prediction = output

        elif stage == ExecutiveStage.LEARN:
            context.learning = output

    @staticmethod
    def _finalize_context(
        context: ExecutiveContext,
    ) -> None:
        successful = sum(
            1
            for result in context.stage_results.values()
            if result.success
        )

        failed = sum(
            1
            for result in context.stage_results.values()
            if not result.success
        )

        if failed == 0:
            context.status = (
                ExecutiveRunStatus.COMPLETED
            )

        elif successful > 0:
            context.status = (
                ExecutiveRunStatus.PARTIAL
            )

        else:
            context.status = (
                ExecutiveRunStatus.FAILED
            )

        context.completed_at = datetime.now(
            timezone.utc
        )

    async def _update_progress(
        self,
        task_id: str,
        progress: int,
        message: str,
    ) -> None:
        """
        Update progress when supported by BaseAgent.

        This compatibility wrapper prevents the executive framework
        from breaking if the underlying task service is unavailable.
        """

        update_method = getattr(
            self,
            "update_task_progress",
            None,
        )

        if update_method is None:
            return

        try:
            await update_method(
                task_id=task_id,
                progress=progress,
                message=message,
            )
        except TypeError:
            try:
                await update_method(
                    task_id,
                    progress,
                    message,
                )
            except Exception:
                return
        except Exception:
            return

    @abstractmethod
    async def analyze(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """Understand the business and current situation."""

    async def think(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Interpret the analysis.

        Executives may override this method with specialized
        reasoning. The default implementation forwards analysis.
        """

        return context.analysis

    @abstractmethod
    async def recommend(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """Produce executive-level recommendations."""

    @abstractmethod
    async def plan(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """Convert recommendations into an actionable plan."""

    async def predict(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Estimate expected outcomes.

        Optional for executives that do not yet support forecasting.
        """

        return {
            "available": False,
            "reason": (
                "Prediction has not been implemented "
                "for this executive."
            ),
        }

    async def learn(
        self,
        context: ExecutiveContext,
    ) -> Any:
        """
        Store insights or outcomes for future decisions.

        Individual executives should override this method when
        connected to Business Memory.
        """

        return {
            "stored": False,
            "reason": (
                "Learning has not been implemented "
                "for this executive."
            ),
        }