from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.missions.models import Mission, MissionResult
from app.core.missions.registry import MissionRegistry, mission_registry
from app.core.missions.status import MissionStatus


class MissionEngineError(Exception):
    """Base exception raised by the Mission Engine."""


class MissionNotFoundError(MissionEngineError):
    """Raised when a requested mission does not exist."""


class InvalidMissionTransitionError(MissionEngineError):
    """Raised when an invalid mission-status transition is attempted."""


class MissionEngine:
    """
    Coordinates mission creation, assignment, tracking,
    lifecycle transitions, and result storage.

    Missions are currently stored in memory through MissionRegistry.
    Persistent database storage can be introduced later without
    changing the public Mission Engine interface.
    """

    _allowed_transitions: dict[MissionStatus, set[MissionStatus]] = {
        MissionStatus.PENDING: {
            MissionStatus.ASSIGNED,
            MissionStatus.CANCELLED,
        },
        MissionStatus.ASSIGNED: {
            MissionStatus.RUNNING,
            MissionStatus.CANCELLED,
        },
        MissionStatus.RUNNING: {
            MissionStatus.COMPLETED,
            MissionStatus.FAILED,
            MissionStatus.CANCELLED,
        },
        MissionStatus.COMPLETED: set(),
        MissionStatus.FAILED: set(),
        MissionStatus.CANCELLED: set(),
    }

    def __init__(
        self,
        registry: MissionRegistry | None = None,
    ) -> None:
        self._registry = registry or mission_registry
        self._results: dict[str, MissionResult] = {}

    def create_mission(
        self,
        *,
        title: str,
        objective: str,
        created_by: str = "CEO",
        assigned_to: list[str] | None = None,
        priority: str = "Medium",
        metadata: dict[str, Any] | None = None,
    ) -> Mission:
        """
        Create and register a mission.

        Missions with one or more assignees begin as ASSIGNED.
        Missions without assignees begin as PENDING.
        """
        clean_title = title.strip()
        clean_objective = objective.strip()
        clean_created_by = created_by.strip()

        if not clean_title:
            raise ValueError("Mission title cannot be empty.")

        if not clean_objective:
            raise ValueError("Mission objective cannot be empty.")

        if not clean_created_by:
            raise ValueError("Mission creator cannot be empty.")

        clean_assignees = self._normalize_assignees(assigned_to or [])

        initial_status = (
            MissionStatus.ASSIGNED
            if clean_assignees
            else MissionStatus.PENDING
        )

        mission = Mission(
            title=clean_title,
            objective=clean_objective,
            created_by=clean_created_by,
            assigned_to=clean_assignees,
            status=initial_status,
            priority=priority.strip() or "Medium",
            metadata=metadata or {},
        )

        return self._registry.add(mission)

    def get_mission(self, mission_id: str) -> Mission:
        """Return a mission or raise MissionNotFoundError."""
        mission = self._registry.get(mission_id)

        if mission is None:
            raise MissionNotFoundError(
                f"Mission '{mission_id}' was not found."
            )

        return mission

    def list_missions(
        self,
        status: MissionStatus | None = None,
    ) -> list[Mission]:
        """Return all missions, optionally filtered by status."""
        missions = self._registry.list_all()

        if status is None:
            return missions

        return [
            mission
            for mission in missions
            if mission.status == status
        ]

    def assign_mission(
        self,
        mission_id: str,
        assigned_to: str | list[str],
    ) -> Mission:
        """
        Assign one or more executives or workers to a mission.

        Existing assignees are preserved and duplicate names are ignored.
        """
        mission = self.get_mission(mission_id)

        new_assignees = (
            [assigned_to]
            if isinstance(assigned_to, str)
            else assigned_to
        )

        clean_assignees = self._normalize_assignees(new_assignees)

        if not clean_assignees:
            raise ValueError(
                "At least one mission assignee is required."
            )

        if mission.status == MissionStatus.PENDING:
            self._transition(
                mission=mission,
                new_status=MissionStatus.ASSIGNED,
            )
        elif mission.status != MissionStatus.ASSIGNED:
            raise InvalidMissionTransitionError(
                f"Mission '{mission.id}' cannot be assigned while its "
                f"status is '{mission.status.value}'."
            )

        existing_assignees = set(mission.assigned_to)

        for assignee in clean_assignees:
            if assignee not in existing_assignees:
                mission.assigned_to.append(assignee)
                existing_assignees.add(assignee)

        mission.updated_at = self._utc_now()

        return mission

    def unassign_mission(
        self,
        mission_id: str,
        assigned_to: str,
    ) -> Mission:
        """
        Remove an assignee from a mission.

        If no assignees remain, the mission returns to PENDING.
        This is allowed only before execution begins.
        """
        mission = self.get_mission(mission_id)
        clean_assignee = assigned_to.strip()

        if not clean_assignee:
            raise ValueError("Mission assignee cannot be empty.")

        if mission.status not in {
            MissionStatus.PENDING,
            MissionStatus.ASSIGNED,
        }:
            raise InvalidMissionTransitionError(
                f"Mission '{mission.id}' cannot be unassigned while its "
                f"status is '{mission.status.value}'."
            )

        mission.assigned_to = [
            assignee
            for assignee in mission.assigned_to
            if assignee != clean_assignee
        ]

        if not mission.assigned_to:
            mission.status = MissionStatus.PENDING

        mission.updated_at = self._utc_now()

        return mission

    def start_mission(self, mission_id: str) -> Mission:
        """Move an assigned mission into the running state."""
        mission = self.get_mission(mission_id)

        if not mission.assigned_to:
            raise MissionEngineError(
                f"Mission '{mission.id}' cannot start without an assignee."
            )

        return self._transition(
            mission=mission,
            new_status=MissionStatus.RUNNING,
        )

    def complete_mission(
        self,
        mission_id: str,
        result: MissionResult,
    ) -> Mission:
        """Complete a running mission and store its validated result."""
        mission = self.get_mission(mission_id)

        if result.mission_id != mission.id:
            raise ValueError(
                "MissionResult mission_id does not match the mission."
            )

        self._transition(
            mission=mission,
            new_status=MissionStatus.COMPLETED,
        )

        self._results[mission.id] = result

        return mission

    def fail_mission(self, mission_id: str) -> Mission:
        """Mark a running mission as failed."""
        mission = self.get_mission(mission_id)

        return self._transition(
            mission=mission,
            new_status=MissionStatus.FAILED,
        )

    def cancel_mission(self, mission_id: str) -> Mission:
        """Cancel a mission that has not reached a terminal state."""
        mission = self.get_mission(mission_id)

        return self._transition(
            mission=mission,
            new_status=MissionStatus.CANCELLED,
        )

    def get_result(
        self,
        mission_id: str,
    ) -> MissionResult | None:
        """Return the stored result for a completed mission."""
        self.get_mission(mission_id)
        return self._results.get(mission_id)

    def clear(self) -> None:
        """Clear all missions and results, primarily for testing."""
        self._registry.clear()
        self._results.clear()

    def _transition(
        self,
        *,
        mission: Mission,
        new_status: MissionStatus,
    ) -> Mission:
        """Validate and apply a mission-status transition."""
        current_status = mission.status

        if new_status == current_status:
            return mission

        allowed_statuses = self._allowed_transitions.get(
            current_status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise InvalidMissionTransitionError(
                f"Mission '{mission.id}' cannot transition from "
                f"'{current_status.value}' to '{new_status.value}'."
            )

        mission.status = new_status
        mission.updated_at = self._utc_now()

        return mission

    @staticmethod
    def _normalize_assignees(
        assignees: list[str],
    ) -> list[str]:
        """Clean assignee names and remove duplicates."""
        normalized: list[str] = []
        seen: set[str] = set()

        for assignee in assignees:
            if not isinstance(assignee, str):
                raise ValueError(
                    "Every mission assignee must be a string."
                )

            clean_assignee = assignee.strip()

            if not clean_assignee:
                continue

            if clean_assignee not in seen:
                normalized.append(clean_assignee)
                seen.add(clean_assignee)

        return normalized

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.utcnow()


mission_engine = MissionEngine()