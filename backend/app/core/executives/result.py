from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutiveResult:
    """
    Standard response from every executive.
    """

    success: bool = True

    summary: str = ""

    data: dict[str, Any] = field(
        default_factory=dict,
    )

    warnings: list[str] = field(
        default_factory=list,
    )

    recommendations: list[str] = field(
        default_factory=list,
    )

    metrics: dict[str, Any] = field(
        default_factory=dict,
    )