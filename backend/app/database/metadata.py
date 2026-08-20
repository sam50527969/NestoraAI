"""Canonical registry for all SQLAlchemy mapped models."""

from app.approvals import models as approval_models
from app.auth import models as auth_models
from app.clinic import models as clinic_models
from app.collaboration import models as collaboration_models
from app.communication import models as communication_models
from app.database import models as database_models
from app.database.database import Base
from app.follow_up_activity import models as follow_up_activity_models
from app.memory import models as memory_models
from app.outreach_activity import models as outreach_activity_models
from app.pipeline_activity import models as pipeline_activity_models


_MAPPED_MODEL_MODULES = (
    approval_models,
    auth_models,
    clinic_models,
    collaboration_models,
    communication_models,
    database_models,
    follow_up_activity_models,
    memory_models,
    outreach_activity_models,
    pipeline_activity_models,
)

metadata = Base.metadata

__all__ = ["metadata"]
