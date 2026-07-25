from __future__ import annotations

from app.core.missions.models import Mission


class MissionRegistry:
    """
    In-memory registry for active and completed missions.

    Persistence can be added later without changing the
    Mission Engine interface.
    """

    def __init__(self) -> None:
        self._missions: dict[str, Mission] = {}

    def add(self, mission: Mission) -> Mission:
        self._missions[mission.id] = mission
        return mission

    def get(self, mission_id: str) -> Mission | None:
        return self._missions.get(mission_id)

    def list_all(self) -> list[Mission]:
        return list(self._missions.values())

    def remove(self, mission_id: str) -> Mission | None:
        return self._missions.pop(mission_id, None)

    def clear(self) -> None:
        self._missions.clear()

    def count(self) -> int:
        return len(self._missions)


mission_registry = MissionRegistry()