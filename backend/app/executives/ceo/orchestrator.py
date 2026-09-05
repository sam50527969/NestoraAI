from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.approvals.schemas import ApprovalCreate
from app.approvals.service import create_approval
from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
)
from app.executives.ceo.serialization import (
    serialize_executive_plan,
)


@dataclass(slots=True)
class CEOOrchestrationResult:
    """
    Result of preparing a CEO executive plan for execution.

    Approval-required actions are converted into approval
    requests. Actions that do not require approval are
    reported separately so execution can be handled by the
    appropriate execution layer.
    """

    plan: ExecutivePlan

    approvals: list[dict[str, Any]] = field(
        default_factory=list
    )

    executable_actions: list[ExecutiveAction] = field(
        default_factory=list
    )

    @property
    def approval_count(self) -> int:
        return len(self.approvals)

    @property
    def executable_count(self) -> int:
        return len(self.executable_actions)

    @property
    def requires_approval(self) -> bool:
        return bool(self.approvals)


class CEOExecutionOrchestrator:
    """
    Coordinates a CEO ExecutivePlan with Nestora's approval
    system.

    Responsibilities:

    - Inspect CEO-generated executive actions.
    - Preserve the complete ExecutivePlan.
    - Create approval requests for actions requiring approval.
    - Keep non-approval actions separate for later execution.

    This service deliberately does not execute approved
    actions itself. Approved execution remains the
    responsibility of the approval executor and execution
    service.
    """

    def prepare_plan(
        self,
        plan: ExecutivePlan,
        *,
        business_uid: str,
        source_uid: str | None = None,
        requested_by: str = "CEO Agent",
    ) -> CEOOrchestrationResult:
        self._validate_plan(plan)

        approval_actions = [
            action
            for action in plan.actions
            if action.requires_approval
        ]

        executable_actions = [
            action
            for action in plan.actions
            if not action.requires_approval
        ]

        approvals = [
            self._create_action_approval(
                plan=plan,
                action=action,
                business_uid=business_uid,
                source_uid=source_uid,
                requested_by=requested_by,
            )
            for action in approval_actions
        ]

        return CEOOrchestrationResult(
            plan=plan,
            approvals=approvals,
            executable_actions=executable_actions,
        )

    def _create_action_approval(
        self,
        *,
        plan: ExecutivePlan,
        action: ExecutiveAction,
        business_uid: str,
        source_uid: str | None,
        requested_by: str,
    ) -> dict[str, Any]:
        payload = {
            "executive_plan": (
                self._build_action_plan_payload(
                    plan,
                    action,
                )
            ),
            "action": {
                "title": action.title,
                "department": action.department,
                "instruction": action.instruction,
                "recommendation_score": (
                    action.recommendation_score
                ),
                "requires_approval": (
                    action.requires_approval
                ),
                "assigned_worker_id": (
                    action.assigned_worker_id
                ),
                "metadata": dict(
                    action.metadata
                ),
            },
        }

        approval = ApprovalCreate(
            title=action.title,
            description=action.instruction,
            decision_type="executive_action",
            source_type="ceo_executive_plan",
            source_uid=source_uid,
            requested_by=requested_by,
            payload=payload,
        )

        return create_approval(
            approval,
            business_uid=business_uid,
        )

    @staticmethod
    def _build_action_plan_payload(
        plan: ExecutivePlan,
        action: ExecutiveAction,
    ) -> dict[str, Any]:
        """
        Build a single-action ExecutivePlan for approval.

        Each approval should execute only the action that was
        explicitly approved rather than every action contained
        in the original CEO plan.
        """

        action_plan = ExecutivePlan(
            objective=plan.objective,
            summary=plan.summary,
            actions=[
                action,
            ],
            recommendations=list(
                plan.recommendations
            ),
            metadata={
                **plan.metadata,
                "orchestration_scope": (
                    "single_action"
                ),
                "original_action_count": (
                    len(plan.actions)
                ),
            },
        )

        return serialize_executive_plan(
            action_plan
        )

    @staticmethod
    def _validate_plan(
        plan: ExecutivePlan,
    ) -> None:
        if not plan.objective.strip():
            raise ValueError(
                "Executive plan objective cannot be empty."
            )

        for action in plan.actions:
            if not action.title.strip():
                raise ValueError(
                    "Executive action title cannot be empty."
                )

            if not action.department.strip():
                raise ValueError(
                    "Executive action department cannot be empty."
                )

            if not action.instruction.strip():
                raise ValueError(
                    "Executive action instruction cannot be empty."
                )


ceo_execution_orchestrator = (
    CEOExecutionOrchestrator()
)