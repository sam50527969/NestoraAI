from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AgentTaskCreate(BaseModel):
    mission_id: str
    agent_name: str
    task_type: str
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    sequence_number: int = 0
    depends_on_task_uid: Optional[str] = None


class AgentTaskUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None


class AgentTaskResponse(BaseModel):
    id: int
    task_uid: str
    mission_id: str
    agent_name: str
    task_type: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    progress: int
    sequence_number: int
    depends_on_task_uid: Optional[str]

    retry_count: int

    created_at: datetime
    updated_at: datetime

    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True