from __future__ import annotations

from enum import Enum


class MissionStatus(str, Enum):
    """
    Lifecycle states for a Nestora mission.
    """

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"