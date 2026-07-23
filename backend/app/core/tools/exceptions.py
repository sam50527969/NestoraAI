class ToolError(Exception):
    """Base tool exception."""


class ToolNotFoundError(ToolError):
    """Raised when a tool is not registered."""