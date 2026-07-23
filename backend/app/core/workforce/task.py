from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkerTask:
    """
    A unit of work assigned to an AI worker.
    """

    worker: str

    title: str

    description: str = ""

    payload: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )