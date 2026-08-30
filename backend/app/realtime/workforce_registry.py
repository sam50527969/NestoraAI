from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


DEFAULT_EXECUTIVES = {
    "ceo": {"name": "CEO AI", "department": "Executive"},
    "sales": {"name": "Sales Director", "department": "Sales"},
    "marketing": {"name": "Marketing Director", "department": "Marketing"},
    "finance": {"name": "Finance Director", "department": "Finance"},
    "reception": {"name": "Reception AI", "department": "Operations"},
}


def _new_executives() -> dict[str, dict]:
    executives = deepcopy(DEFAULT_EXECUTIVES)

    for data in executives.values():
        data.update({
            "status": "idle",
            "current_task": None,
            "progress": 0,
            "missions_today": 0,
            "success_rate": 100,
            "last_updated": None,
        })

    return executives


class WorkforceRegistry:
    """Hold independent live executive state for each workspace."""

    def __init__(self) -> None:
        self._workspaces: dict[str, dict[str, dict]] = {}

    def _workspace(self, business_uid: str) -> dict[str, dict]:
        clean_uid = str(business_uid or "").strip()

        if not clean_uid:
            raise ValueError("Business UID is required.")

        return self._workspaces.setdefault(
            clean_uid,
            _new_executives(),
        )

    def has_executive(
        self,
        business_uid: str,
        executive: str,
    ) -> bool:
        return executive in self._workspace(business_uid)

    def get_all(self, business_uid: str) -> list[dict]:
        return list(
            deepcopy(self._workspace(business_uid)).values()
        )

    def get(
        self,
        business_uid: str,
        executive: str,
    ) -> dict | None:
        data = self._workspace(business_uid).get(executive)
        return deepcopy(data) if data else None

    def update(
        self,
        business_uid: str,
        executive: str,
        *,
        status: str | None = None,
        task: str | None = None,
        progress: int | None = None,
    ) -> dict | None:
        data = self._workspace(business_uid).get(executive)

        if data is None:
            return None

        if status is not None:
            data["status"] = status

        if task is not None:
            data["current_task"] = task

        if progress is not None:
            data["progress"] = progress

        data["last_updated"] = datetime.now(
            timezone.utc
        ).isoformat()

        return deepcopy(data)

    def clear(self) -> None:
        self._workspaces.clear()


workforce_registry = WorkforceRegistry()
