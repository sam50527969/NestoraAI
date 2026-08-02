from __future__ import annotations

from time import perf_counter
from typing import Any, Protocol

from app.workforce.executive_response import ExecutiveResponse
from app.workforce.runtime import (
    FinanceExecutive,
    FollowUpExecutive,
    MarketingExecutive,
    OperationsExecutive,
    QualityControlExecutive,
    ReceptionExecutive,
)


class ExecutiveProtocol(Protocol):
    name: str

    def execute(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        ...


class ExecutiveRouter:
    """
    Selects and executes the correct executive for a persisted task.

    The router also converts every executive result into Nestora's
    standard ExecutiveResponse structure.
    """

    def __init__(self) -> None:
        marketing = MarketingExecutive()
        follow_up = FollowUpExecutive()
        reception = ReceptionExecutive()
        finance = FinanceExecutive()
        operations = OperationsExecutive()
        quality_control = QualityControlExecutive()

        self._executives: dict[str, ExecutiveProtocol] = {
            "marketing": marketing,
            "follow-up": follow_up,
            "followup": follow_up,
            "follow up": follow_up,
            "reception": reception,
            "finance": finance,
            "operations": operations,
            "operation": operations,
            "quality control": quality_control,
            "quality-control": quality_control,
            "qualitycontrol": quality_control,
            "quality assurance": quality_control,
            "quality-assurance": quality_control,
            "qa": quality_control,
            "qc": quality_control,
        }

        self._fallback_executive = operations

    def get_executive(
        self,
        agent_name: str,
    ) -> ExecutiveProtocol:
        """
        Resolve an agent name to a registered executive.

        Unknown executives temporarily fall back to Operations.
        """

        normalized_name = self._normalize_agent_name(
            agent_name
        )

        return self._executives.get(
            normalized_name,
            self._fallback_executive,
        )

    def execute_task(
        self,
        *,
        agent_name: str,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a task and return a standardized response.
        """

        executive = self.get_executive(agent_name)

        started_at = perf_counter()

        try:
            raw_output = executive.execute(
                title=title,
                description=description,
                input_data=input_data,
            )

            execution_time_ms = round(
                (perf_counter() - started_at) * 1000
            )

            response = ExecutiveResponse(
                success=True,
                executive=self._get_executive_name(
                    executive=executive,
                    fallback_name=agent_name,
                ),
                summary=self._build_summary(
                    title=title,
                    raw_output=raw_output,
                ),
                output=self._normalize_output(raw_output),
                metrics=self._extract_metrics(raw_output),
                warnings=self._extract_warnings(raw_output),
                artifacts=self._extract_artifacts(raw_output),
                execution_time_ms=execution_time_ms,
            )

            return response.to_dict()

        except Exception as exc:
            execution_time_ms = round(
                (perf_counter() - started_at) * 1000
            )

            response = ExecutiveResponse(
                success=False,
                executive=self._get_executive_name(
                    executive=executive,
                    fallback_name=agent_name,
                ),
                summary=f"Executive failed to complete: {title}",
                output={},
                metrics={},
                warnings=[str(exc)],
                artifacts=[],
                execution_time_ms=execution_time_ms,
            )

            return response.to_dict()

    @staticmethod
    def _normalize_agent_name(
        agent_name: str,
    ) -> str:
        return " ".join(
            agent_name.strip().lower().split()
        )

    @staticmethod
    def _get_executive_name(
        *,
        executive: ExecutiveProtocol,
        fallback_name: str,
    ) -> str:
        executive_name = getattr(
            executive,
            "name",
            None,
        )

        if isinstance(executive_name, str):
            cleaned_name = executive_name.strip()

            if cleaned_name:
                return cleaned_name

        return fallback_name.strip() or "Unknown Executive"

    @staticmethod
    def _normalize_output(
        raw_output: Any,
    ) -> dict[str, Any]:
        """
        Convert legacy executive outputs into a dictionary.
        """

        if isinstance(raw_output, dict):
            if (
                "output" in raw_output
                and isinstance(raw_output["output"], dict)
            ):
                return raw_output["output"]

            return raw_output

        return {
            "result": raw_output,
        }

    @staticmethod
    def _build_summary(
        *,
        title: str,
        raw_output: Any,
    ) -> str:
        """
        Use an executive-provided summary when available.
        Otherwise create a safe default summary.
        """

        if isinstance(raw_output, dict):
            summary = raw_output.get("summary")

            if isinstance(summary, str) and summary.strip():
                return summary.strip()

            message = raw_output.get("message")

            if isinstance(message, str) and message.strip():
                return message.strip()

        return f"Successfully completed: {title}"

    @staticmethod
    def _extract_metrics(
        raw_output: Any,
    ) -> dict[str, Any]:
        if not isinstance(raw_output, dict):
            return {}

        metrics = raw_output.get("metrics")

        if isinstance(metrics, dict):
            return metrics

        return {}

    @staticmethod
    def _extract_warnings(
        raw_output: Any,
    ) -> list[str]:
        if not isinstance(raw_output, dict):
            return []

        warnings = raw_output.get("warnings")

        if not isinstance(warnings, list):
            return []

        return [
            str(warning)
            for warning in warnings
            if warning is not None
        ]

    @staticmethod
    def _extract_artifacts(
        raw_output: Any,
    ) -> list[dict[str, Any]]:
        if not isinstance(raw_output, dict):
            return []

        artifacts = raw_output.get("artifacts")

        if not isinstance(artifacts, list):
            return []

        return [
            artifact
            for artifact in artifacts
            if isinstance(artifact, dict)
        ]