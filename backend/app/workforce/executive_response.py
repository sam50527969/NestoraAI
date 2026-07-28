from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ExecutiveResponse:
    """
    Standard response returned by every Nestora executive.

    Individual executives may produce different business outputs,
    but the top-level response structure remains consistent.
    """

    success: bool
    executive: str
    summary: str
    output: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    execution_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the response into a JSON-serializable dictionary.
        """

        return asdict(self)