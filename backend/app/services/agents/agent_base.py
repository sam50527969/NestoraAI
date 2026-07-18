from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from sqlalchemy.orm import Session

from app.services.mission_activity import log_mission_activity
from app.services.mission_state import (
    MISSIONS,
    update_agent,
    update_mission,
)
from app.services.mission_task_runtime import (
    complete_mission_task,
    fail_mission_task,
    start_mission_task,
    update_mission_task_progress,
)


class BaseAgent(ABC):
    """
    Base class for every Nestora AI agent.

    All agents use the same lifecycle:

        prepare()
        run()
        complete()
        rollback()

    Agents may also declare capabilities so that the CEO Agent,
    Mission Planner, and future orchestrator can discover which
    AI employee is suitable for a requested task.
    """

    AGENT_NAME: ClassVar[str] = "Unnamed Agent"
    AGENT_DESCRIPTION: ClassVar[str] = (
        "A Nestora AI workforce agent."
    )

    TASK_NAME: ClassVar[str | None] = None

    CAPABILITIES: ClassVar[tuple[str, ...]] = ()

    VERSION: ClassVar[str] = "1.0"
    ENABLED: ClassVar[bool] = True

    def __init__(
        self,
        db: Session,
        mission_id: str,
        request: Any,
    ):
        self.db = db
        self.mission_id = mission_id
        self.request = request

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    async def prepare(self):
        """
        Optional setup before agent execution.

        Agents may override this to validate inputs, initialize
        resources, start task records, or prepare internal state.
        """
        return None

    @abstractmethod
    async def run(self, *args, **kwargs):
        """
        Execute the agent's primary responsibility.
        """
        raise NotImplementedError

    async def complete(self):
        """
        Optional completion hook.

        Agents may override this to finalize task records,
        publish results, or update shared mission state.
        """
        return None

    async def rollback(self):
        """
        Optional compensation hook.

        Future agents may override this to undo or compensate
        for partial work after a failure.
        """
        return None

    # -------------------------------------------------
    # Capability system
    # -------------------------------------------------

    @classmethod
    def normalize_capability(cls, capability: str) -> str:
        """
        Convert capability names into a consistent internal format.

        Examples:

            "Campaign Strategy" -> "campaign_strategy"
            "campaign-strategy" -> "campaign_strategy"
        """

        return (
            str(capability)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

    @classmethod
    def get_capabilities(cls) -> tuple[str, ...]:
        """
        Return normalized, duplicate-free capabilities.
        """

        normalized: list[str] = []

        for capability in cls.CAPABILITIES:
            value = cls.normalize_capability(capability)

            if value and value not in normalized:
                normalized.append(value)

        return tuple(normalized)

    @classmethod
    def supports(cls, capability: str) -> bool:
        """
        Return True when the agent supports the requested capability.
        """

        normalized = cls.normalize_capability(capability)

        return normalized in cls.get_capabilities()

    @classmethod
    def supports_any(
        cls,
        capabilities: list[str] | tuple[str, ...] | set[str],
    ) -> bool:
        """
        Return True when the agent supports at least one capability.
        """

        return any(
            cls.supports(capability)
            for capability in capabilities
        )

    @classmethod
    def supports_all(
        cls,
        capabilities: list[str] | tuple[str, ...] | set[str],
    ) -> bool:
        """
        Return True when the agent supports every capability.
        """

        return all(
            cls.supports(capability)
            for capability in capabilities
        )

    @classmethod
    def metadata(cls) -> dict[str, Any]:
        """
        Return discoverable information about this agent.

        The future Agent Registry, CEO Agent, and Mission Planner
        can use this metadata without instantiating the agent.
        """

        return {
            "name": cls.AGENT_NAME,
            "description": cls.AGENT_DESCRIPTION,
            "task_name": cls.TASK_NAME,
            "capabilities": list(cls.get_capabilities()),
            "version": cls.VERSION,
            "enabled": cls.ENABLED,
        }

    # -------------------------------------------------
    # Mission helpers
    # -------------------------------------------------

    def log(self, message: str) -> None:
        mission = MISSIONS.get(self.mission_id)

        if mission is None:
            return

        log_mission_activity(
            mission,
            self.AGENT_NAME,
            message,
        )

    def update_status(
        self,
        *,
        status: str | None = None,
        progress: int | None = None,
        current_task: str | None = None,
    ) -> None:
        update_agent(
            self.mission_id,
            self.AGENT_NAME,
            status=status,
            progress=progress,
            current_task=current_task,
        )

    def update_mission(self, **kwargs) -> None:
        update_mission(
            self.mission_id,
            **kwargs,
        )

    # -------------------------------------------------
    # Persistent task helpers
    # -------------------------------------------------

    def task_start(self) -> None:
        if not self.TASK_NAME:
            return

        start_mission_task(
            self.db,
            self.mission_id,
            self.TASK_NAME,
        )

    def task_progress(self, progress: int) -> None:
        if not self.TASK_NAME:
            return

        safe_progress = min(
            max(int(progress), 0),
            100,
        )

        update_mission_task_progress(
            self.db,
            self.mission_id,
            self.TASK_NAME,
            safe_progress,
        )

    def task_complete(
        self,
        output: dict[str, Any] | None = None,
    ) -> None:
        if not self.TASK_NAME:
            return

        complete_mission_task(
            self.db,
            self.mission_id,
            self.TASK_NAME,
            output_data=output or {},
        )

    def task_failed(self, reason: str) -> None:
        if not self.TASK_NAME:
            return

        fail_mission_task(
            self.db,
            self.mission_id,
            self.TASK_NAME,
            error_message=str(reason),
        )