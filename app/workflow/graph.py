from typing import Any

from langgraph.graph import END, START, StateGraph

from app.workflow.nodes import (
    analyze_request_node,
    create_ticket_draft_node,
    generate_final_answer_node,
    route_after_rag,
    run_rag_node,
    wait_for_human_review_node,
)
from app.workflow.state import TicketWorkflowState


def build_ticket_workflow_graph():
    """
    Build the LangGraph workflow for RAG + ticket creation + human review.
    """
    builder = StateGraph(TicketWorkflowState)

    builder.add_node("analyze_request", analyze_request_node)
    builder.add_node("run_rag", run_rag_node)
    builder.add_node("generate_final_answer", generate_final_answer_node)
    builder.add_node("create_ticket_draft", create_ticket_draft_node)
    builder.add_node("wait_for_human_review", wait_for_human_review_node)

    builder.add_edge(START, "analyze_request")
    builder.add_edge("analyze_request", "run_rag")

    builder.add_conditional_edges(
        "run_rag",
        route_after_rag,
        {
            "answer": "generate_final_answer",
            "ticket": "create_ticket_draft",
        },
    )

    builder.add_edge("generate_final_answer", END)
    builder.add_edge("create_ticket_draft", "wait_for_human_review")
    builder.add_edge("wait_for_human_review", END)

    graph = builder.compile()

    return graph


def run_ticket_workflow(user_input: str) -> dict[str, Any]:
    """
    Run the ticket workflow once.
    """
    graph = build_ticket_workflow_graph()

    initial_state: TicketWorkflowState = {
        "user_input": user_input,
    }

    final_state = graph.invoke(initial_state)

    return dict(final_state)