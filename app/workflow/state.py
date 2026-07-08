from typing import Any, TypedDict


class TicketWorkflowState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # User input
    user_input: str

    # Intent analysis
    wants_ticket: bool

    # RAG result
    rag_result: dict[str, Any]
    answerable: bool

    # Ticket creation
    ticket_id: int | None
    ticket: dict[str, Any] | None

    # Human review
    requires_human_review: bool
    human_approved: bool | None
    reviewer_comment: str | None

    # Final response
    final_message: str