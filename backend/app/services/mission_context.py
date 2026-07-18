from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MissionStatistics:
    searched: int = 0
    qualified: int = 0
    saved: int = 0
    analyzed: int = 0
    websites: int = 0
    outreach: int = 0
    duplicates: int = 0
    rejected: int = 0
    errors: int = 0


@dataclass
class MissionContext:
    """
    Shared state object used by every AI agent.

    The Mission Executor creates one MissionContext and passes it
    through the complete AI pipeline.

    Every agent reads from and writes to this object instead of
    exchanging dozens of parameters.
    """

    mission_id: str

    request: dict[str, Any]

    created_at: datetime = field(default_factory=datetime.utcnow)

    raw_results: list[dict] = field(default_factory=list)

    qualified_leads: list[dict] = field(default_factory=list)

    saved_leads: list[dict] = field(default_factory=list)

    analyzed_leads: list[dict] = field(default_factory=list)

    website_results: list[dict] = field(default_factory=list)

    outreach_results: list[dict] = field(default_factory=list)

    completed_agents: list[str] = field(default_factory=list)

    failed_agents: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    statistics: MissionStatistics = field(
        default_factory=MissionStatistics
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    def complete_agent(self, name: str):
        if name not in self.completed_agents:
            self.completed_agents.append(name)

    def fail_agent(self, name: str):
        if name not in self.failed_agents:
            self.failed_agents.append(name)

    def warning(self, message: str):
        self.warnings.append(message)

    def error(self, message: str):
        self.errors.append(message)
        self.statistics.errors += 1

    @property
    def success(self):
        return len(self.failed_agents) == 0

    def summary(self):
        return {
            "mission_id": self.mission_id,
            "created_at": self.created_at.isoformat(),
            "statistics": vars(self.statistics),
            "completed_agents": self.completed_agents,
            "failed_agents": self.failed_agents,
            "warnings": self.warnings,
            "errors": self.errors,
        }