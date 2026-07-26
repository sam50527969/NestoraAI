from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ArtifactType(str, Enum):
    """
    Types of business deliverables that an executive can produce.
    """

    REPORT = "report"
    DOCUMENT = "document"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    CAMPAIGN = "campaign"
    APPOINTMENT_LIST = "appointment_list"
    CUSTOMER_LIST = "customer_list"
    DASHBOARD = "dashboard"
    PRESENTATION = "presentation"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"


@dataclass(slots=True)
class ExecutiveArtifact:
    """
    A structured deliverable produced by an executive.

    Examples
    --------
    • Marketing campaign
    • Financial report
    • SMS template
    • Appointment schedule
    • Contract
    """

    id: str

    artifact_type: ArtifactType

    title: str

    description: str = ""

    content: Any = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    @property
    def has_content(self) -> bool:
        return self.content is not None