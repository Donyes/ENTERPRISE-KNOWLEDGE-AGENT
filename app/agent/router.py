from fastapi import APIRouter

from app.agent.schemas import AgentChatRequest, AgentChatResponse
from app.agent.service import run_enterprise_agent

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(request: AgentChatRequest):
    result = run_enterprise_agent(
        user_input=request.message,
        include_debug=request.include_debug,
    )

    return AgentChatResponse(
        answer=result["answer"],
        messages=result.get("messages"),
    )