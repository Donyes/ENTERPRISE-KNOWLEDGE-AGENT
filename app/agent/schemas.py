from typing import Any

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User message to the enterprise agent.",
        examples=["公司有没有免费午餐？如果不知道，帮我生成一个工单草稿。"],
    )
    include_debug: bool = Field(
        default=False,
        description="Whether to include internal agent messages for debugging.",
    )


class AgentChatResponse(BaseModel):
    answer: str
    messages: list[dict[str, Any]] | None = None