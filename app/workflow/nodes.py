from typing import Any, Literal

from app.rag.chains import ask_advanced_rag
from app.tickets.database import SessionLocal
from app.tickets.models import TicketStatus
from app.tickets.schemas import TicketResponse
from app.tickets.service import (
    create_ticket,
    infer_ticket_category,
    infer_ticket_priority,
    update_ticket_status,
)
from app.workflow.state import TicketWorkflowState


def _ticket_to_dict(ticket) -> dict[str, Any]:
    """
    Convert SQLAlchemy Ticket object to JSON-serializable dict.
    """
    return TicketResponse.model_validate(ticket).model_dump(mode="json")


def analyze_request_node(state: TicketWorkflowState) -> TicketWorkflowState:
    """
    Analyze whether the user wants to create or process a ticket.
    """
    user_input = state["user_input"]

    ticket_keywords = [
        "工单",
        "提交",
        "创建",
        "生成",
        "记录",
        "反馈",
        "处理",
        "帮我建",
        "帮我生成",
        "帮我提交",
    ]

    wants_ticket = any(keyword in user_input for keyword in ticket_keywords)

    return {
        "wants_ticket": wants_ticket,
    }


def run_rag_node(state: TicketWorkflowState) -> TicketWorkflowState:
    """
    Run advanced RAG to check whether the knowledge base can answer the user input.
    """
    user_input = state["user_input"]

    rag_result = ask_advanced_rag(
        question=user_input,
        fetch_k=8,
        final_k=4,
        min_score=None,
        use_query_rewrite=True,
    )

    return {
        "rag_result": rag_result,
        "answerable": bool(rag_result.get("answerable", False)),
    }


def route_after_rag(state: TicketWorkflowState) -> Literal["answer", "ticket"]:
    """
    Decide whether to answer directly or create a ticket draft.
    """
    answerable = state.get("answerable", False)
    wants_ticket = state.get("wants_ticket", False)

    if answerable:
        return "answer"

    if wants_ticket:
        return "ticket"

    return "answer"


def generate_final_answer_node(state: TicketWorkflowState) -> TicketWorkflowState:
    """
    Generate the final response when no ticket creation is needed.
    """
    rag_result = state.get("rag_result", {})
    answerable = state.get("answerable", False)

    if answerable:
        final_message = rag_result.get("answer", "")
    else:
        final_message = (
            "根据当前知识库资料，我无法确定。"
            "如果你希望继续处理这个问题，可以让我生成一个工单草稿。"
        )

    return {
        "final_message": final_message,
        "requires_human_review": False,
    }


def create_ticket_draft_node(state: TicketWorkflowState) -> TicketWorkflowState:
    """
    Create a pending-review ticket when the knowledge base cannot answer
    and the user wants to create a ticket.
    """
    user_input = state["user_input"]
    rag_result = state.get("rag_result", {})

    category = infer_ticket_category(user_input)
    priority = infer_ticket_priority(user_input)
    evidence = rag_result.get("sources", [])

    summary = f"知识库暂无法回答，需人工处理：{user_input}"

    db = SessionLocal()

    try:
        ticket = create_ticket(
            db=db,
            user_question=user_input,
            category=category,
            priority=priority,
            summary=summary,
            evidence=evidence,
            status=TicketStatus.PENDING_REVIEW,
        )

        ticket_dict = _ticket_to_dict(ticket)

        return {
            "ticket_id": ticket.id,
            "ticket": ticket_dict,
            "requires_human_review": True,
        }
    finally:
        db.close()


def wait_for_human_review_node(state: TicketWorkflowState) -> TicketWorkflowState:
    """
    Stop the workflow at the human review point.
    """
    ticket_id = state.get("ticket_id")
    ticket = state.get("ticket")

    final_message = (
        f"知识库资料不足，已生成工单草稿，当前状态为 pending_review。"
        f"请人工审核后决定是否提交。工单 ID：{ticket_id}。"
    )

    return {
        "final_message": final_message,
        "ticket": ticket,
        "requires_human_review": True,
    }


def apply_review_decision(
    ticket_id: int,
    approved: bool,
    reviewer_comment: str | None = None,
) -> dict[str, Any]:
    """
    Apply human review decision to a pending ticket.
    """
    target_status = TicketStatus.SUBMITTED if approved else TicketStatus.REJECTED

    db = SessionLocal()

    try:
        ticket = update_ticket_status(
            db=db,
            ticket_id=ticket_id,
            status=target_status,
        )

        if ticket is None:
            return {
                "updated": False,
                "ticket": None,
                "final_message": f"未找到 ID 为 {ticket_id} 的工单。",
            }

        ticket_dict = _ticket_to_dict(ticket)

        if approved:
            final_message = f"人工审核已通过，工单 {ticket_id} 已提交。"
        else:
            final_message = f"人工审核未通过，工单 {ticket_id} 已拒绝。"

        if reviewer_comment:
            final_message += f" 审核备注：{reviewer_comment}"

        return {
            "updated": True,
            "ticket": ticket_dict,
            "final_message": final_message,
        }
    finally:
        db.close()