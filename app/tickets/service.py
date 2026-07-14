from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rag.chains import ask_advanced_rag
from app.tickets.models import (
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


def validate_ticket_category(category: str) -> None:
    if category not in TicketCategory.ALL:
        raise ValueError(
            f"Invalid category: {category}. "
            f"Allowed values: {sorted(TicketCategory.ALL)}"
        )


def validate_ticket_priority(priority: str) -> None:
    if priority not in TicketPriority.ALL:
        raise ValueError(
            f"Invalid priority: {priority}. "
            f"Allowed values: {sorted(TicketPriority.ALL)}"
        )


def validate_ticket_status(status: str) -> None:
    if status not in TicketStatus.ALL:
        raise ValueError(
            f"Invalid status: {status}. "
            f"Allowed values: {sorted(TicketStatus.ALL)}"
        )


def create_ticket(
    db: Session,
    user_question: str,
    summary: str,
    category: str = TicketCategory.GENERAL,
    priority: str = TicketPriority.MEDIUM,
    evidence: list[dict[str, Any]] | None = None,
    status: str = TicketStatus.DRAFT,
) -> Ticket:
    """
    Create a new ticket.
    """
    validate_ticket_category(category)
    validate_ticket_priority(priority)
    validate_ticket_status(status)

    ticket = Ticket(
        user_question=user_question,
        category=category,
        priority=priority,
        summary=summary,
        evidence=evidence or [],
        status=status,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def list_tickets(
    db: Session,
    status: str | None = None,
    limit: int = 50,
) -> list[Ticket]:
    """
    List tickets, optionally filtered by status.
    """
    statement = select(Ticket).order_by(Ticket.created_at.desc())

    if status is not None:
        validate_ticket_status(status)
        statement = statement.where(Ticket.status == status)

    statement = statement.limit(limit)

    tickets = db.execute(statement).scalars().all()

    return list(tickets)


def get_ticket_by_id(
    db: Session,
    ticket_id: int,
) -> Ticket | None:
    """
    Get one ticket by id.
    """
    return db.get(Ticket, ticket_id)


def update_ticket_status(
    db: Session,
    ticket_id: int,
    status: str,
) -> Ticket | None:
    """
    Update ticket status.
    """
    validate_ticket_status(status)

    ticket = get_ticket_by_id(db, ticket_id)

    if ticket is None:
        return None

    ticket.status = status

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def infer_ticket_category(question: str) -> str:
    """
    A simple rule-based category classifier.

    This will be replaced by an LLM/tool-based classifier in later lessons.
    """
    question_lower = question.lower()

    finance_keywords = ["报销", "发票", "差旅", "费用", "付款", "财务"]
    it_keywords = ["vpn", "密码", "账号", "登录", "系统", "验证码", "网络"]
    hr_keywords = ["年假", "试用期", "入职", "离职", "工资", "福利", "请假"]

    if any(keyword in question_lower for keyword in finance_keywords):
        return TicketCategory.FINANCE

    if any(keyword in question_lower for keyword in it_keywords):
        return TicketCategory.IT

    if any(keyword in question_lower for keyword in hr_keywords):
        return TicketCategory.HR

    return TicketCategory.GENERAL


def infer_ticket_priority(question: str) -> str:
    """
    A simple rule-based priority classifier.
    """
    urgent_keywords = ["紧急", "马上", "立即", "严重", "无法工作", "宕机"]
    high_keywords = ["被拒", "无法登录", "影响", "错误", "失败"]

    if any(keyword in question for keyword in urgent_keywords):
        return TicketPriority.URGENT

    if any(keyword in question for keyword in high_keywords):
        return TicketPriority.HIGH

    return TicketPriority.MEDIUM


def create_ticket_draft_from_rag(
    db: Session,
    question: str,
) -> dict[str, Any]:
    """
    Run advanced RAG first.

    If the knowledge base cannot answer the question,
    create a ticket draft using the retrieved sources as evidence.
    """
    rag_result = ask_advanced_rag(
        question=question,
        fetch_k=8,
        final_k=4,
        min_score=None,
        use_query_rewrite=True,
    )

    if rag_result["answerable"]:
        return {
            "created": False,
            "reason": "知识库已有可回答依据，因此未自动创建工单草稿。",
            "rag_result": rag_result,
            "ticket": None,
        }

    category = infer_ticket_category(question)
    priority = infer_ticket_priority(question)

    summary = f"用户问题暂无法由知识库直接回答：{question}"

    ticket = create_ticket(
        db=db,
        user_question=question,
        category=category,
        priority=priority,
        summary=summary,
        evidence=rag_result["sources"],
        status=TicketStatus.DRAFT,
    )

    return {
        "created": True,
        "reason": "知识库资料不足，已生成工单草稿。",
        "rag_result": rag_result,
        "ticket": ticket,
    }