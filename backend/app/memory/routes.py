from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.memory.schemas import (
    ExecutiveMemoryCreate,
    ExecutiveMemoryListResponse,
    ExecutiveMemoryResponse,
)
from app.memory.service import ExecutiveMemoryService


router = APIRouter(
    prefix="/memory",
    tags=["Executive Memory"],
)


@router.get("/health")
def memory_health() -> dict[str, str]:
    return {
        "status": "ok",
        "module": "Executive Memory",
    }


@router.post(
    "",
    response_model=ExecutiveMemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    payload: ExecutiveMemoryCreate,
    db: Session = Depends(get_db),
) -> ExecutiveMemoryResponse:
    service = ExecutiveMemoryService(db)

    return service.create_memory(payload)


@router.get(
    "",
    response_model=ExecutiveMemoryListResponse,
)
def list_memories(
    executive: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
) -> ExecutiveMemoryListResponse:
    service = ExecutiveMemoryService(db)

    memories = service.list_memories(
        executive=executive,
        limit=limit,
    )

    return ExecutiveMemoryListResponse(
        count=len(memories),
        memories=memories,
    )


@router.get(
    "/{memory_id}",
    response_model=ExecutiveMemoryResponse,
)
def get_memory(
    memory_id: int,
    db: Session = Depends(get_db),
) -> ExecutiveMemoryResponse:
    service = ExecutiveMemoryService(db)

    memory = service.get_memory(memory_id)

    if memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive memory not found.",
        )

    return memory


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_200_OK,
)
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = ExecutiveMemoryService(db)

    deleted = service.delete_memory(memory_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive memory not found.",
        )

    return {
        "message": "Executive memory deleted successfully.",
    }