from fastapi import APIRouter

from app.workflow.graph import run_ticket_workflow
from app.workflow.nodes import apply_review_decision
from app.workflow.schemas import (
    WorkflowReviewRequest,
    WorkflowReviewResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)

router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
)


@router.post("/run", response_model=WorkflowRunResponse)
def run_workflow_api(request: WorkflowRunRequest):
    result = run_ticket_workflow(
        user_input=request.message,
    )

    return WorkflowRunResponse(
        final_message=result.get("final_message", ""),
        answerable=result.get("answerable"),
        requires_human_review=result.get("requires_human_review", False),
        wants_ticket=result.get("wants_ticket"),
        rag_result=result.get("rag_result"),
        ticket_id=result.get("ticket_id"),
        ticket=result.get("ticket"),
    )


@router.post("/review", response_model=WorkflowReviewResponse)
def review_workflow_ticket_api(request: WorkflowReviewRequest):
    result = apply_review_decision(
        ticket_id=request.ticket_id,
        approved=request.approved,
        reviewer_comment=request.reviewer_comment,
    )

    return WorkflowReviewResponse(
        updated=result["updated"],
        final_message=result["final_message"],
        ticket=result.get("ticket"),
    )