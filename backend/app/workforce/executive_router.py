from __future__ import annotations

from time import perf_counter
from typing import Any, Protocol

from app.workforce.executive_response import ExecutiveResponse
from app.workforce.runtime import (
    AnalyticsExecutive,
    CustomerSuccessExecutive,
    FinanceExecutive,
    FollowUpExecutive,
    MarketingExecutive,
    OperationsExecutive,
    QualityControlExecutive,
    ReceptionExecutive,
    SalesExecutive,
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
    Select and execute the correct executive for a persisted task.

    The router also:
    - injects experience-based reasoning guidance,
    - preserves the original task input,
    - normalizes every executive result into Nestora's standard
      ExecutiveResponse structure.
    """

    def __init__(self) -> None:
        analytics = AnalyticsExecutive()
        customer_success = CustomerSuccessExecutive()
        marketing = MarketingExecutive()
        follow_up = FollowUpExecutive()
        reception = ReceptionExecutive()
        sales = SalesExecutive()
        finance = FinanceExecutive()
        operations = OperationsExecutive()
        quality_control = QualityControlExecutive()

        self._executives: dict[str, ExecutiveProtocol] = {
            "analytics": analytics,
            "analytics executive": analytics,
            "analytics-executive": analytics,
            "customer success": customer_success,
            "customer-success": customer_success,
            "customersuccess": customer_success,
            "marketing": marketing,
            "follow-up": follow_up,
            "followup": follow_up,
            "follow up": follow_up,
            "reception": reception,
            "sales": sales,
            "sales executive": sales,
            "sales-executive": sales,
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

        Relevant executive memories are converted into explicit
        reasoning guidance before the runtime executive is called.
        """

        executive = self.get_executive(agent_name)

        prepared_input = self._prepare_experience_input(
            agent_name=agent_name,
            title=title,
            description=description,
            input_data=input_data,
        )

        started_at = perf_counter()

        try:
            raw_output = executive.execute(
                title=title,
                description=description,
                input_data=prepared_input,
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

    def _prepare_experience_input(
        self,
        *,
        agent_name: str,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build final executive input without mutating the caller's data.
        """

        prepared_input = dict(input_data or {})

        learning_context = prepared_input.get(
            "learning_context"
        )

        memories = self._extract_learning_memories(
            learning_context
        )

        prepared_input["experience_reasoning"] = {
            "executive": agent_name,
            "task_title": title,
            "task_description": description or "",
            "memory_count": len(memories),
            "previous_experience": memories,
            "instructions": self._build_reasoning_instructions(
                agent_name=agent_name,
                memories=memories,
            ),
        }

        prepared_input["reasoning_prompt"] = (
            self._build_reasoning_prompt(
                agent_name=agent_name,
                title=title,
                description=description,
                memories=memories,
            )
        )

        return prepared_input

    @staticmethod
    def _extract_learning_memories(
        learning_context: Any,
    ) -> list[str]:
        if not isinstance(learning_context, dict):
            return []

        raw_memories = learning_context.get("memories")

        if not isinstance(raw_memories, list):
            return []

        memories: list[str] = []

        for memory in raw_memories:
            if memory is None:
                continue

            cleaned_memory = str(memory).strip()

            if cleaned_memory:
                memories.append(cleaned_memory)

        return memories

    @staticmethod
    def _build_reasoning_instructions(
        *,
        agent_name: str,
        memories: list[str],
    ) -> list[str]:
        instructions = [
            (
                f"Act as Nestora's {agent_name} executive and complete "
                "the assigned task using sound business judgment."
            ),
            (
                "Use relevant past experience when it improves the "
                "current recommendation or output."
            ),
            (
                "Do not copy previous outputs blindly. Adapt useful "
                "lessons to the current mission, business, and objective."
            ),
            (
                "Avoid repeating approaches that the available experience "
                "suggests were ineffective or low value."
            ),
            (
                "When memories conflict, prefer the most recent, specific, "
                "and business-relevant evidence."
            ),
        ]

        if memories:
            instructions.append(
                f"Review the {len(memories)} retrieved memory record(s) before finalizing the response."
            )
        else:
            instructions.append(
                "No previous executive memories were retrieved. Proceed using the current mission context."
            )

        return instructions

    @staticmethod
    def _build_reasoning_prompt(
        *,
        agent_name: str,
        title: str,
        description: str | None,
        memories: list[str],
    ) -> str:
        memory_section = (
            "\n".join(
                f"{index}. {memory}"
                for index, memory in enumerate(
                    memories,
                    start=1,
                )
            )
            if memories
            else "No previous memories were retrieved."
        )

        task_description = (
            description.strip()
            if isinstance(description, str)
            and description.strip()
            else "No additional task description was provided."
        )

        return (
            f"You are Nestora's {agent_name} Executive.\n\n"
            f"Current task:\n{title}\n\n"
            f"Task description:\n{task_description}\n\n"
            "Relevant previous experience:\n"
            f"{memory_section}\n\n"
            "Reasoning requirements:\n"
            "- Consider the previous experience before deciding.\n"
            "- Reuse proven approaches only when relevant.\n"
            "- Adapt past lessons to the current business context.\n"
            "- Avoid repeating ineffective strategies.\n"
            "- Produce a clear, practical, and task-specific result."
        )

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