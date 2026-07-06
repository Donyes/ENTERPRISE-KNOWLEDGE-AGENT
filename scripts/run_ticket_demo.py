from app.tickets.database import SessionLocal, create_tables
from app.tickets.service import (
    create_ticket,
    create_ticket_draft_from_rag,
    list_tickets,
    update_ticket_status,
)


def main():
    create_tables()

    db = SessionLocal()

    try:
        print("Creating a manual ticket...")

        ticket = create_ticket(
            db=db,
            user_question="我的差旅费报销被拒了，帮我提交一个工单。",
            category="finance",
            priority="high",
            summary="用户差旅费报销被拒，需要财务部门协助确认原因。",
            evidence=[],
            status="draft",
        )

        print("\nCreated ticket:")
        print(ticket.id, ticket.summary, ticket.status)

        print("\nListing tickets:")
        tickets = list_tickets(db=db)

        for item in tickets:
            print(item.id, item.category, item.priority, item.status, item.summary)

        print("\nUpdating ticket status:")
        updated_ticket = update_ticket_status(
            db=db,
            ticket_id=ticket.id,
            status="submitted",
        )

        if updated_ticket:
            print(updated_ticket.id, updated_ticket.status)

        print("\nCreating ticket draft from RAG unanswered question:")
        rag_ticket_result = create_ticket_draft_from_rag(
            db=db,
            question="公司有没有免费午餐？",
        )

        print(rag_ticket_result["created"])
        print(rag_ticket_result["reason"])

        if rag_ticket_result["ticket"]:
            generated_ticket = rag_ticket_result["ticket"]
            print(
                generated_ticket.id,
                generated_ticket.category,
                generated_ticket.priority,
                generated_ticket.status,
                generated_ticket.summary,
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()