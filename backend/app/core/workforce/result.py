from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkerResult:
    """
    Standard result returned by every worker.
    """

    success: bool = True

    summary: str = ""

    output: dict[str, Any] = field(
        default_factory=dict,
    )

    warnings: list[str] = field(
        default_factory=list,
    )

    execution_time_ms: int = 0