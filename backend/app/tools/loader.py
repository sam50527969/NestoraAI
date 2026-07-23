from app.core.tools import tool_registry
from app.tools.crm import crm_tool


def load_tools() -> None:
    """
    Register all built-in Nestora tools.
    """
    tool_registry.register(crm_tool)