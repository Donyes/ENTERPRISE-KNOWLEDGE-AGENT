from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.tickets.database import get_db
from app.tickets.schemas import (
    CreateTicketFromRAGRequest,
    CreateTicketFromRAGResponse,
    TicketCreateRequest,
    TicketListResponse,
    TicketResponse,
    TicketStatusUpdateRequest,
)
from app.tickets.service import (
    create_ticket,
    create_ticket_draft_from_rag,
    get_ticket_by_id,
    list_tickets,
    update_ticket_status,
)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("", response_model=TicketResponse)
def create_ticket_api(
    request: TicketCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = create_ticket(
            db=db,
            user_question=request.user_question,
            category=request.category,
            priority=request.priority,
            summary=request.summary,
            evidence=request.evidence,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ticket


@router.get("", response_model=TicketListResponse)
def list_tickets_api(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        tickets = list_tickets(
            db=db,
            status=status,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TicketListResponse(
        tickets=tickets,
        total=len(tickets),
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_api(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(
        db=db,
        ticket_id=ticket_id,
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status_api(
    ticket_id: int,
    request: TicketStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = update_ticket_status(
            db=db,
            ticket_id=ticket_id,
            status=request.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    return ticket


@router.post("/from-rag", response_model=CreateTicketFromRAGResponse)
def create_ticket_from_rag_api(
    request: CreateTicketFromRAGRequest,
    db: Session = Depends(get_db),
) -> CreateTicketFromRAGResponse:
    result = create_ticket_draft_from_rag(
        db=db,
        question=request.question,
    )

    ticket = result.get("ticket")

    ticket_response = None
    if ticket is not None:
        ticket_response = TicketResponse.model_validate(ticket)

    return CreateTicketFromRAGResponse(
        created=result["created"],
        reason=result["reason"],
        rag_result=result["rag_result"],
        ticket=ticket_response,
    )