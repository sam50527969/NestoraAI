from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutiveContext:
    """
    Context passed to every executive.
    """

    mission: str

    objective: str | None = None

    business_name: str | None = None

    business_id: str | None = None

    user_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    memory: dict[str, Any] = field(
        default_factory=dict,
    )

    shared_data: dict[str, Any] = field(
        default_factory=dict,
    )