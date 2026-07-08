from fastapi import APIRouter

from app.agents.orchestrator import AIAgent
from app.schemas.ai_agent import (
    AgentStartRequest,
    AgentResult,
)

router = APIRouter(prefix="/ai-agent", tags=["AI Agent"])


@router.post("/start", response_model=AgentResult)
async def start_agent(request: AgentStartRequest):

    agent = AIAgent()

    result = await agent.run(request)

    return result