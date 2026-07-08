import json
from typing import Any

from langchain.tools import tool
from langchain_core.documents import Document
from pydantic import BaseModel, Field

from app.rag.chains import ask_advanced_rag
from app.rag.retriever import retrieve_documents
from app.tickets.database import SessionLocal
from app.tickets.schemas import TicketResponse
from app.tickets.service import (
    create_ticket as create_ticket_service,
    list_tickets as list_tickets_service,
    update_ticket_status as update_ticket_status_service,
)


def _document_to_dict(document: Document) -> dict[str, Any]:
    """
    Convert a LangChain Document into a JSON-serializable dict.
    """
    return {
        "content": document.page_content,
        "metadata": document.metadata,
    }


def _ticket_to_dict(ticket) -> dict[str, Any]:
    """
    Convert a SQLAlchemy Ticket object into a JSON-serializable dict.
    """
    return TicketResponse.model_validate(ticket).model_dump(mode="json")


class SearchKnowledgeBaseInput(BaseModel):
    query: str = Field(
        ...,
        description="The search query for the enterprise knowledge base.",
    )
    k: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve.",
    )


@tool(args_schema=SearchKnowledgeBaseInput)
def search_knowledge_base(query: str, k: int = 4) -> dict[str, Any]:
    """
    Search the enterprise knowledge base and return relevant document chunks.
    """
    documents = retrieve_documents(
        query=query,
        k=k,
    )

    return {
        "query": query,
        "retrieved_count": len(documents),
        "documents": [
            _document_to_dict(document)
            for document in documents
        ],
    }


class AnswerWithKnowledgeBaseInput(BaseModel):
    question: str = Field(
        ...,
        description="The user's question that should be answered with enterprise knowledge base.",
    )


@tool(args_schema=AnswerWithKnowledgeBaseInput)
def answer_with_knowledge_base(question: str) -> dict[str, Any]:
    """
    Answer a user question with the advanced RAG pipeline.
    """
    result = ask_advanced_rag(
        question=question,
        fetch_k=8,
        final_k=4,
        max_distance=None,
        use_query_rewrite=True,
    )

    return result


class CreateTicketDraftInput(BaseModel):
    user_question: str = Field(
        ...,
        description="The original user issue or question.",
    )
    summary: str = Field(
        ...,
        description="A short summary of the ticket.",
    )
    category: str = Field(
        default="general",
        description="Ticket category. Allowed values: hr, finance, it, general.",
    )
    priority: str = Field(
        default="medium",
        description="Ticket priority. Allowed values: low, medium, high, urgent.",
    )
    evidence_json: str = Field(
        default="[]",
        description="A JSON string list of evidence sources. Use [] if there is no evidence.",
    )


@tool(args_schema=CreateTicketDraftInput)
def create_ticket_draft(
    user_question: str,
    summary: str,
    category: str = "general",
    priority: str = "medium",
    evidence_json: str = "[]",
) -> dict[str, Any]:
    """
    Create a draft ticket in the ticket database.
    """
    try:
        evidence = json.loads(evidence_json)
        if not isinstance(evidence, list):
            evidence = []
    except json.JSONDecodeError:
        evidence = []

    db = SessionLocal()

    try:
        ticket = create_ticket_service(
            db=db,
            user_question=user_question,
            summary=summary,
            category=category,
            priority=priority,
            evidence=evidence,
            status="draft",
        )

        return {
            "created": True,
            "ticket": _ticket_to_dict(ticket),
        }
    finally:
        db.close()


class ListTicketsInput(BaseModel):
    status: str | None = Field(
        default=None,
        description="Optional ticket status filter: draft, pending_review, submitted, resolved, rejected.",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of tickets to return.",
    )


@tool(args_schema=ListTicketsInput)
def list_tickets(status: str | None = None, limit: int = 10) -> dict[str, Any]:
    """
    List tickets from the ticket database.
    """
    db = SessionLocal()

    try:
        tickets = list_tickets_service(
            db=db,
            status=status,
            limit=limit,
        )

        return {
            "total": len(tickets),
            "tickets": [
                _ticket_to_dict(ticket)
                for ticket in tickets
            ],
        }
    finally:
        db.close()


class UpdateTicketStatusInput(BaseModel):
    ticket_id: int = Field(
        ...,
        description="The ticket id to update.",
    )
    status: str = Field(
        ...,
        description="New ticket status: draft, pending_review, submitted, resolved, rejected.",
    )


@tool(args_schema=UpdateTicketStatusInput)
def update_ticket_status(ticket_id: int, status: str) -> dict[str, Any]:
    """
    Update the status of a ticket.
    """
    db = SessionLocal()

    try:
        ticket = update_ticket_status_service(
            db=db,
            ticket_id=ticket_id,
            status=status,
        )

        if ticket is None:
            return {
                "updated": False,
                "reason": f"Ticket {ticket_id} not found.",
            }

        return {
            "updated": True,
            "ticket": _ticket_to_dict(ticket),
        }
    finally:
        db.close()


ENTERPRISE_AGENT_TOOLS = [
    search_knowledge_base,
    answer_with_knowledge_base,
    create_ticket_draft,
    list_tickets,
    update_ticket_status,
]