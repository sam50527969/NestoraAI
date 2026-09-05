from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExecutiveMemoryCreate(BaseModel):
    executive: str = Field(
        min_length=1,
        max_length=100,
    )

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    memory: str = Field(
        min_length=1,
    )

    importance: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    source: str = Field(
        default="mission",
        min_length=1,
        max_length=100,
    )


class ExecutiveMemoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    business_uid: str | None = None
    executive: str
    category: str
    memory: str
    importance: int
    source: str
    created_at: datetime
    updated_at: datetime | None = None


class ExecutiveMemoryListResponse(BaseModel):
    count: int
    memories: list[ExecutiveMemoryResponse]