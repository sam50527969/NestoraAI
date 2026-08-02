from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_event(
    event: str,
    data: Any,
) -> dict[str, Any]:
    """
    Build a standardized realtime event payload.
    """

    return {
        "event": event,
        "version": 1,
        "timestamp": (
            datetime.now(UTC)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "data": data,
    }