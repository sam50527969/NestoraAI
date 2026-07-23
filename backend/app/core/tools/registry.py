from __future__ import annotations

from app.core.tools.base import ToolBase
from app.core.tools.exceptions import (
    ToolNotFoundError,
)


class ToolRegistry:
    """
    Registry of all available tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolBase] = {}

    def register(
        self,
        tool: ToolBase,
    ) -> None:
        tool_id = tool.tool_id.strip().lower()

        if not tool_id:
            raise ValueError(
                "Tool must define a tool_id."
            )

        self._tools[tool_id] = tool

    def register_many(
        self,
        tools: list[ToolBase],
    ) -> None:
        for tool in tools:
            self.register(tool)

    def get(
        self,
        tool_id: str,
    ) -> ToolBase:
        normalized = tool_id.strip().lower()

        tool = self._tools.get(normalized)

        if tool is None:
            raise ToolNotFoundError(
                f"Tool '{normalized}' not found."
            )

        return tool

    def list_tools(
        self,
    ) -> list[str]:
        return sorted(
            self._tools.keys()
        )

    def count(
        self,
    ) -> int:
        return len(self._tools)

    def clear(
        self,
    ) -> None:
        self._tools.clear()


tool_registry = ToolRegistry()