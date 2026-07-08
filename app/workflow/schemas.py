from typing import Any

from pydantic import BaseModel, Field


class WorkflowRunRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User message for the LangGraph workflow.",
        examples=["公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。"],
    )


class WorkflowRunResponse(BaseModel):
    final_message: str
    answerable: bool | None = None
    requires_human_review: bool = False
    wants_ticket: bool | None = None
    rag_result: dict[str, Any] | None = None
    ticket_id: int | None = None
    ticket: dict[str, Any] | None = None


class WorkflowReviewRequest(BaseModel):
    ticket_id: int = Field(
        ...,
        description="Ticket id waiting for human review.",
        examples=[1],
    )
    approved: bool = Field(
        ...,
        description="Whether the human reviewer approves the ticket submission.",
    )
    reviewer_comment: str | None = Field(
        default=None,
        description="Optional human review comment.",
    )


class WorkflowReviewResponse(BaseModel):
    updated: bool
    final_message: str
    ticket: dict[str, Any] | None = None