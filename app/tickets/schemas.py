from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):
    user_question: str = Field(
        ...,
        min_length=1,
        description="Original user question or issue",
        examples=["我的差旅费报销被拒了，帮我提交一个工单。"],
    )
    category: str = Field(
        default="general",
        description="Ticket category: hr, finance, it, general",
    )
    priority: str = Field(
        default="medium",
        description="Ticket priority: low, medium, high, urgent",
    )
    summary: str = Field(
        ...,
        min_length=1,
        description="Short summary of the ticket",
    )
    evidence: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Knowledge-base sources related to this ticket",
    )


class TicketStatusUpdateRequest(BaseModel):
    status: str = Field(
        ...,
        description="New ticket status: draft, pending_review, submitted, resolved, rejected",
        examples=["submitted"],
    )


class TicketResponse(BaseModel):
    id: int
    user_question: str
    category: str
    priority: str
    summary: str
    evidence: list[dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class TicketListResponse(BaseModel):
    tickets: list[TicketResponse]
    total: int


class CreateTicketFromRAGRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question to be checked by advanced RAG before creating a ticket draft",
        examples=["公司有没有免费午餐？"],
    )

class CreateTicketFromRAGResponse(BaseModel):
    created: bool
    reason: str
    rag_result: dict[str, Any]
    ticket: TicketResponse | None = None