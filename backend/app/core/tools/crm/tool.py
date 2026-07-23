from __future__ import annotations

from app.core.tools import ToolBase


class CRMTool(ToolBase):
    """
    CRM Tool
    Wraps CRM functionality so workers can interact
    with the CRM through a common interface.
    """

    tool_id = "crm"

    name = "CRM Tool"

    description = "Lead and customer management."

    async def save_lead(
        self,
        **kwargs,
    ):
        """
        Placeholder implementation.

        In the next package this will call the
        existing CRM repository/service layer.
        """
        return {
            "success": True,
            "message": "CRM Tool placeholder",
            "data": kwargs,
        }