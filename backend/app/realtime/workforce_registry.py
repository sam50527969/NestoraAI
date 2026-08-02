from __future__ import annotations

from datetime import datetime


class WorkforceRegistry:
    """
    Holds the live state of every AI executive.
    This will later be backed by Redis or a database,
    but an in-memory registry is perfect for development.
    """

    def __init__(self) -> None:
        self.executives = {
            "ceo": {
                "name": "CEO AI",
                "department": "Executive",
                "status": "idle",
                "current_task": None,
                "progress": 0,
                "missions_today": 0,
                "success_rate": 100,
                "last_updated": None,
            },
            "sales": {
                "name": "Sales Director",
                "department": "Sales",
                "status": "idle",
                "current_task": None,
                "progress": 0,
                "missions_today": 0,
                "success_rate": 100,
                "last_updated": None,
            },
            "marketing": {
                "name": "Marketing Director",
                "department": "Marketing",
                "status": "idle",
                "current_task": None,
                "progress": 0,
                "missions_today": 0,
                "success_rate": 100,
                "last_updated": None,
            },
            "finance": {
                "name": "Finance Director",
                "department": "Finance",
                "status": "idle",
                "current_task": None,
                "progress": 0,
                "missions_today": 0,
                "success_rate": 100,
                "last_updated": None,
            },
            "reception": {
                "name": "Reception AI",
                "department": "Operations",
                "status": "idle",
                "current_task": None,
                "progress": 0,
                "missions_today": 0,
                "success_rate": 100,
                "last_updated": None,
            },
        }

    def get_all(self):
        return list(self.executives.values())

    def update(
        self,
        executive: str,
        *,
        status: str | None = None,
        task: str | None = None,
        progress: int | None = None,
    ) -> None:

        if executive not in self.executives:
            return

        data = self.executives[executive]

        if status is not None:
            data["status"] = status

        if task is not None:
            data["current_task"] = task

        if progress is not None:
            data["progress"] = progress

        data["last_updated"] = datetime.utcnow().isoformat()


workforce_registry = WorkforceRegistry()