from pydantic import BaseModel


class ExecutiveLearningContext(BaseModel):
    executive: str
    memories: list[str]
    summary: str