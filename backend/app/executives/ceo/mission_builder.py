from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.missions.models import Mission
from app.core.scheduler.models import SchedulerTask
from app.core.scheduler.workflow import Workflow
from app.executives.ceo.models import ExecutiveAction, ExecutivePlan


@dataclass(slots=True)
class MissionBuildResult:
    """
    Result produced when a CEO executive plan is converted
    into an executable mission and workflow.
    """

    mission: Mission
    workflow: Workflow


class CEOMissionBuilder:
    """
    Converts a CEO ExecutivePlan into the core execution models.

    Responsibilities:
    - Create a business mission from the CEO objective.
    - Convert executive actions into scheduler tasks.
    - Create a workflow containing those tasks.

    Registration and execution remain the responsibility of the
    Mission Engine and Executive Scheduler.
    """

    PRIORITY_MAP: dict[str, int] = {
        "critical": 0,
        "high": 10,
        "medium": 20,
        "low": 30,
    }

    def build(self, plan: ExecutivePlan) -> MissionBuildResult:
        """
        Convert an executive plan into a mission and workflow.
        """
        objective = plan.objective.strip()

        if not objective:
            raise ValueError("Executive plan objective cannot be empty.")

        if not plan.actions:
            raise ValueError(
                "Executive plan must contain at least one action."
            )

        departments = self._collect_departments(plan.actions)

        mission = Mission(
            title=self._build_mission_title(objective),
            objective=objective,
            created_by="CEO",
            assigned_to=departments,
            priority=self._determine_mission_priority(plan.actions),
            metadata={
                "plan_summary": plan.summary,
                "action_count": len(plan.actions),
                "source": "ceo_brain",
                "plan_metadata": dict(plan.metadata),
            },
        )

        tasks = [
            self._action_to_task(
                mission_id=mission.id,
                action=action,
                position=index,
            )
            for index, action in enumerate(plan.actions)
        ]

        workflow = Workflow(
            mission_id=mission.id,
            name=f"{mission.title} Workflow",
            description=plan.summary,
            tasks=tasks,
            metadata={
                "created_by": "CEO",
                "objective": objective,
                "departments": departments,
            },
        )

        return MissionBuildResult(
            mission=mission,
            workflow=workflow,
        )

    def _action_to_task(
        self,
        mission_id: str,
        action: ExecutiveAction,
        position: int,
    ) -> SchedulerTask:
        department = self._normalize_department(action.department)

        priority_level = str(
            action.metadata.get("priority_level", "medium")
        ).lower()

        priority = self.PRIORITY_MAP.get(priority_level, 20)

        payload: dict[str, Any] = {
            "instruction": action.instruction,
            "requires_approval": action.requires_approval,
            "recommendation_score": action.recommendation_score,
            "assigned_worker_id": action.assigned_worker_id,
            "action_metadata": dict(action.metadata),
            "sequence": position,
        }

        return SchedulerTask(
            mission_id=mission_id,
            name=action.title.strip(),
            task_type="executive",
            executor=department,
            payload=payload,
            dependencies=[],
            priority=priority,
        )

    def _collect_departments(
        self,
        actions: list[ExecutiveAction],
    ) -> list[str]:
        departments: list[str] = []

        for action in actions:
            department = self._normalize_department(
                action.department
            )

            if department not in departments:
                departments.append(department)

        return departments

    def _determine_mission_priority(
        self,
        actions: list[ExecutiveAction],
    ) -> str:
        priority_rank = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        highest_priority = "medium"
        highest_rank = priority_rank[highest_priority]

        for action in actions:
            priority = str(
                action.metadata.get("priority_level", "medium")
            ).lower()

            rank = priority_rank.get(priority, 2)

            if rank > highest_rank:
                highest_priority = priority
                highest_rank = rank

        return highest_priority.capitalize()

    @staticmethod
    def _normalize_department(department: str) -> str:
        normalized = department.strip().lower()
        normalized = normalized.replace(" ", "_")
        normalized = normalized.replace("-", "_")

        if not normalized:
            raise ValueError(
                "Executive action department cannot be empty."
            )

        return normalized

    @staticmethod
    def _build_mission_title(objective: str) -> str:
        maximum_length = 80

        if len(objective) <= maximum_length:
            return objective

        return f"{objective[:maximum_length - 3].rstrip()}..."