from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.tickets.database import Base


class TicketStatus:
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    SUBMITTED = "submitted"
    RESOLVED = "resolved"
    REJECTED = "rejected"

    ALL = {
        DRAFT,
        PENDING_REVIEW,
        SUBMITTED,
        RESOLVED,
        REJECTED,
    }


class TicketPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    ALL = {
        LOW,
        MEDIUM,
        HIGH,
        URGENT,
    }


class TicketCategory:
    HR = "hr"
    FINANCE = "finance"
    IT = "it"
    GENERAL = "general"

    ALL = {
        HR,
        FINANCE,
        IT,
        GENERAL,
    }


class Ticket(Base):
    """
    SQLAlchemy ORM model for enterprise tickets.
    """
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    user_question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TicketCategory.GENERAL,
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TicketPriority.MEDIUM,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evidence: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TicketStatus.DRAFT,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )