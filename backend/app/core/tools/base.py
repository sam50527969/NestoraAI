from __future__ import annotations

from abc import ABC


class ToolBase(ABC):
    """
    Base class for every Nestora tool.
    """

    tool_id: str = ""

    name: str = ""

    description: str = ""